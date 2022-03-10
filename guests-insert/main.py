import os
import sqlalchemy
import base64
import json
import time
from sqlalchemy import create_engine, Table, MetaData, Column, inspect
from sqlalchemy.dialects.postgresql import *

from google.cloud import secretmanager


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


def fnc_target(event, context):
    if not running_locally:
        pubsub_msg = json.loads(base64.b64decode(event["data"]).decode("utf-8"))
    else:
        pubsub_msg = json.loads(event["data"])
    postgres_insert(db, pubsub_msg)


def create_guests_table_mapping():
    table_name = os.environ["GUESTS_TABLE_NAME"]
    meta = MetaData(db)
    tbl = Table(
        table_name,
        meta,
        Column("fnc_ts_registered", VARCHAR(13)),
        Column("fnc_status", VARCHAR),
        Column("fnc_score", INTEGER),
        Column("name", VARCHAR),
        Column("country", VARCHAR),
        Column("phone_num", VARCHAR),
        Column("email", VARCHAR),
        Column("city", VARCHAR),
        Column("is_children", VARCHAR),
        Column("is_pet", VARCHAR),
        Column("is_handicapped", VARCHAR),
        Column("num_people", INTEGER),
        Column("period", INTEGER),
        Column("listing_country", VARCHAR),
        Column("acceptable_shelter_types", VARCHAR),
        Column("beds", INTEGER),
        Column("group_relation", VARCHAR),
        Column("is_pregnant", VARCHAR),
        Column("is_with_disability", VARCHAR),
        Column("is_with_animal", VARCHAR),
        Column("is_with_elderly", VARCHAR),
        Column("is_ukrainian_nationality", VARCHAR),
        Column("duration_category", VARCHAR),
    )

    return tbl


def postgres_insert(db, pubsub_msg):
    tbl = create_guests_table_mapping()

    VALUE_NOT_PROVIDED = sqlalchemy.null()

    ins = tbl.insert().values(
        fnc_ts_registered=f"{int(time.time() * 1000)}",
        fnc_status=os.environ["GUEST_INITIAL_STATUS"],
        fnc_score=5,
        name=pubsub_msg.get("name", VALUE_NOT_PROVIDED),
        country=pubsub_msg.get("country", VALUE_NOT_PROVIDED),
        phone_num=pubsub_msg.get("phone_num", VALUE_NOT_PROVIDED),
        email=pubsub_msg.get("email", VALUE_NOT_PROVIDED),
        city=pubsub_msg.get("city", VALUE_NOT_PROVIDED),
        is_children=pubsub_msg.get("is_children", VALUE_NOT_PROVIDED),
        is_pet=pubsub_msg.get("is_pet", VALUE_NOT_PROVIDED),
        is_handicapped=pubsub_msg.get("is_handicapped", VALUE_NOT_PROVIDED),
        num_people=pubsub_msg.get("num_people", VALUE_NOT_PROVIDED),
        period=pubsub_msg.get("period", VALUE_NOT_PROVIDED),
        listing_country=pubsub_msg.get("listing_country", VALUE_NOT_PROVIDED),
        acceptable_shelter_types=pubsub_msg.get(
            "acceptable_shelter_types", VALUE_NOT_PROVIDED
        ),
        beds=pubsub_msg.get("beds", VALUE_NOT_PROVIDED),
        group_relation=pubsub_msg.get("group_relation", VALUE_NOT_PROVIDED),
        is_pregnant=pubsub_msg.get("is_pregnant", VALUE_NOT_PROVIDED),
        is_with_disability=pubsub_msg.get("is_with_disability", VALUE_NOT_PROVIDED),
        is_with_animal=pubsub_msg.get("is_with_animal", VALUE_NOT_PROVIDED),
        is_with_elderly=pubsub_msg.get("is_with_elderly", VALUE_NOT_PROVIDED),
        is_ukrainian_nationality=pubsub_msg.get(
            "is_ukrainian_nationality", VALUE_NOT_PROVIDED
        ),
        duration_category=pubsub_msg.get("duration_category", VALUE_NOT_PROVIDED),
    )
    with db.connect() as conn:
        conn.execute(ins)
