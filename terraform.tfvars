project_id       = "ukrn-hlpr"
region           = "europe-central2"
secondary_region = "europe-west3"
project_number   = "55609607717"

tf_repo_name = "gcp-infra"

network_name = "private-vpc"
subnet_name1 = "private-subnetwork"
subnet_name2 = "serverless-connector"
subnet_name3 = "private-subnetwork-sec-region"
subnet_name4 = "serverless-connector-sec-region"

vpc_access_connector_name = "eu-central2-serverless"

### Functions-specific

gcf_secret_configuration_context = "FUNCTIONS_CONFIGURATION_CONTEXT"
cloud_sql_instance_name = "sql-hlpr-prd-db"
gcf_sa_name = "gcf-sa"

gcf_matches_table_name = "matches"
gcf_guests_table_name = "guests"
gcf_hosts_table_name = "hosts"

# hosts-insert

gcf_hosts-insert_name = "hosts-insert"
gcf_hosts-insert_target = "fnc_target"
gcf_hosts-insert_folder = "hosts-insert"
gcf_hosts-insert_memory = 1024
gcf_hosts-insert_timeout = 540
gcf_hosts-insert_pubsub_topic_name = "hosts"

gcf_hosts-insert_hosts_table_name = "hosts"
gcf_hosts-insert_host_initial_status = "065"

# guests-insert

gcf_guests-insert_name = "guests-insert"
gcf_guests-insert_target = "fnc_target"
gcf_guests-insert_folder = "guests-insert"
gcf_guests-insert_memory = 1024
gcf_guests-insert_timeout = 540
gcf_guests-insert_pubsub_topic_name = "guests"

gcf_guests-insert_guests_table_name = "guests"
gcf_guests-insert_guest_initial_status = "065"

# matches-change-status

gcf_matches-change-status_name = "matches-change-status" 
gcf_matches-change-status_target = "fnc_target" 
gcf_matches-change-status_folder = "matches-change-status" 
gcf_matches-change-status_memory = 1024 
gcf_matches-change-status_timeout = 540 
gcf_matches-change-status_pubsub_topic_name = "matches_status_changes" 

# gcf_matches-create

gcf_matches-create_name = "matches-create" 
gcf_matches-create_target = "fnc_target" 
gcf_matches-create_folder = "matches-create" 
gcf_matches-create_memory = 1024 
gcf_matches-create_timeout = 540 
gcf_matches-create_pubsub_topic_name = "matches-create" 
gcf_matches-create_matches_initial_status = "055" 

# gcf_matches-create-notifications

gcf_matches-create-notifications_name = "matches-create-notifications" 
gcf_matches-create-notifications_target = "fnc_target" 
gcf_matches-create-notifications_folder = "matches-create-notifications" 
gcf_matches-create-notifications_memory = 1024 
gcf_matches-create-notifications_timeout = 540 
gcf_matches-create-notifications_pubsub_topic_name = "matches-create-notifications" 

gcf_matches_process_rejections_name = "matches_process_rejections"
gcf_matches_process_rejections_target = "fnc_target"
gcf_matches_process_rejections_folder = "matches-process-rejections"
gcf_matches_process_rejections_memory = 1024
gcf_matches_process_rejections_timeout = 540
gcf_matches_process_rejections_pubsub_topic_name = "matches_process_rejections"

gcf_matches_process_timeout_name = "matches_process_timeout"
gcf_matches_process_timeout_target = "fnc_target"
gcf_matches_process_timeout_folder = "matches-process-timeout"
gcf_matches_process_timeout_memory = 1024
gcf_matches_process_timeout_timeout = 540
gcf_matches_process_timeout_pubsub_topic_name = "matches_process_timeout"

gcf_send_notification_email_channel_name = "send_notification_email_channel"
gcf_send_notification_email_channel_target = "fnc_target"
gcf_send_notification_email_channel_folder = "send-notification-email-channel"
gcf_send_notification_email_channel_memory = 1024
gcf_send_notification_email_channel_timeout = 540
gcf_send_notification_email_channel_pubsub_topic_name = "send_notification_email_channel"

gcf_matches-create-match-sealed-notifications_name = "matches-create-match-sealed-notifications"
gcf_matches-create-match-sealed-notifications_target = "fnc_target"
gcf_matches-create-match-sealed-notifications_folder = "matches-create-match-sealed-notifications"
gcf_matches-create-match-sealed-notifications_memory = 1024
gcf_matches-create-match-sealed-notifications_timeout = 540
gcf_matches-create-match-sealed-notifications_pubsub_topic_name = "matches-create-match-sealed-notifications"

gcf_matches-create-offering-notifications_name = "matches-create-offering-notifications"
gcf_matches-create-offering-notifications_target = "fnc_target"
gcf_matches-create-offering-notifications_folder = "matches-create-offering-notifications"
gcf_matches-create-offering-notifications_memory = 1024
gcf_matches-create-offering-notifications_timeout = 540
gcf_matches-create-offering-notifications_pubsub_topic_name = "matches-create-offering-notifications"

gcf_host_initial_status = "065"
gcf_guest_initial_status = "065"
gcf_match_initial_status = "055"