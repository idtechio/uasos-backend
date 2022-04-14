import os
import sqlalchemy
import base64
import json
import time

from enum import Enum

from sqlalchemy import create_engine
from sqlalchemy import Table
from sqlalchemy import MetaData
from sqlalchemy import Column
from sqlalchemy import or_
from sqlalchemy.dialects.postgresql import *

from google.cloud import secretmanager
from dotenv import load_dotenv


# region configuration context
def query_configuration_context(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    secret_name = (
        f'projects/{os.environ["PROJECT_ID"]}/secrets/{secret_id}/versions/latest'
    )
    response = client.access_secret_version(request={"name": secret_name})
    secret_value = response.payload.data.decode("UTF-8")
    configuration_context = json.loads(secret_value)
    return configuration_context


# Load local .env if not on GCP
running_locally = bool(os.getenv("LOCAL_DEVELOPMENT"))
if not running_locally:
    configuration_context = query_configuration_context(
        os.environ["SECRET_CONFIGURATION_CONTEXT"]
    )
else:
    print(f"Running locally")
    load_dotenv()
# endregion


# region database connectivity
def create_db_engine():
    db_config = {
        "drivername": "postgresql+pg8000",
    }
    if not running_locally:
        db_connection_name = os.environ["DB_CONNECTION_NAME"]
        db_config |= {
            "query": dict(
                {"unix_sock": f"/cloudsql/{db_connection_name}/.s.PGSQL.5432"}
            ),
            "database": configuration_context["DB_NAME"],
            "username": configuration_context["DB_USER"],
            "password": configuration_context["DB_PASS"],
        }
    else:
        db_config |= {
            "host": os.environ["DB_HOST"],
            "port": os.environ["DB_PORT"],
            "database": os.environ["DB_NAME"],
            "username": os.environ["DB_USER"],
            "password": os.environ["DB_PASS"],
        }
    pool = create_engine(
        sqlalchemy.engine.url.URL.create(**db_config),
    )
    pool.dialect.description_encoding = None
    return pool


db = create_db_engine()
# endregion


# region Enum definitions
class MatchesStatus(Enum):
    DEFAULT = "055"
    FNC_AWAITING_RESPONSE = "065"
    MATCH_ACCEPTED = "075"
    MATCH_REJECTED = "045"
    MATCH_TIMEOUT = "035"


class HostsGuestsStatus(Enum):
    MOD_REJECTED = "045"
    DEFAULT = "055"
    MOD_ACCEPTED = "065"
    FNC_BEING_PROCESSED = "075"
    FNC_MATCHED = "085"
    MATCH_ACCEPTED = "095"


# endregion


# region Database data models
def create_table_mapping(db_pool, db_table_name):
    meta = MetaData(db_pool)
    tbl = Table(db_table_name, meta, autoload=True, autoload_with=db_pool)

    return tbl
# endregion


# region utility functions
def check_expired_in_hours(str_epoch, timeout_hours):
    now = int(time.time() * 1000)

    int_epoch = int(str_epoch)

    delta = now - int_epoch
    delta_in_hours = int(delta / 1000 / 3600)

    return delta_in_hours > int(timeout_hours)
# endregion


# region integration utilities
def fnc_target(event, context):
    if not running_locally:
        pubsub_msg = json.loads(base64.b64decode(event["data"]).decode("utf-8"))
    else:
        pubsub_msg = json.loads(event["data"])

    postgres_process_timeout(pubsub_msg)
# endregion


# region data mutation services
def postgres_process_timeout(pubsub_msg):
    tbl_matches = create_table_mapping(db_pool=db, db_table_name=os.environ["MATCHES_TABLE_NAME"])
    tbl_guests = create_table_mapping(db_pool=db, db_table_name=os.environ["GUESTS_TABLE_NAME"])
    tbl_hosts = create_table_mapping(db_pool=db, db_table_name=os.environ["HOSTS_TABLE_NAME"])

    sel_matches = (
        tbl_matches.select()
        .where(
            or_(
                tbl_matches.c.fnc_host_status == MatchesStatus.FNC_AWAITING_RESPONSE,
                tbl_matches.c.fnc_guest_status == MatchesStatus.FNC_AWAITING_RESPONSE,
            )
        )
        .where(tbl_matches.c.fnc_status == MatchesStatus.FNC_AWAITING_RESPONSE)
    )

    print("Timeout value: ", int(configuration_context["MATCH_TIMEOUT_HOURS"]))
    with db.connect() as conn:
        with conn.begin():
            result = conn.execute(sel_matches)

            for row in result:
                print(f"processing MATCH {row['db_matches_id']}")

                if check_expired_in_hours(
                    row["db_ts_matched"], configuration_context["MATCH_TIMEOUT_HOURS"]
                ):
                    change_matches_status = (
                        tbl_matches.update()
                        .where(tbl_matches.c.db_matches_id == row["db_matches_id"])
                        .values(fnc_status=MatchesStatus.MATCH_TIMEOUT)
                    )
                    conn.execute(change_matches_status)

                    change_hosts_status = (
                        tbl_hosts.update()
                        .where(tbl_hosts.c.db_hosts_id == row["fnc_hosts_id"])
                        .values(fnc_status=HostsGuestsStatus.MOD_ACCEPTED)
                    )
                    conn.execute(change_hosts_status)

                    change_guests_status = (
                        tbl_guests.update()
                        .where(tbl_guests.c.db_guests_id == row["fnc_guests_id"])
                        .values(fnc_status=HostsGuestsStatus.MOD_ACCEPTED)
                    )
                    conn.execute(change_guests_status)

# endregion

# This is end of file. Testing (1)