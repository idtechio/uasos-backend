import os
import sqlalchemy
import base64
import json
import time
from enum import Enum
from sqlalchemy import create_engine, Table, MetaData, Column, or_
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


# region utility functions
def nvl(dct):
    return {k: sqlalchemy.null() if not v else v for k, v in dct.items()}


def lowercase_stripped(value):
    result = value

    if result:
        result = result.strip()
        result = result.lower()

    return result
# endregion


# region Enum definitions
class HostsGuestsStatus(Enum):
    FNC_INACTIVE = "015"
    FNC_DISABLED = "025"
    MOD_REJECTED = "045"
    DEFAULT = "055"
    MOD_ACCEPTED = "065"
    FNC_BEING_PROCESSED = "075"
    FNC_MATCHED = "085"
    MATCH_ACCEPTED = "095"
# endregion


# region Database data models
def create_table_mapping(db_pool, table_name):
    meta = MetaData(db_pool)
    tbl = Table(table_name, meta, autoload=True, autoload_with=db_pool)

    return tbl
# endregion


# region integration utilities
def fnc_target(event, context):
    if not running_locally:
        pubsub_msg = json.loads(base64.b64decode(event["data"]).decode("utf-8"))
    else:
        pubsub_msg = json.loads(event["data"])
    postgres_renew(db, pubsub_msg)
# endregion


# region data mutation services
def postgres_renew(db_pool, pubsub_msg):
    table_name = os.environ["GUESTS_TABLE_NAME"]
    tbl_guests = create_table_mapping(db_pool=db_pool, table_name=table_name)

    if 'db_guests_id' not in pubsub_msg.keys():
        raise ValueError(f'key value "db_guests_id" is missing for RENEW (UPDATE) in "{pubsub_msg}"')

    db_guests_id = pubsub_msg["db_guests_id"]

    stmt = (
        tbl_guests.update()
        .where(tbl_guests.c.db_guests_id == db_guests_id)
        .where(
            or_(
                tbl_guests.c.fnc_status == HostsGuestsStatus.FNC_INACTIVE,
                tbl_guests.c.fnc_status == HostsGuestsStatus.FNC_DISABLED,
            )
        )
        .values(fnc_status=HostsGuestsStatus.MOD_ACCEPTED)
        .returning(tbl_guests.c.db_guests_id)
    )

    with db.connect() as conn:
        with conn.begin():
            result = conn.execute(stmt)

            processed_rows = 0
            for idx, row in enumerate(result):
                print(f'renewed listing for db_guests_id={db_guests_id}')
                processed_rows = idx + 1

            if processed_rows == 0:
                raise ValueError(
                    f'given db_guests_id={db_guests_id} is not in FNC_INACTIVE state for RENEW (UPDATE) in "{pubsub_msg}"')
# endregion
