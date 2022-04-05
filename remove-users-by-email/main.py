import os
import sqlalchemy
import json
from enum import Enum
from sqlalchemy import create_engine, Table, MetaData, Column, any_
from sqlalchemy.dialects.postgresql import VARCHAR

from google.cloud import secretmanager
from dotenv import load_dotenv
from google.cloud import pubsub_v1


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
        Column("country", VARCHAR),
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
        Column("db_ts_registered", VARCHAR),
        Column("city", VARCHAR),
        Column("country", VARCHAR),
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

# region integration utilities


def fnc_publish_message(message):
    topic_name = os.environ["UNSUBSCRIBE_USER_TOPIC"]
    topic_path = publisher.topic_path(os.environ["PROJECT_ID"], topic_name)

    message_json = json.dumps(message)
    message_bytes = message_json.encode("utf-8")

    try:
        publish_future = publisher.publish(topic_path, data=message_bytes)
        publish_future.result()  # Verify the publish succeeded
        return "Message published."
    except Exception as e:
        print(e)
        return (e, 500)


# endregion


# Instantiates a Pub/Sub client
publisher = pubsub_v1.PublisherClient()


def fnc_target(event, context):
    # pubsub_msg = json.loads(event["data"])
    emails = event["emails"]
    mod_emails = [f"%{email}%" for email in emails]
    print(mod_emails)
    unsubscribe_hosts(mod_emails)
    unsubscribe_guests(mod_emails)


def unsubscribe_hosts(emails):
    tbl_hosts = create_hosts_table_mapping()

    with db.connect() as conn:
        with conn.begin():
            sel_hosts = tbl_hosts.select().where(tbl_hosts.c.email.ilike(any_(emails)))
            result = conn.execute(sel_hosts)

            for row in result:
                print(f"Unsubscribing {row['name']} with id: {row['db_hosts_id']}")
                fnc_publish_message({"user_id": row["db_hosts_id"], "is_host": "1"})


def unsubscribe_guests(emails):
    tbl_guests = create_guests_table_mapping()

    with db.connect() as conn:
        with conn.begin():
            sel_guests = tbl_guests.select().where(
                tbl_guests.c.email.ilike(any_(emails))
            )
            result = conn.execute(sel_guests)

            for row in result:
                print(f"Unsubscribing {row['name']} with id: {row['db_guests_id']}")
                fnc_publish_message({"user_id": row["db_guests_id"], "is_host": "0"})
