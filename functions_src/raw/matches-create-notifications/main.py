import os
import sqlalchemy
import base64
import json
import time

from enum import Enum

from sqlalchemy import create_engine
from sqlalchemy import Table
from sqlalchemy import MetaData
from sqlalchemy import Column
from sqlalchemy import or_
from sqlalchemy.dialects.postgresql import *

from google.cloud import pubsub_v1
from google.cloud import secretmanager
from dotenv import load_dotenv

def query_configuration_context(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    secret_name = f'projects/{os.environ["PROJECT_ID"]}/secrets/{secret_id}/versions/latest'
    response = client.access_secret_version(request={"name": secret_name})
    secret_value = response.payload.data.decode("UTF-8")
    configuration_context = json.loads(secret_value)
    return configuration_context


# Load local .env if not on GCP
running_locally = bool(os.getenv("LOCAL_DEVELOPMENT"))
if not running_locally:
    configuration_context = query_configuration_context(os.environ["SECRET_CONFIGURATION_CONTEXT"])
else:
    print(f"Running locally")
    load_dotenv()


def create_db_engine():
    db_config = {
        "drivername": "postgresql+pg8000",
    }
    if not running_locally:
        db_connection_name = os.environ["DB_CONNECTION_NAME"]
        db_config |= {
            "query": dict({"unix_sock": f"/cloudsql/{db_connection_name}/.s.PGSQL.5432"}),
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
        sqlalchemy.engine.url.URL.create(
            **db_config
        ),
    )
    pool.dialect.description_encoding = None
    return pool


db = create_db_engine()


def create_matches_table_mapping():
    table_name = os.environ["MATCHES_TABLE_NAME"]
    meta = MetaData(db)
    tbl = Table(table_name, meta,
                Column('db_matches_id', VARCHAR),
                Column('fnc_ts_matched', VARCHAR),
                Column('fnc_status', VARCHAR)
                )

    return tbl


def create_hosts_table_mapping():
    table_name = table_name = os.environ["HOSTS_TABLE_NAME"]
    meta = MetaData(db)
    tbl = Table(table_name, meta,
                Column('db_hosts_id', VARCHAR),
                Column('name', VARCHAR),
                Column('email', VARCHAR),
                Column('fnc_status', VARCHAR),
                Column('city', VARCHAR),
                Column('children_allowed', VARCHAR),
                Column('pet_allowed', VARCHAR),
                Column('handicapped_allowed', VARCHAR),
                Column('period', INTEGER),
                Column('pietro', INTEGER),
                )

    return tbl


def create_guests_table_mapping():
    table_name = os.environ["GUESTS_TABLE_NAME"]
    meta = MetaData(db)
    tbl = Table(table_name, meta,
                Column('db_guests_id',  VARCHAR),
                Column('fnc_status', VARCHAR)
                )

    return tbl


class MatchesStatus(Enum):
    DEFAULT 			  = '055'
    FNC_AWAITING_RESPONSE = '065'
    MATCH_ACCEPTED 		  = '075'
    MATCH_REJECTED		  = '045'


class HostsGuestsStatus(Enum):
    MOD_REJECTED 		= '045'
    DEFAULT 			= '055'
    MOD_ACCEPTED  		= '065'
    FNC_BEING_PROCESSED = '075'
    FNC_MATCHED 		= '085'
    MATCH_ACCEPTED 		= '095'





def fetch_row(pubsub_msg):
    tbl_matches = create_matches_table_mapping()
    tbl_guests = create_guests_table_mapping()
    tbl_hosts = create_hosts_table_mapping()

    sel_matches = (
        tbl_hosts.select()
            .where(tbl_hosts.c.db_hosts_id == '176')
    )


    with db.connect() as conn:
        with conn.begin():
            result = conn.execute(sel_matches)
            for row in result:
                return dict(row) 
                # dict(row))
                # print(row)
                # dct = row2dict(row)
                # print(dct)
# 






















































# Instantiates a Pub/Sub client
publisher = pubsub_v1.PublisherClient()
PROJECT_ID = 'ukrn-hlpr'
topic_name = 'notification_messages'

template_id = "dummy-template-id"



"""
{
    "from_email": "michal.kolodziejski@gmail.com",
    "context": [
            {"key": "guest.city", "value":"Warszawa"},
            {"key": "host.children_allowed", "value":"true"},
            {"key": "host.handicapped_allowed", "value":"true"},
            {"key": "host.pet_allowed", "value":"true"},
            {"key": "host.pietro", "value":"1"},
            {"key": "host.period", "value":"1"}
    ],
    "template_id": "d-62faf432bc8348e9a7b4dd8a268410a6",
    "to_emails":
    [
        {"email": "michal.kolodziejski@gmail.com", "name": "Michał Kołodziejski"}
    ]
}
"""



























payload = json.loads('''{ "from_email": "michal.kolodziejski@gmail.com", "context": [ {"key": "guest.city", "value":"Warszawa"}, {"key": "host.children_allowed", "value":"true"}, {"key": "host.handicapped_allowed", "value":"true"}, {"key": "host.pet_allowed", "value":"true"}, {"key": "host.pietro", "value":"1"}, {"key": "host.period", "value":"1"} ], "template_id": "d-62faf432bc8348e9a7b4dd8a268410a6", "to_emails": [ {"email": "michal.kolodziejski@gmail.com", "name": "Michał Kołodziejski"} ] }''')

def fnc_target(event, context):
    row = fetch_row(payload)
    print(row)




    topic_path = publisher.topic_path(PROJECT_ID, topic_name)

    message_json = json.dumps(row)
    message_bytes = message_json.encode('utf-8')

    try:
        publish_future = publisher.publish(topic_path, data=message_bytes)
        publish_future.result()  # Verify the publish succeeded
        return 'Message published.'
    except Exception as e:
        print(e)
        return (e, 500)

