import os
import sqlalchemy
import base64
import json
from enum import Enum
from sqlalchemy import create_engine, Table, MetaData, Column, or_, exists, and_
from sqlalchemy.dialects.postgresql import VARCHAR

from google.cloud import pubsub_v1
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
class ListingType(Enum):
    GUEST = "guest"
    HOST = "host"


# endregion


# region integration utilities
def fnc_publish_message(message):
    topic_name = os.environ["LISTING_DELETE_TOPIC"]
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
    if not running_locally:
        pubsub_msg = json.loads(base64.b64decode(event["data"]).decode("utf-8"))
    else:
        pubsub_msg = json.loads(event["data"])

    if listing_exists(pubsub_msg):
        fnc_publish_message({"user_id": pubsub_msg["listing_id"], "is_host": is_host})
    else:
        raise ValueError(f'Provided listing "{pubsub_msg}" does not exist')


# region Main function
def listing_exists(pubsub_msg):
    global is_host
    predefined_listing_types = [listing_type.value for listing_type in ListingType]
    
    if pubsub_msg["listing_type"] not in predefined_listing_types:
        raise RuntimeError(f'Provided message "{pubsub_msg}" does not contain a predefined "listing_type"')

    if pubsub_msg["listing_type"] == ListingType.HOST.value:
        is_host = 1
        tbl = create_hosts_table_mapping()

        stmt = (
                tbl.select()
                .where(
                        and_(
                            tbl.c.db_hosts_id == pubsub_msg["listing_id"],
                            tbl.c.email == pubsub_msg["listing_email"],
                        )
                )
            )
    elif pubsub_msg["listing_type"] == ListingType.GUEST.value:
        is_host = 0
        tbl = create_guests_table_mapping()

        stmt = (
                tbl.select()
                .where(
                        and_(
                            tbl.c.db_guests_id == pubsub_msg["listing_id"],
                            tbl.c.email == pubsub_msg["listing_email"],
                        )
                )
            )

    with db.connect() as conn:
        with conn.begin():
            result = bool(conn.execute(stmt).scalar())
    
    
    return result


# endregion
