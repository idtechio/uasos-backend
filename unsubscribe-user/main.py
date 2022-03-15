import os
import sqlalchemy
import base64
import json
from enum import Enum
from sqlalchemy import create_engine, Table, MetaData, Column, or_
from sqlalchemy.dialects.postgresql import VARCHAR

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
    print("Running locally")
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


# region Database data models
def create_matches_table_mapping():
    table_name = os.environ["MATCHES_TABLE_NAME"]
    # table_name = 'matches'
    meta = MetaData(db)
    tbl = Table(
        table_name,
        meta,
        Column("db_matches_id", VARCHAR),
        Column("fnc_ts_matched", VARCHAR),
        Column("fnc_status", VARCHAR),
        Column("fnc_hosts_id", VARCHAR),
        Column("fnc_guests_id", VARCHAR),
        Column("fnc_host_status", VARCHAR),
        Column("fnc_guest_status", VARCHAR),
    )

    return tbl


def create_guests_table_mapping():
    table_name = os.environ["GUESTS_TABLE_NAME"]
    # table_name = 'guests'
    meta = MetaData(db)
    tbl = Table(
        table_name,
        meta,
        Column("db_guests_id", VARCHAR),
        Column("name", VARCHAR),
        Column("city", VARCHAR),
        Column("fnc_status", VARCHAR),
        Column("listing_country", VARCHAR),
        Column("acceptable_shelter_types", VARCHAR),
        Column("beds", VARCHAR),
        Column("group_relation", VARCHAR),
        Column("is_pregnant", VARCHAR),
        Column("is_with_disability", VARCHAR),
        Column("is_with_animal", VARCHAR),
        Column("is_with_elderly", VARCHAR),
        Column("is_ukrainian_nationality", VARCHAR),
        Column("duration_category", VARCHAR),
        Column("email", VARCHAR),
        Column("phone_num", VARCHAR),
    )

    return tbl


def create_hosts_table_mapping():
    table_name = os.environ["HOSTS_TABLE_NAME"]
    # table_name = 'hosts'
    meta = MetaData(db)
    tbl = Table(
        table_name,
        meta,
        Column("db_hosts_id", VARCHAR),
        Column("name", VARCHAR),
        Column("fnc_status", VARCHAR),
        Column("fnc_ts_registered", VARCHAR),
        Column("city", VARCHAR),
        Column("listing_country", VARCHAR),
        Column("shelter_type", VARCHAR),
        Column("beds", VARCHAR),
        Column("acceptable_group_relations", VARCHAR),
        Column("ok_for_pregnant", VARCHAR),
        Column("ok_for_disabilities", VARCHAR),
        Column("ok_for_animals", VARCHAR),
        Column("ok_for_elderly", VARCHAR),
        Column("ok_for_any_nationality", VARCHAR),
        Column("duration_category", VARCHAR),
        Column("email", VARCHAR),
        Column("phone_num", VARCHAR),
        Column("transport_included", VARCHAR),
    )

    return tbl


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


class MatchAcceptanceDecision(Enum):
    ACCEPTED = "1"
    REJECTED = "0"


class MatchAcceptanceSide(Enum):
    GUEST = "guest"
    HOST = "host"


# endregion


# region Database mutation functions
def change_match_status(db_connection, db_matches_id, target_status):
    tbl = create_matches_table_mapping()

    upd = (
        tbl.update()
        .where(tbl.c.db_matches_id == db_matches_id)
        .values(fnc_status=target_status)
    )

    db_connection.execute(upd)


def change_host_status(db_connection, db_hosts_id, target_status):
    tbl = create_hosts_table_mapping()

    upd = (
        tbl.update()
        .where(tbl.c.db_hosts_id == db_hosts_id)
        .values(fnc_status=target_status)
    )

    db_connection.execute(upd)


def change_guest_status(db_connection, db_guests_id, target_status):
    tbl = create_guests_table_mapping()

    upd = (
        tbl.update()
        .where(tbl.c.db_guests_id == db_guests_id)
        .values(fnc_status=target_status)
    )

    db_connection.execute(upd)


# endregion

# region Unsubscribing functions


