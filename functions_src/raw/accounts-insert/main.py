import os
import sqlalchemy
import base64
import json
import time
from enum import Enum
from sqlalchemy import create_engine, Table, MetaData

from google.cloud import secretmanager


# region configuration context
def query_configuration_context(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    secret_name = (
        f'projects/{os.environ["PROJECT_ID"]}/secrets/{secret_id}/versions/latest'
    )
    response = client.access_secret_version(request={"name": secret_name})
    secret_value = response.payload.data.decode("UTF-8")
    configuration_context = json.loads(secret_value)  # FIXME: shadows the outer scope in purpose
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
def query_epoch_with_milliseconds():
    return int(time.time() * 1000)


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
class AccountsStatus(Enum):
    MOD_REJECTED = "045"
    DEFAULT = "055"
    MOD_ACCEPTED = "065"
# endregion


# region integration utilities
def fnc_target(event, context):
    if not running_locally:
        pubsub_msg = json.loads(base64.b64decode(event["data"]).decode("utf-8"))
    else:
        pubsub_msg = json.loads(event["data"])
    postgres_insert(db_pool=db, pubsub_msg=pubsub_msg)
# endregion


# region Database data models
def create_table_mapping(db_pool, db_table_name):
    meta = MetaData(db_pool)
    tbl = Table(db_table_name, meta, autoload=True, autoload_with=db_pool)

    return tbl
# endregion


# region data mutation services
def postgres_insert(db_pool, pubsub_msg):
    # table_name = 'accounts'
    table_name = os.environ["ACCOUNTS_TABLE_NAME"]

    tbl_accounts = create_table_mapping(db_pool=db_pool, db_table_name=table_name)

    if 'db_accounts_id' in pubsub_msg.keys():
        raise ValueError(f'Key value "db_accounts_id" cannot have value for INSERT in "{pubsub_msg}"')

    pubsub_msg['preferred_lang'] = lowercase_stripped(pubsub_msg['preferred_lang'])
    pubsub_msg['email'] = lowercase_stripped(pubsub_msg['email'])
    payload = nvl(pubsub_msg)

    with db.connect() as conn:
        with conn.begin():
            stmt = tbl_accounts.insert()
            print(f"prepared INSERT statement for table={table_name}")

            conn.execute(stmt.values(**payload))
# endregion
