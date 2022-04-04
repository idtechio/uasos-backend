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
from sqlalchemy import join
from sqlalchemy import select

import i18n

from google.cloud import pubsub_v1
from google.cloud import secretmanager
from dotenv import load_dotenv


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


# region Database connectivity initialisation
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


# region Database data models
def create_table_mapping(db_pool, db_table_name):
    meta = MetaData(db_pool)
    tbl = Table(db_table_name, meta, autoload=True, autoload_with=db_pool)

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


def fnc_publish_sms(message):
    topic_name = os.environ["SEND_SMS_TOPIC"]
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


def create_sms_payload(phone_num, body):
    return {
        "phone_num": phone_num,
        "body": body
    }

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


def query_acceptance_url(matches_id, accept_value, side):
    template_url = configuration_context["MATCH_ACCEPTANCE_URL_TEMPLATE"]
    return template_url.format(
        matches_id=matches_id, accept_value=accept_value.value, side=side.value
    )


def create_paylod_for_guest_and_host_match_confirm_template(
    matches_id, guest_row, host_row, to_emails, preferred_lang
):

    print(
        f"preparing payload with context for 'GuestAndHostMatchConfirm' SendGrid template, preferred_lang={preferred_lang}"
    )

    # template_id = "d-4b189c34ff584451a1dc1f83421a7d21"
    template_id = i18n.t("sendgrid.GUESTANDHOSTMATCHCONFIRM", locale=preferred_lang)

    context = {
        "host_name": host_row["name"],
        "host_phone": host_row["phone_num"],
        "host_email": host_row["email"],
        "guest_name": guest_row["name"],
        "guest_phone": guest_row["phone_num"],
        "guest_email": guest_row["email"],
    }

    return create_email_payload(
        template_id=template_id, context=context, to_emails=to_emails
    )


# endregion

# Instantiates a Pub/Sub client
publisher = pubsub_v1.PublisherClient()


def fnc_target(event, context):
    create_offering_notifications()

# endregion


# region Main function
def create_offering_notifications():
    tbl_matches = create_table_mapping(db_pool=db, db_table_name=os.environ["MATCHES_TABLE_NAME"])
    tbl_guests = create_table_mapping(db_pool=db, db_table_name=os.environ["GUESTS_TABLE_NAME"])
    tbl_hosts = create_table_mapping(db_pool=db, db_table_name=os.environ["HOSTS_TABLE_NAME"])
    tbl_accounts = create_table_mapping(db_pool=db, db_table_name=os.environ["ACCOUNTS_TABLE_NAME"])

    sel_matches = (
        tbl_matches.select()
        .where(tbl_matches.c.fnc_status == MatchesStatus.FNC_AWAITING_RESPONSE)
        .where(tbl_matches.c.fnc_host_status == MatchesStatus.MATCH_ACCEPTED)
        .where(tbl_matches.c.fnc_guest_status == MatchesStatus.MATCH_ACCEPTED)
    )

    with db.connect() as conn:
        with conn.begin():
            result = conn.execute(sel_matches)

            for match in result:
                # guests_join_accounts = join(tbl_guests, tbl_accounts, tbl_guests.c.fnc_accounts_id == tbl_accounts.c.db_accounts_id)
                # sel_guests2 = select(tbl_guests, tbl_accounts).select_from(guests_join_accounts).where(
                #     tbl_guests.c.db_guests_id == match["fnc_guests_id"]
                # ) #FIXME
                sel_guests = sqlalchemy.text(
                    f"SELECT gue.db_guests_id, gue.db_ts_registered, gue.fnc_accounts_id, gue.fnc_status, gue.country, gue.city, gue.acceptable_shelter_types, gue.beds, gue.group_relation, gue.is_pregnant, gue.is_with_disability, gue.is_with_animal, gue.is_with_elderly, gue.is_ukrainian_nationality, duration_category, coalesce(acc.phone_num, gue.phone_num) as phone_num, coalesce(acc.email, gue.email) as email, coalesce(acc.name, gue.name) as name, coalesce(acc.preferred_lang, 'uk') as preferred_lang FROM guests gue LEFT JOIN accounts acc ON gue.fnc_accounts_id = acc.db_accounts_id WHERE gue.db_guests_id = '{match['fnc_guests_id']}';"
                )
                guest_rows = conn.execute(sel_guests)

                # hosts_join_accounts = join(tbl_hosts, tbl_accounts, tbl_hosts.c.fnc_accounts_id == tbl_accounts.c.db_accounts_id)
                # sel_hosts = select(tbl_hosts, tbl_accounts).select_from(hosts_join_accounts).where(
                #     tbl_guests.c.db_guests_id == match["fnc_hosts_id"]
                # )
                sel_hosts = sqlalchemy.text(
                    f"SELECT hos.db_hosts_id, hos.db_ts_registered, hos.fnc_accounts_id, hos.fnc_status, hos.country, hos.city, hos.closest_city, hos.zipcode, hos.street, hos.building_no, hos.appartment_no, hos.shelter_type, hos.beds, hos.acceptable_group_relations, hos.ok_for_pregnant, hos.ok_for_disabilities, hos.ok_for_animals, hos.ok_for_elderly, hos.ok_for_any_nationality, hos.duration_category, hos.transport_included, can_be_verified, coalesce(acc.phone_num, hos.phone_num) as phone_num, coalesce(acc.email, hos.email) as email, coalesce(acc.name, hos.name) as name, coalesce(acc.preferred_lang, 'pl') as preferred_lang FROM hosts hos LEFT JOIN accounts acc ON hos.fnc_accounts_id = acc.db_accounts_id WHERE hos.db_hosts_id = '{match['fnc_hosts_id']}';"
                )
                host_rows = conn.execute(sel_hosts)

                for host_row in host_rows:
                    for guest_row in guest_rows:
                        message_for_host = (
                            create_paylod_for_guest_and_host_match_confirm_template(
                                matches_id=match["db_matches_id"],
                                guest_row=guest_row,
                                host_row=host_row,
                                to_emails=create_to_email_element(
                                    host_row["name"], host_row["email"]
                                ),
                                preferred_lang=host_row['preferred_lang']
                            )
                        )
                        message_for_guest = (
                            create_paylod_for_guest_and_host_match_confirm_template(
                                matches_id=match["db_matches_id"],
                                guest_row=guest_row,
                                host_row=host_row,
                                to_emails=create_to_email_element(
                                    guest_row["name"], guest_row["email"]
                                ),
                                preferred_lang=guest_row['preferred_lang']
                            )
                        )
                        print(message_for_host)
                        print(message_for_guest)
                        fnc_publish_message(message_for_host)
                        fnc_publish_sms(
                            create_sms_payload(phone_num=host_row["phone_num"],
                                               body=i18n.t("messaging.sms.sealedNotification", locale=host_row['preferred_lang'])
                                               )
                        )
                        fnc_publish_message(message_for_guest)
                        fnc_publish_sms(
                            create_sms_payload(phone_num=guest_row["phone_num"],
                                               body=i18n.t("messaging.sms.sealedNotification", locale=guest_row['preferred_lang'])
                                               )
                        )

                upd_matches_status = (
                    tbl_matches.update()
                    .where(tbl_matches.c.db_matches_id == match["db_matches_id"])
                    .values(
                        fnc_status=MatchesStatus.MATCH_ACCEPTED,
                        fnc_host_status=MatchesStatus.MATCH_ACCEPTED,
                        fnc_guest_status=MatchesStatus.MATCH_ACCEPTED,
                    )
                )

                conn.execute(upd_matches_status)


# endregion
