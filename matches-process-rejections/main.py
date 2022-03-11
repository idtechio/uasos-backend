import os
import sqlalchemy
import base64
import json

from enum import Enum

from sqlalchemy import create_engine
from sqlalchemy import Table
from sqlalchemy import MetaData
from sqlalchemy import Column
from sqlalchemy import or_
from sqlalchemy.dialects.postgresql import *

from google.cloud import secretmanager
from dotenv import load_dotenv


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


def create_matches_table_mapping():
    table_name = os.environ["MATCHES_TABLE_NAME"]
    meta = MetaData(db)
    tbl = Table(
        table_name,
        meta,
        Column("db_matches_id", VARCHAR),
        Column("fnc_host_status", VARCHAR),
        Column("fnc_guest_status", VARCHAR),
        Column("fnc_status", VARCHAR),
    )

    return tbl


def create_hosts_table_mapping():
    table_name = table_name = os.environ["HOSTS_TABLE_NAME"]
    meta = MetaData(db)
    tbl = Table(
        table_name, meta, Column("db_hosts_id", VARCHAR), Column("fnc_status", VARCHAR)
    )

    return tbl


def create_guests_table_mapping():
    table_name = os.environ["GUESTS_TABLE_NAME"]
    meta = MetaData(db)
    tbl = Table(
        table_name, meta, Column("db_guests_id", VARCHAR), Column("fnc_status", VARCHAR)
    )

    return tbl


class MatchesStatus(Enum):
    DEFAULT = "055"
    FNC_AWAITING_RESPONSE = "065"
    MATCH_ACCEPTED = "075"
    MATCH_REJECTED = "045"


class HostsGuestsStatus(Enum):
    MOD_REJECTED = "045"
    DEFAULT = "055"
    MOD_ACCEPTED = "065"
    FNC_BEING_PROCESSED = "075"
    FNC_MATCHED = "085"
    MATCH_ACCEPTED = "095"


def fnc_target(event, context):
    if not running_locally:
        pubsub_msg = json.loads(base64.b64decode(event["data"]).decode("utf-8"))
    else:
        pubsub_msg = json.loads(event["data"])

    postgres_process_rejection(pubsub_msg)


def postgres_process_rejection(pubsub_msg):
    tbl_matches = create_matches_table_mapping()
    tbl_guests = create_guests_table_mapping()
    tbl_hosts = create_hosts_table_mapping()

    sel_matches = (
        tbl_matches.select()
        .where(
            or_(
                tbl_matches.c.fnc_host_status == MatchesStatus.MATCH_REJECTED,
                tbl_matches.c.fnc_guest_status == MatchesStatus.MATCH_REJECTED,
            )
        )
        .where(tbl_matches.c.fnc_status == MatchesStatus.FNC_AWAITING_RESPONSE)
    )

    with db.connect() as conn:
        with conn.begin():
            result = conn.execute(sel_matches)

            for row in result:
                print(f"processing MATCH {row['db_matches_id']}")
                print(
                    f"setting MATCH {row['db_matches_id']} to {MatchesStatus.MATCH_REJECTED} status"
                )

                change_matches_status = (
                    tbl_matches.update()
                    .where(tbl_matches.c.db_matches_id == row["db_matches_id"])
                    .values(fnc_status=MatchesStatus.MATCH_REJECTED)
                )

                conn.execute(change_matches_status)

                print(
                    f"setting HOST {row['fnc_host_id']} to {HostsGuestsStatus.DEFAULT} status"
                )

                change_hosts_status = (
                    tbl_hosts.update()
                    .where(tbl_hosts.c.db_hosts_id == row["fnc_host_id"])
                    .values(fnc_status=HostsGuestsStatus.DEFAULT)
                )

                conn.execute(change_hosts_status)

                print(
                    f"setting GUEST {row['fnc_guest_id']} to {HostsGuestsStatus.DEFAULT} status"
                )

                change_guests_status = (
                    tbl_guests.update()
                    .where(tbl_guests.c.db_guests_id == row["fnc_guest_id"])
                    .values(fnc_status=HostsGuestsStatus.DEFAULT)
                )

                conn.execute(change_guests_status)
