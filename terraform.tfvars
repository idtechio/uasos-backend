project_id       = "ukrn-hlpr-dev"
region           = "europe-central2"
secondary_region = "europe-west3"
project_number   = "727398461288"

tf_repo_name = "uasos-dev-infra"

network_name = "private-vpc"
subnet_name1 = "private-subnetwork"
subnet_name2 = "serverless-connector"
subnet_name3 = "private-subnetwork-sec-region"
subnet_name4 = "serverless-connector-sec-region"

vpc_access_connector_name = "eu-central2-serverless"

### Functions-specific

gcf_secret_configuration_context = "FUNCTIONS_CONFIGURATION_CONTEXT"
cloud_sql_instance_name = "sql-ukr-helper-dev"
gcf_sa_name = "gcf-sa"
gcf_target = "fnc_target"

gcf_matches_table_name = "matches"
gcf_guests_table_name = "guests"
gcf_hosts_table_name = "hosts"

gcf_memory = 1024
gcf_matches-create_memory = 4096
gcf_timeout = 540

# Functions

gcf_hosts-insert_name = "hosts-insert"
gcf_hosts-insert_pubsub_topic_name = "hosts"

gcf_guests-insert_name = "guests-insert"
gcf_guests-insert_pubsub_topic_name = "guests"

gcf_matches-change-status_name = "matches-change-status" 
gcf_matches-change-status_pubsub_topic_name = "matches_status_changes" 

gcf_matches-create_name = "matches-create" 
gcf_matches-create_pubsub_topic_name = "matches-create" 

gcf_matches_process_rejections_name = "matches-process-rejections"
gcf_matches_process_rejections_pubsub_topic_name = "matches_process_rejections"

gcf_matches_process_timeout_name = "matches-process-timeout"
gcf_matches_process_timeout_pubsub_topic_name = "matches_process_timeout"

gcf_send_notification_email_channel_name = "send-notification-email-channel"
gcf_send_notification_email_channel_pubsub_topic_name = "email"

gcf_send_notification_sms_channel_name = "send-notification-sms-channel"
gcf_send_notification_sms_channel_pubsub_topic_name = "sms"

gcf_matches-create-match-sealed-notifications_name = "matches-create-match-sealed-notifications"
gcf_matches-create-match-sealed-notifications_pubsub_topic_name = "matches-create-match-sealed-notifications"

gcf_matches-create-offering-notifications_name = "matches-create-offering-notifications"
gcf_matches-create-offering-notifications_pubsub_topic_name = "matches-create-offering-notifications"

gcf_unsubscribe-user_name = "unsubscribe-user"
gcf_unsubscribe-user_pubsub_topic_name = "unsubscribe-user"

gcf_remove-users-by-email_name = "remove-users-by-email"
gcf_remove-users-by-email_pubsub_topic_name = "remove-users-by-email"

gcf_listing-delete_name = "listing-delete"
gcf_listing-delete_pubsub_topic_name = "listing-delete"
