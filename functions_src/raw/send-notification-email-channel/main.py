import os
import base64
import json
from sendgrid.helpers.mail import Mail
from sendgrid import SendGridAPIClient

from google.cloud import secretmanager
from dotenv import load_dotenv


# Load local .env if not on GCP
running_locally = bool(os.getenv("LOCAL_DEVELOPMENT"))
if running_locally:
	print(f"Running locally")
	load_dotenv()


def query_configuration_context(secret_id):
	client = secretmanager.SecretManagerServiceClient()
	name = f'projects/{os.environ["PROJECT_ID"]}/secrets/{secret_id}/versions/latest'
	response = client.access_secret_version(request={"name": name})

	configuration_context = json.loads(response.payload.data.decode("UTF-8"))
	return configuration_context


configuration_context = query_configuration_context("FUNCTIONS_CONFIGURATION_CONTEXT")


def fnc_target(event, context):
	if not running_locally:
		pubsub_msg = json.loads(base64.b64decode(event['data']).decode('utf-8'))
	else:
		pubsub_msg = json.loads(event['data'])

	send_notification(pubsub_msg)


def send_notification(pubsub_msg):
	from_email = pubsub_msg['from_email']
	template_id = pubsub_msg['template_id']

	to_emails = [(x['email'], x['name']) for x in pubsub_msg['to_emails']]

	message = Mail(
					from_email=from_email,
					to_emails=to_emails)

	message.dynamic_template_data = dict([(x['key'], x['value']) for x in pubsub_msg['context']])

	message.template_id = template_id

	try:
		sg = SendGridAPIClient(configuration_context['SENDGRID_API_KEY'])
		response = sg.send(message)
		code, body, headers = response.status_code, response.body, response.headers
		print(f"Response code: {code}")
		print(f"Response headers: {headers}")
		print(f"Response body: {body}")
		print("Dynamic Messages Sent!")
	except Exception as e:
		print("Error: {0}".format(e))
