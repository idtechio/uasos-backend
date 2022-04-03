import base64
import json
import os
from enum import Enum

import sqlalchemy
from google.cloud import secretmanager
from sqlalchemy import create_engine, Table, MetaData


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
            "guest": os.environ["DB_HOST"],
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


# region utility functions
def check_guest_listing_exists(guests_id, db_conn):
    tbl_guests = create_table_mapping(db_pool=db, db_table_name=os.environ["GUESTS_TABLE_NAME"])

    stmt = (
        tbl_guests.select().where(tbl_guests.c.db_guests_id == guests_id)
    )

    result = bool(db_conn.execute(stmt).scalar())

    print(f'checking if listing for guest={guests_id} exists={result}')

    return result


def check_guest_match_exists(guests_id, db_conn):
    tbl_matches = create_table_mapping(db_pool=db, db_table_name=os.environ["MATCHES_TABLE_NAME"])

    sel_matches = tbl_matches.select().where(tbl_matches.c.fnc_guests_id == guests_id)
    db_conn.execute(sel_matches)

    result = bool(db_conn.execute(sel_matches).scalar())

    print(f'checking if match for guest={guests_id} exists={result}')

    return result


# endregion


# region Enum definitions
class HostsGuestsStatus(Enum):
    MOD_DELETED = '035'
    MOD_REJECTED = "045"
    DEFAULT = "055"
    MOD_ACCEPTED = "065"
    FNC_BEING_PROCESSED = "075"
    FNC_MATCHED = "085"
    MATCH_ACCEPTED = "095"
    FNC_DELETED = "035"


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

    if 'db_guests_id' not in pubsub_msg:
        raise RuntimeError(f'Provided message "{pubsub_msg}" does not contain expected field "db_guests_id"')

    postgres_update(db, pubsub_msg)


# endregion


# region data mutation services
def change_guest_status(guests_id, db_conn):
    tbl_guests = create_table_mapping(db_pool=db, db_table_name=os.environ["GUESTS_TABLE_NAME"])

    print(f'updating status for guest={guests_id} to={HostsGuestsStatus.MOD_DELETED.value}')

    change_guests_status = (
        tbl_guests.update()
            .where(tbl_guests.c.db_guests_id == guests_id)
            .values(fnc_status=HostsGuestsStatus.MOD_DELETED)
    )

    db_conn.execute(change_guests_status)


def postgres_update(db_pool, pubsub_msg):
    db_guests_id = pubsub_msg["db_guests_id"]

    with db_pool.connect() as conn:
        with conn.begin():
            if check_guest_match_exists(guests_id=db_guests_id, db_conn=conn):
                raise ValueError(f'listing for guest={db_guests_id} is already in marriage')

            if not check_guest_listing_exists(guests_id=db_guests_id, db_conn=conn):
                raise ValueError(f'listing for guest={db_guests_id} does not exist!')

            change_guest_status(guests_id=db_guests_id, db_conn=conn)
# endregion