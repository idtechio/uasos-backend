import os
import sqlalchemy
import base64
import json
import time
from enum import Enum
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


def create_hosts_table_mapping():
    table_name = os.environ["HOSTS_TABLE_NAME"]
    meta = MetaData(db)
    tbl = Table(
        table_name,
        meta,
        Column("fnc_ts_registered", VARCHAR(13)),
        Column("fnc_status", VARCHAR),
        Column("fnc_score", INTEGER),
        Column("name", VARCHAR),
        # Column("country", VARCHAR), # FIXME: misleading field name
        Column("phone_num", VARCHAR),
        Column("email", VARCHAR),
        Column("city", VARCHAR),
        Column("children_allowed", VARCHAR),
        Column("pet_allowed", VARCHAR),
        Column("handicapped_allowed", VARCHAR),
        Column("num_people", INTEGER),
        Column("period", INTEGER),
        Column("pietro", INTEGER),
        Column("listing_country", VARCHAR),
        Column("shelter_type", VARCHAR),
        Column("beds", INTEGER),
        Column("acceptable_group_relations", VARCHAR),
        Column("ok_for_pregnant", VARCHAR),
        Column("ok_for_disabilities", VARCHAR),
        Column("ok_for_animals", VARCHAR),
        Column("ok_for_elderly", VARCHAR),
        Column("ok_for_any_nationality", VARCHAR),
        Column("duration_category", VARCHAR),
        Column("transport_included", VARCHAR),
    )

    return tbl


class HostsGuestsStatus(Enum):
    MOD_REJECTED = "045"
    DEFAULT = "055"
    MOD_ACCEPTED = "065"
    FNC_BEING_PROCESSED = "075"
    FNC_MATCHED = "085"
    MATCH_ACCEPTED = "095"


def postgres_insert(db, pubsub_msg):
    tbl = create_hosts_table_mapping()

    VALUE_NOT_PROVIDED = sqlalchemy.null()

    country = pubsub_msg.get("country", VALUE_NOT_PROVIDED)  # FIXME: misleading field name

    ins = tbl.insert().values(
        fnc_ts_registered=f"{int(time.time() * 1000)}",
        fnc_status=HostsGuestsStatus.MOD_ACCEPTED,
        fnc_score=5,
        name=pubsub_msg.get("name", VALUE_NOT_PROVIDED),
        country=country,  # FIXME: misleading field name
        phone_num=pubsub_msg.get("phone_num", VALUE_NOT_PROVIDED),
        email=pubsub_msg.get("email", VALUE_NOT_PROVIDED),
        city=pubsub_msg.get("city", VALUE_NOT_PROVIDED),
        children_allowed=pubsub_msg.get("children_allowed", VALUE_NOT_PROVIDED),
        pet_allowed=pubsub_msg.get("pet_allowed", VALUE_NOT_PROVIDED),
        handicapped_allowed=pubsub_msg.get("handicapped_allowed", VALUE_NOT_PROVIDED),
        num_people=pubsub_msg.get("num_people", VALUE_NOT_PROVIDED),
        period=pubsub_msg.get("period", VALUE_NOT_PROVIDED),
        pietro=pubsub_msg.get("pietro", VALUE_NOT_PROVIDED),
        listing_country=country,  # FIXME: misleading field name
        shelter_type=pubsub_msg.get("shelter_type", VALUE_NOT_PROVIDED),
        beds=pubsub_msg.get("beds", VALUE_NOT_PROVIDED),
        acceptable_group_relations=pubsub_msg.get(
            "acceptable_group_relations", VALUE_NOT_PROVIDED
        ),
        ok_for_pregnant=pubsub_msg.get("ok_for_pregnant", VALUE_NOT_PROVIDED),
        ok_for_disabilities=pubsub_msg.get("ok_for_disabilities", VALUE_NOT_PROVIDED),
        ok_for_animals=pubsub_msg.get("ok_for_animals", VALUE_NOT_PROVIDED),
        ok_for_elderly=pubsub_msg.get("ok_for_elderly", VALUE_NOT_PROVIDED),
        ok_for_any_nationality=pubsub_msg.get(
            "ok_for_any_nationality", VALUE_NOT_PROVIDED
        ),
        duration_category=pubsub_msg.get("duration_category", VALUE_NOT_PROVIDED),
        transport_included=pubsub_msg.get("transport_included", VALUE_NOT_PROVIDED),
    )
    with db.connect() as conn:
        conn.execute(ins)
