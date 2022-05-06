import os
import sqlalchemy
import base64
import json
import time

from enum import Enum

import i18n

from sqlalchemy import create_engine
from sqlalchemy import Table
from sqlalchemy import MetaData
from sqlalchemy import Column
from sqlalchemy import or_
from sqlalchemy.dialects.postgresql import *

from google.cloud import secretmanager
from dotenv import load_dotenv
from google.cloud import pubsub_v1


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


# region i18n initialisation
TRANSLATIONS_FILE_PATH = './locale'

i18n.set('fallback', 'en')
i18n.set('filename_format', '{locale}.{format}')
i18n.set('skip_locale_root_data', True)
i18n.load_path.append(TRANSLATIONS_FILE_PATH)

print(f'i18n initialised - configuration={i18n.load_path}')
# endregion


# region Enum definitions
class MatchesStatus(Enum):
    DEFAULT = "055"
    FNC_AWAITING_RESPONSE = "065"
    MATCH_ACCEPTED = "075"
    MATCH_REJECTED = "045"
    MATCH_TIMEOUT = "035"


class HostsGuestsStatus(Enum):
    FNC_INACTIVE = "015"
    MOD_REJECTED = "045"
    DEFAULT = "055"
    MOD_ACCEPTED = "065"
    FNC_BEING_PROCESSED = "075"
    FNC_MATCHED = "085"
    MATCH_ACCEPTED = "095"


# endregion


# region Database data models
def create_table_mapping(db_pool, db_table_name):
    meta = MetaData(db_pool)
    tbl = Table(db_table_name, meta, autoload=True, autoload_with=db_pool)

    return tbl
# endregion


# region Email message creation utilities
def create_to_email_element(name, email):
    return {"email": email.strip(), "name": name}


def create_email_payload(template_id, context, to_emails):
    return {
        "from_email": configuration_context["SENDGRID_VERIFIED_SENDER_EMAIL"],
        "context": context,
        "template_id": template_id,
        "to_emails": to_emails,
    }


def create_payload_for_match_timeout_template(
    row, to_emails, preferred_lang
):

    print(
        f"preparing payload with context for 'MatchTimeout' SendGrid template, preferred_lang={preferred_lang}"
    )

    # template_id = "d-4b189c34ff584451a1dc1f83421a7d21"
    template_id = i18n.t("sendgrid.MatchTimeout", locale=preferred_lang)

    context = {
        "name": row["name"],
        "phone": row["phone_num"],
        "email": row["email"],
    }

    return create_email_payload(
        template_id=template_id, context=context, to_emails=to_emails
    )
# endregion


# region utility functions
def check_expired_in_hours(str_epoch, timeout_hours):
    now = int(time.time() * 1000)

    int_epoch = int(str_epoch)

    delta = now - int_epoch
    delta_in_hours = int(delta / 1000 / 3600)

    return delta_in_hours > int(timeout_hours)
# endregion


# region integration utilities

# Instantiates a Pub/Sub client
publisher = pubsub_v1.PublisherClient()


def fnc_target(event, context):
    if not running_locally:
        pubsub_msg = json.loads(base64.b64decode(event["data"]).decode("utf-8"))
    else:
        pubsub_msg = json.loads(event["data"])

    postgres_process_timeout(pubsub_msg)
# endregion


# region integration utilities
def fnc_publish_message(message):
    topic_name = os.environ["SEND_EMAIL_TOPIC"]
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


