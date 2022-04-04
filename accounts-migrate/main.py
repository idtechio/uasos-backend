import os
import sqlalchemy
import base64
import json
import time
from enum import Enum
from sqlalchemy import create_engine, Table, MetaData, Column, or_, exists, and_

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
# endregion


# region Enum definitions
class AccountsStatus(Enum):
    MOD_TO_MIGRATE = "035"
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

    accounts_migrate(db_pool=db, pubsub_msg=pubsub_msg)
# endregion


# region Database data models
def create_table_mapping(db_pool, db_table_name):
    meta = MetaData(db_pool)
    tbl = Table(db_table_name, meta, autoload=True, autoload_with=db_pool)

    return tbl
# endregion


# region data mutation services
def update_hosts_with_accounts(db_pool):
    print(f"migrating hosts listings")

    # tbl_name_accounts = 'accounts'
    tbl_name_accounts = os.environ["ACCOUNTS_TABLE_NAME"]
    tbl_accounts = create_table_mapping(db_pool=db_pool, db_table_name=tbl_name_accounts)

    # tbl_name_hosts = 'hosts'
    tbl_name_hosts = os.environ["HOSTS_TABLE_NAME"]
    tbl_hosts = create_table_mapping(db_pool=db_pool, db_table_name=tbl_name_hosts)

    sel_accounts = (
        tbl_accounts.select().where(tbl_accounts.c.fnc_status == AccountsStatus.MOD_TO_MIGRATE)
    )

    with db.connect() as conn:
        with conn.begin():
            accounts = conn.execute(sel_accounts)

            for account in accounts:
                # find hosts with fnc_accounts_id=NULL and with email and phone_num matching accounts.email and accounts.phone_num
                sel_hosts_for_account = (
                    tbl_hosts.select()
                    .where(
                        and_(
                            tbl_hosts.c.fnc_accounts_id == sqlalchemy.null(),
                            tbl_hosts.c.email == account['email'],
                            # tbl_hosts.c.phone_num == account['phone_num'],
                        )
                    )
                )

                hosts_listings_for_account = conn.execute(sel_hosts_for_account)

                for host in hosts_listings_for_account:
                    upd_hosts = (
                        tbl_hosts.update()
                            .where(tbl_hosts.c.db_hosts_id == host['db_hosts_id'])
                            .values(fnc_accounts_id=account['db_accounts_id'], fnc_status=AccountsStatus.MOD_ACCEPTED)
                    )

                    hosts_update_result = conn.execute(upd_hosts)

                    print(f"assigned db_account_id={account['db_accounts_id']} host={host['db_hosts_id']} with result={hosts_update_result}")


def update_guests_with_accounts(db_pool):
    print(f"migrating guests")

    # tbl_name_accounts = 'accounts'
    tbl_name_accounts = os.environ["ACCOUNTS_TABLE_NAME"]
    tbl_accounts = create_table_mapping(db_pool=db_pool, db_table_name=tbl_name_accounts)

    # tbl_name_guests = 'guests'
    tbl_name_guests = os.environ["GUESTS_TABLE_NAME"]
    tbl_guests = create_table_mapping(db_pool=db_pool, db_table_name=tbl_name_guests)

    sel_accounts = (
        tbl_accounts.select().where(tbl_accounts.c.fnc_status == AccountsStatus.MOD_TO_MIGRATE)
    )

    with db.connect() as conn:
        with conn.begin():
            accounts = conn.execute(sel_accounts)

            for account in accounts:
                # find guests with fnc_accounts_id=NULL and with email and phone_num matching accounts.email and accounts.phone_num
                sel_guests_for_account = (
                    tbl_guests.select().where(
                        and_(
                            tbl_guests.c.fnc_accounts_id == sqlalchemy.null(),
                            tbl_guests.c.email == account['email'],
                            # tbl_guests.c.phone_num == account['phone_num'],
                        )
                    )
                )

                guests_listings_for_account = conn.execute(sel_guests_for_account)

                for guest in guests_listings_for_account:
                    upd_guests = (
                        tbl_guests.update()
                            .where(tbl_guests.c.db_guests_id == guest['db_guests_id'])
                            .values(fnc_accounts_id=account['db_accounts_id'], fnc_status=AccountsStatus.MOD_ACCEPTED)
                    )

                    guests_update_result = conn.execute(upd_guests)

                    print(f"assigned db_account_id={account['db_accounts_id']} guest={guest['db_guests_id']} with result={guests_update_result}")


def accounts_migrate(db_pool, pubsub_msg):
    update_hosts_with_accounts(db_pool=db_pool)
    update_guests_with_accounts(db_pool=db_pool)

# endregion
