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
def check_host_listing_exists(hosts_id, db_conn):
    tbl_hosts = create_table_mapping(db_pool=db, db_table_name=os.environ["HOSTS_TABLE_NAME"])

    stmt = (
        tbl_hosts.select().where(tbl_hosts.c.db_hosts_id == hosts_id)
    )

    result = bool(db_conn.execute(stmt).scalar())

    print(f'checking if listing for host={hosts_id} exists={result}')

    return result


def check_host_match_exists(hosts_id, db_conn):
    tbl_matches = create_table_mapping(db_pool=db, db_table_name=os.environ["MATCHES_TABLE_NAME"])

    sel_matches = (
        tbl_matches.select()
            .where(tbl_matches.c.fnc_hosts_id == hosts_id)
    )
    db_conn.execute(sel_matches)

    result = bool(db_conn.execute(sel_matches).scalar())

    print(f'checking if match for host={hosts_id} exists={result}')

    return result


def check_host_match_in_status_exists(hosts_id, db_conn, status=None):
    tbl_matches = create_table_mapping(db_pool=db, db_table_name=os.environ["MATCHES_TABLE_NAME"])

    sel_matches = (
        tbl_matches.select()
            .where(tbl_matches.c.fnc_guests_id == hosts_id)
            .where(tbl_matches.c.fnc_status == status)
    )

    result = bool(db_conn.execute(sel_matches).scalar())

    print(f'checking if match for guest={hosts_id} exists={result}')

    return result
# endregion


# region Enum definitions
class MatchesStatus(Enum):
    DEFAULT = "055"
    FNC_AWAITING_RESPONSE = "065"
    MATCH_ACCEPTED = "075"
    MATCH_REJECTED = "045"
    MATCH_TIMEOUT = "035"


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

    if 'db_hosts_id' not in pubsub_msg:
        raise RuntimeError(f'Provided message "{pubsub_msg}" does not contain expected field "db_hosts_id"')

    postgres_update(db, pubsub_msg)


# endregion


# region data mutation services
def change_guests_status(db_guests_id, target_status, db_conn):
    tbl_guests_name = os.environ["GUESTS_TABLE_NAME"]
    # tbl_guests_name = "guests"
    tbl_guests = create_table_mapping(db_pool=db, db_table_name=tbl_guests_name)

    change_guests_status = (
        tbl_guests.update()
            .where(tbl_guests.c.db_guests_id == db_guests_id)
            .values(fnc_status=target_status)
    )

    result = db_conn.execute(change_guests_status)

    print(f"changed status of db_guests_id={db_guests_id} to fnc_status={target_status} with result={result}")


def change_hosts_status(db_hosts_id, target_status, db_conn):
    tbl_hosts_name = os.environ["HOSTS_TABLE_NAME"]
    # tbl_hosts_name = "hosts"
    tbl_hosts = create_table_mapping(db_pool=db, db_table_name=tbl_hosts_name)

    change_hosts_status = (
        tbl_hosts.update()
            .where(tbl_hosts.c.db_hosts_id == db_hosts_id)
            .values(fnc_status=target_status)
    )

    result = db_conn.execute(change_hosts_status)

    print(f"changed status of db_hosts_id={db_hosts_id} to fnc_status={target_status} with result={result}")


def change_matches_status(db_matches_id, target_status, db_conn):
    tbl_matches_name = os.environ["MATCHES_TABLE_NAME"]
    # tbl_matches_name = "matches"
    tbl_matches = create_table_mapping(db_pool=db, db_table_name=tbl_matches_name)

    change_matches_status = (
        tbl_matches.update()
            .where(tbl_matches.c.db_matches_id == db_matches_id)
            .values(fnc_status=target_status)
    )

    result = db_conn.execute(change_matches_status)

    print(f"changed status of db_matches_id={db_matches_id} to fnc_status={target_status} with result={result}")


# endregion


# region main function
def postgres_update(db_pool, pubsub_msg):
    db_hosts_id = pubsub_msg["db_hosts_id"]

    with db_pool.connect() as conn:
        with conn.begin():
            # check if listing exists
            if not check_host_listing_exists(hosts_id=db_hosts_id, db_conn=conn):
                raise ValueError(f'listing for db_hosts_id={db_hosts_id} does not exist!')

            # check if match in status MATCH_ACCEPTED exists for this guest
            if check_host_match_in_status_exists(hosts_id=db_hosts_id, db_conn=conn,
                                                 status=MatchesStatus.MATCH_ACCEPTED):
                raise ValueError(
                    f'listing for db_hosts_id={db_hosts_id} is already part of MATCH in status={MatchesStatus.MATCH_ACCEPTED}')

            # soft-delete guest
            change_hosts_status(db_hosts_id=db_hosts_id,
                                target_status=HostsGuestsStatus.MOD_DELETED,
                                db_conn=conn)

            # check if match exists to split (is not in MATCH_ACCEPTED status)
            if check_host_match_exists(hosts_id=db_hosts_id, db_conn=conn):
                # check if match exists to split (is not in MATCH_ACCEPTED status)
                if 'db_matches_id' in pubsub_msg:
                    db_matches_id = pubsub_msg["db_matches_id"]
                    print(f'host db_host_id={db_hosts_id} is in MATCH that can be split db_matches_id={db_matches_id}')

                    # select a match
                    tbl_matches = create_table_mapping(db_pool=db, db_table_name=os.environ["MATCHES_TABLE_NAME"])
                    sel_matches = tbl_matches.select().where(tbl_matches.c.db_matches_id == db_matches_id)
                    result = conn.execute(sel_matches)

                    for match_row in result:
                        db_guests_id = match_row['fnc_guests_id']
                        print(f'splitting db_matches_id={db_matches_id} for db_guest_id={db_guests_id} and db_host_id={db_hosts_id} - initiated by host')

                        change_guests_status(db_guests_id=db_guests_id,
                                             target_status=HostsGuestsStatus.MOD_ACCEPTED,
                                             db_conn=conn)
                        change_hosts_status(db_hosts_id=db_hosts_id,
                                            target_status=HostsGuestsStatus.MOD_DELETED,
                                            db_conn=conn)
                        change_matches_status(db_matches_id=db_matches_id,
                                              target_status=MatchesStatus.MATCH_REJECTED,
                                              db_conn=conn)
# endregion
