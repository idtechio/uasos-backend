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


def filter_table_mapping(tbl):
    columns_to_filter = [col for col in tbl._columns if col.name.lower().startswith('db_')]
    for col in columns_to_filter:
        tbl._columns.remove(col)
    return tbl


def add_missing_fields_in_payload(pubsub_msg, tbl):
    column_names = {c.name for c in tbl.columns}
    empty_dict = dict.fromkeys(column_names, None)
    valid_dict = empty_dict | {k: pubsub_msg[k] for k in pubsub_msg if k in empty_dict}
    payload = nvl(valid_dict)

    return payload
# endregion


# region integration utilities
def fnc_target(event, context):
    if not running_locally:
        pubsub_msg = json.loads(base64.b64decode(event["data"]).decode("utf-8"))
    else:
        pubsub_msg = json.loads(event["data"])
    postgres_insert(db, pubsub_msg)
# endregion


# region data mutation services
def postgres_insert(db_pool, pubsub_msg):
    table_name = os.environ["GUESTS_TABLE_NAME"]
    tbl_guests_raw = create_table_mapping(db_pool=db_pool, table_name=table_name)
    tbl_guests = filter_table_mapping(tbl_guests_raw)

    if 'db_guests_id' in pubsub_msg.keys():
        raise ValueError(f'Key value "db_guests_id" cannot have value for INSERT in "{pubsub_msg}"')

    if 'email' in pubsub_msg.keys():
        pubsub_msg['email'] = lowercase_stripped(pubsub_msg['email'])
        
    pubsub_msg['fnc_status'] = HostsGuestsStatus.MOD_ACCEPTED

    payload = add_missing_fields_in_payload(pubsub_msg, tbl_guests)

    stmt = tbl_guests.insert()

    with db.connect() as conn:
        with conn.begin():
            conn.execute(stmt.values(**payload))
# endregion
