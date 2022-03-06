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


def query_status(input_payload):
	return {
		True: MatchesStatus.MATCH_ACCEPTED,
		False: MatchesStatus.MATCH_REJECTED
	}.get(input_payload['accepted'], MatchesStatus.DEFAULT)


def create_matches_table_mapping():
	meta = MetaData(db)
	tbl = Table('matches', meta,
				Column('db_matches_id', VARCHAR),
				Column('fnc_host_status', VARCHAR),
				Column('fnc_guest_status', VARCHAR),
				Column('fnc_status', VARCHAR)
				)

	return tbl


def change_host_status(matches_id, target_status):
	tbl = create_matches_table_mapping()

	upd = (
		tbl.update()
			.where(tbl.c.db_matches_id==matches_id)
			.where(tbl.c.fnc_status==MatchesStatus.FNC_AWAITING_RESPONSE)
			.values(fnc_h_status=target_status)
	)

	with db.connect() as conn:
		conn.execute(upd)


def change_guest_status(matches_id, target_status):
	tbl = create_matches_table_mapping()

	upd = (
		tbl.update()
			.where(tbl.c.db_matches_id==matches_id)
			.where(tbl.c.fnc_status==MatchesStatus.FNC_AWAITING_RESPONSE)
			.values(fnc_g_status=target_status)
	)

	with db.connect() as conn:
		conn.execute(upd)


def fnc_target(event, context):
	if not running_locally:
		pubsub_msg = json.loads(base64.b64decode(event['data']).decode('utf-8'))
	else:
		pubsub_msg = json.loads(event['data'])

	if not 'is_host' in pubsub_msg or pubsub_msg['is_host'] == None:
		raise RuntimeError('message is missing required field "is_host"!')

	postgres_change_status(pubsub_msg)


def postgres_change_status(pubsub_msg):
	matches_id = pubsub_msg['matches_id']

	target_status = query_status(pubsub_msg)

	if not pubsub_msg['is_host']:
		change_host_status(matches_id, target_status)
	else:
		change_guest_status(matches_id, target_status)
