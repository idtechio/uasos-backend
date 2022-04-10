import os
import sqlalchemy
import base64
import json
import time
from enum import Enum
from sqlalchemy import create_engine, Table, MetaData, Column, inspect
from sqlalchemy.dialects.postgresql import *

from google.cloud import secretmanager


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
    from dotenv import load_dotenv

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
    MATCH_TIMEOUT = "035"
    MATCH_REJECTED = "045"
    DEFAULT = "055"
    FNC_AWAITING_RESPONSE = "065"
    MATCH_ACCEPTED = "075"


class HostsGuestsStatus(Enum):
    FNC_DISABLED = "025"
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


# region integration utilities
def fnc_target(event, context):
    if not running_locally:
        pubsub_msg = json.loads(base64.b64decode(event["data"]).decode("utf-8"))
    else:
        pubsub_msg = json.loads(event["data"])

    if "db_matches_id" not in pubsub_msg or pubsub_msg["db_matches_id"] is None:
        raise RuntimeError('message is missing required field "db_matches_id"!')

    postgres_split_match(pubsub_msg)


# endregion


# region data mutation services
def guests_change_status(guests_to_return, target_status, conn):
    tbl_guests_name = os.environ["GUESTS_TABLE_NAME"]
    # tbl_guests_name = "guests"
    tbl_guests = create_table_mapping(db_pool=db, db_table_name=tbl_guests_name)

    for db_guests_id in guests_to_return:
        change_guests_status = (
            tbl_guests.update()
                .where(tbl_guests.c.db_guests_id == db_guests_id)
                .values(fnc_status=target_status)
        )

        result = conn.execute(change_guests_status)

        print(f"changed status of db_guests_id={db_guests_id} to fnc_status={target_status} with result={result}")


def hosts_change_status(hosts_to_disable, target_status, conn):
    tbl_hosts_name = os.environ["HOSTS_TABLE_NAME"]
    # tbl_hosts_name = "hosts"
    tbl_hosts = create_table_mapping(db_pool=db, db_table_name=tbl_hosts_name)

    for db_hosts_id in hosts_to_disable:
        change_hosts_status = (
            tbl_hosts.update()
                .where(tbl_hosts.c.db_hosts_id == db_hosts_id)
                .values(fnc_status=target_status)
        )

        result = conn.execute(change_hosts_status)

        print(f"changed status of db_hosts_id={db_hosts_id} to fnc_status={target_status} with result={result}")


def matches_change_status(db_matches_id, target_status, conn):
    tbl_matches_name = os.environ["MATCHES_TABLE_NAME"]
    # tbl_matches_name = "matches"
    tbl_matches = create_table_mapping(db_pool=db, db_table_name=tbl_matches_name)

    change_matches_status = (
        tbl_matches.update()
            .where(tbl_matches.c.db_matches_id == db_matches_id)
            .values(fnc_status=target_status)
    )

    result = conn.execute(change_matches_status)

    print(f"changed status of db_matches_id={db_matches_id} to fnc_status={target_status} with result={result}")


# endregion


# region Main function
def postgres_split_match(pubsub_msg):
    db_matches_id = pubsub_msg["db_matches_id"]

    print(f"processing MATCH {db_matches_id}")

    with db.connect() as conn:
        with conn.begin():
            matches_change_status(db_matches_id, MatchesStatus.MATCH_REJECTED, conn)
            if "guests_to_disable" in pubsub_msg:
                guests_change_status(pubsub_msg["guests_to_disable"], HostsGuestsStatus.FNC_DISABLED, conn)
            if "hosts_to_disable" in pubsub_msg:
                hosts_change_status(pubsub_msg["hosts_to_disable"], HostsGuestsStatus.FNC_DISABLED, conn)
            if "guests_to_return" in pubsub_msg:
                guests_change_status(pubsub_msg["guests_to_return"], HostsGuestsStatus.MOD_ACCEPTED, conn)
            if "hosts_to_return" in pubsub_msg:
                hosts_change_status(pubsub_msg["hosts_to_return"], HostsGuestsStatus.MOD_ACCEPTED, conn)
# endregion