def unsubscribe_host(host_id):
    with db.connect() as conn:
        with conn.begin():
            # 1. Take host out of queue, matched status set to not undo if he is in
            # "marriage", otherwise record will be deleted
            change_host_status(conn, host_id, HostsGuestsStatus.FNC_MATCHED)

            # 2. Get all user matches, rejected and timeout status is excluded as those
            # dont need to be moved back to queue
            tbl_matches = create_matches_table_mapping()
            sel_matches = (
                tbl_matches.select()
                .where(tbl_matches.c.fnc_hosts_id == host_id)
                .where(
                    or_(
                        tbl_matches.c.fnc_status == MatchesStatus.MATCH_ACCEPTED,
                        tbl_matches.c.fnc_status == MatchesStatus.FNC_AWAITING_RESPONSE,
                        tbl_matches.c.fnc_status == MatchesStatus.DEFAULT,
                    )
                )
            )
            result = conn.execute(sel_matches)

            guests_ids_to_free = []
            for row in result:
                if row["fnc_status"] == MatchesStatus.MATCH_ACCEPTED.value:
                    # if in marriage raise and quite
                    raise ValueError(f"Host with id {host_id} is already in marriage.")
                guests_ids_to_free.append(row["fnc_guests_id"])

            # 3. Reject all pending matches
            upd_matches = (
                tbl_matches.update()
                .where(tbl_matches.c.fnc_hosts_id == host_id)
                .where(
                    or_(
                        tbl_matches.c.fnc_status == MatchesStatus.MATCH_ACCEPTED,
                        tbl_matches.c.fnc_status == MatchesStatus.FNC_AWAITING_RESPONSE,
                        tbl_matches.c.fnc_status == MatchesStatus.DEFAULT,
                    )
                )
                .values(fnc_status=MatchesStatus.MATCH_REJECTED)
            )
            conn.execute(upd_matches)

            # 4. Free all guests back to queue
            for guest_id in guests_ids_to_free:
                change_guest_status(conn, guest_id, HostsGuestsStatus.MOD_ACCEPTED)

            # 5. Remove host from database
            tbl_hosts = create_hosts_table_mapping()
            dlt_host = tbl_hosts.delete().where(tbl_hosts.c.db_hosts_id == host_id)
            conn.execute(dlt_host)


def unsubscribe_guest(guest_id):
    with db.connect() as conn:
        with conn.begin():
            # 1. Take guest out of queue, matched status set, not to undo if he is in
            # "marriage", otherwise record will be deleted
            change_guest_status(conn, guest_id, HostsGuestsStatus.FNC_MATCHED)

            # 2. Get all user matches, rejected and timeout status is excluded as those
            # dont need to be moved back to queue
            tbl_matches = create_matches_table_mapping()
            sel_matches = (
                tbl_matches.select()
                .where(tbl_matches.c.fnc_guests_id == guest_id)
                .where(
                    or_(
                        tbl_matches.c.fnc_status == MatchesStatus.MATCH_ACCEPTED,
                        tbl_matches.c.fnc_status == MatchesStatus.FNC_AWAITING_RESPONSE,
                        tbl_matches.c.fnc_status == MatchesStatus.DEFAULT,
                    )
                )
            )
            result = conn.execute(sel_matches)

            hosts_ids_to_free = []
            for row in result:
                if row["fnc_status"] == MatchesStatus.MATCH_ACCEPTED.value:
                    # if in marriage raise and quite
                    raise ValueError(
                        f"Guest with id {guest_id} is already in marriage."
                    )
                hosts_ids_to_free.append(row["fnc_hosts_id"])

            # 3. Reject all pending matches
            upd_matches = (
                tbl_matches.update()
                .where(tbl_matches.c.fnc_guests_id == guest_id)
                .where(
                    or_(
                        tbl_matches.c.fnc_status == MatchesStatus.MATCH_ACCEPTED,
                        tbl_matches.c.fnc_status == MatchesStatus.FNC_AWAITING_RESPONSE,
                        tbl_matches.c.fnc_status == MatchesStatus.DEFAULT,
                    )
                )
                .values(fnc_status=MatchesStatus.MATCH_REJECTED)
            )
            conn.execute(upd_matches)

            # 4. Free all hosts back to queue
            for host_id in hosts_ids_to_free:
                change_host_status(conn, host_id, HostsGuestsStatus.MOD_ACCEPTED)

            # 5. Remove host from database
            tbl_guests = create_guests_table_mapping()
            dlt_guest = tbl_guests.delete().where(tbl_guests.c.db_guests_id == guest_id)
            conn.execute(dlt_guest)


# endregion


def fnc_target(event, context):
    if not running_locally:
        pubsub_msg = json.loads(base64.b64decode(event["data"]).decode("utf-8"))
    else:
        pubsub_msg = json.loads(event["data"])

    unsubscribe_user(pubsub_msg)


def unsubscribe_user(pubsub_msg):
    user_id = pubsub_msg["user_id"]
    is_host = bool(int(pubsub_msg["is_host"]))
    print(f"Deleting {'Host' if is_host else 'Guest'} with id: {user_id}")
    if is_host:
        unsubscribe_host(user_id)
    else:
        unsubscribe_guest(user_id)