def postgres_process_timeout(pubsub_msg):
    tbl_matches = create_table_mapping(db_pool=db, db_table_name=os.environ["MATCHES_TABLE_NAME"])
    tbl_guests = create_table_mapping(db_pool=db, db_table_name=os.environ["GUESTS_TABLE_NAME"])
    tbl_hosts = create_table_mapping(db_pool=db, db_table_name=os.environ["HOSTS_TABLE_NAME"])

    sel_matches = (
        tbl_matches.select()
        .where(
            or_(
                tbl_matches.c.fnc_host_status == MatchesStatus.FNC_AWAITING_RESPONSE,
                tbl_matches.c.fnc_guest_status == MatchesStatus.FNC_AWAITING_RESPONSE,
            )
        )
        .where(tbl_matches.c.fnc_status == MatchesStatus.FNC_AWAITING_RESPONSE)
    )

    print("Timeout value: ", int(configuration_context["MATCH_TIMEOUT_HOURS"]))
    with db.connect() as conn:
        with conn.begin():
            result = conn.execute(sel_matches)

            for row in result:
                print(f"processing MATCH {row}")

                if check_expired_in_hours(
                    row["db_ts_matched"], configuration_context["MATCH_TIMEOUT_HOURS"]
                ):
                    change_matches_status(db_matches_id=row["db_matches_id"],
                                          target_status=MatchesStatus.MATCH_REJECTED,
                                          db_conn=conn)

                    if row['fnc_host_status'] != MatchesStatus.FNC_AWAITING_RESPONSE.value:
                        change_hosts_status(db_hosts_id=row["fnc_hosts_id"],
                                            target_status=HostsGuestsStatus.MOD_ACCEPTED,
                                            db_conn=conn)
                    else:
                        sel_hosts = sqlalchemy.text(
                            f"SELECT hos.db_hosts_id, hos.db_ts_registered, hos.fnc_accounts_id, hos.fnc_status, hos.country, hos.city, hos.closest_city, hos.zipcode, hos.street, hos.building_no, hos.appartment_no, hos.shelter_type, hos.beds, hos.acceptable_group_relations, hos.ok_for_pregnant, hos.ok_for_disabilities, hos.ok_for_animals, hos.ok_for_elderly, hos.ok_for_any_nationality, hos.duration_category, hos.transport_included, can_be_verified, coalesce(acc.phone_num, hos.phone_num) as phone_num, coalesce(acc.email, hos.email) as email, coalesce(acc.name, hos.name) as name, coalesce(acc.preferred_lang, 'pl') as preferred_lang, coalesce(acc.sms_notification, 'FALSE') as sms_notification FROM hosts hos LEFT JOIN accounts acc ON hos.fnc_accounts_id = acc.db_accounts_id WHERE hos.db_hosts_id = '{row['fnc_hosts_id']}';"
                        )
                        result = conn.execute(sel_hosts)
                        for host_row in result:
                            message_for_host = (
                                create_payload_for_match_timeout_template(
                                    row=host_row, # FIXME clean up
                                    to_emails=create_to_email_element(
                                        host_row["name"], host_row["email"]
                                    ),
                                    preferred_lang=host_row['preferred_lang']
                                )
                            )
                            print(message_for_host)
                            fnc_publish_message(message_for_host)
                            change_hosts_status(db_hosts_id=row["fnc_hosts_id"],
                                                target_status=HostsGuestsStatus.FNC_INACTIVE,
                                                db_conn=conn)

                    if row['fnc_guest_status'] != MatchesStatus.FNC_AWAITING_RESPONSE.value:
                        change_guests_status(db_guests_id=row["fnc_guests_id"],
                                             target_status=HostsGuestsStatus.MOD_ACCEPTED,
                                             db_conn=conn)
                    else:
                        sel_guests = sqlalchemy.text(
                            f"SELECT gue.db_guests_id, gue.db_ts_registered, gue.fnc_accounts_id, gue.fnc_status, gue.country, gue.city, gue.acceptable_shelter_types, gue.beds, gue.group_relation, gue.is_pregnant, gue.is_with_disability, gue.is_with_animal, gue.is_with_elderly, gue.is_ukrainian_nationality, duration_category, coalesce(acc.phone_num, gue.phone_num) as phone_num, coalesce(acc.email, gue.email) as email, coalesce(acc.name, gue.name) as name, coalesce(acc.preferred_lang, 'uk') as preferred_lang, coalesce(acc.sms_notification, 'FALSE') as sms_notification FROM guests gue LEFT JOIN accounts acc ON gue.fnc_accounts_id = acc.db_accounts_id WHERE gue.db_guests_id = '{row['fnc_guests_id']}';"
                        )
                        result = conn.execute(sel_guests)

                        for guest_row in result:
                            message_for_guest = (
                                create_payload_for_match_timeout_template(
                                    row=guest_row,
                                    to_emails=create_to_email_element(
                                        guest_row["name"], guest_row["email"]
                                    ),
                                    preferred_lang=guest_row['preferred_lang']
                                )
                            )

                            print(message_for_guest)
                            fnc_publish_message(message_for_guest)
                            change_guests_status(db_guests_id=row["fnc_guests_id"],
                                                 target_status=HostsGuestsStatus.FNC_INACTIVE,
                                                 db_conn=conn)

# endregion

# This is end of file. Testing (3)