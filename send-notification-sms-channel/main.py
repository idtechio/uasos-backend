import base64
import json
import os
from enum import Enum

from dotenv import load_dotenv
from google.cloud import secretmanager
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client as TwilioClient

# Load local .env if not on GCP
running_locally = bool(os.getenv("LOCAL_DEVELOPMENT"))
if running_locally:
    print(f"Running locally")
    load_dotenv()


class Language(Enum):
    PL = "pl"
    UA = "us"


def query_configuration_context(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f'projects/{os.environ["PROJECT_ID"]}/secrets/{secret_id}/versions/latest'
    response = client.access_secret_version(request={"name": name})

    configuration_context = json.loads(response.payload.data.decode("UTF-8"))
    return configuration_context


configuration_context = query_configuration_context("FUNCTIONS_CONFIGURATION_CONTEXT")


def fnc_target(event, context):
    print(event)
    if not running_locally:
        pubsub_msg = json.loads(base64.b64decode(event["data"]).decode("utf-8"))
    else:
        pubsub_msg = json.loads(event["data"])

    send_notification(pubsub_msg)


def send_notification(pubsub_msg):
    to_phone_number = pubsub_msg["phone_num"]
    language = pubsub_msg["language"]

    body = ""
    if language == Language.PL.value:
        body = "We have a contact for you! Check your email and confirm." # FIXME Use proper enum/message pair
    elif language == Language.UA.value:
        body = "У нас є для Вас контакт! Перевірте імейл (спам) та дайте відповідь"

    try:
        client = TwilioClient(
            configuration_context["TWILIO_ACC_SID"],
            configuration_context["TWILIO_AUTH_TOKEN"],
        )
        client.messages.create(
            to=to_phone_number, from_=configuration_context["TWILIO_FROM"], body=body
        )
        print(f"SMS sent to {to_phone_number}")
    except TwilioRestException as err:
        print("Error: {0}".format(err))
