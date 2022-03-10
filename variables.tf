variable "region" {
  description = "Project resources region"
  type        = string
}

variable "secondary_region" {
  description = "Project resources secondary region"
  type        = string
}

variable "project_id" {
  description = "GCP project id"
  type        = string
}

variable "project_number" {
  type        = string
  description = "Google Cloud Project number where resources should be created"
}

variable "tf_repo_name" {
  type        = string
  description = "Cloud Source Repositories Terraform repository name"
}

variable "network_name" {
  description = "Network name"
  type        = string
}

variable "subnet_name1" {
  description = "Subnetwork name 1"
  type        = string
}

variable "subnet_name2" {
  description = "Subnetwork name 2"
  type        = string
}

variable "subnet_name3" {
  description = "Subnetwork name 3"
  type        = string
}

variable "subnet_name4" {
  description = "Subnetwork name 4"
  type        = string
}

variable "vpc_access_connector_name" {
  description = "vpc_access_connector_name"
  type        = string
}

variable "cloud_sql_instance_name" {
  type        = string
  description = "cloud_sql_instance_name"
}

variable "gcf_secret_configuration_context" {
  type        = string
  description = "gcf_secret_configuration_contexte"
}

variable "gcf_hosts-insert_name" {
  description = "gcf_hosts-insert_name"
  type        = string
}

variable "gcf_hosts-insert_target" {
  type        = string
  description = "gcf_hosts-insert_target"
}

variable "gcf_hosts-insert_folder" {
  type        = string
  description = "gcf_hosts-insert_folder"
}

variable "gcf_hosts-insert_memory" {
  type        = string
  description = "gcf_hosts-insert_memory"
}

variable "gcf_hosts-insert_timeout" {
  type        = number
  description = "gcf_hosts-insert_timeout"
}

variable "gcf_hosts-insert_pubsub_topic_name" {
  type        = string
  description = "gcf_hosts-insert_pubsub_topic_name"
}

variable "gcf_sa_name" {
  type        = string
  description = "gcf_sa_name"
}

variable "gcf_hosts-insert_hosts_table_name" {
  type        = string
  description = "gcf_hosts-insert_hosts_table_name"
}

variable "gcf_hosts-insert_host_initial_status" {
  type        = string
  description = "gcf_hosts-insert_host_initial_status"
}

variable "gcf_guests-insert_name" {
  description = "gcf_guests-insert_name"
  type        = string
}

variable "gcf_guests-insert_target" {
  type        = string
  description = "gcf_guests-insert_target"
}

variable "gcf_guests-insert_folder" {
  type        = string
  description = "gcf_guests-insert_folder"
}

variable "gcf_guests-insert_memory" {
  type        = string
  description = "gcf_guests-insert_memory"
}

variable "gcf_guests-insert_timeout" {
  type        = number
  description = "gcf_guests-insert_timeout"
}

variable "gcf_guests-insert_pubsub_topic_name" {
  type        = string
  description = "gcf_guests-insert_pubsub_topic_name"
}

variable "gcf_guests-insert_guests_table_name" {
  type        = string
  description = "gcf_guests-insert_guests_table_name"
}

variable "gcf_guests-insert_guest_initial_status" {
  type        = string
  description = "gcf_guests-insert_guest_initial_status"
}

variable "gcf_matches-change-status_name" {
  description = "gcf_matches-change-status_name"
  type        = string
}

variable "gcf_matches-change-status_target" {
  type        = string
  description = "gcf_matches-change-status_target"
}

variable "gcf_matches-change-status_folder" {
  type        = string
  description = "gcf_matches-change-status_folder"
}

variable "gcf_matches-change-status_memory" {
  type        = string
  description = "gcf_matches-change-status_memory"
}

variable "gcf_matches-change-status_timeout" {
  type        = number
  description = "gcf_matches-change-status_timeout"
}

variable "gcf_matches-change-status_pubsub_topic_name" {
  type        = string
  description = "gcf_matches-change-status_pubsub_topic_name"
}


variable "gcf_matches-create_name" {
  description = "gcf_matches-create_name"
  type        = string
}

variable "gcf_matches-create_target" {
  type        = string
  description = "gcf_matches-create_target"
}

variable "gcf_matches-create_folder" {
  type        = string
  description = "gcf_matches-create_folder"
}

variable "gcf_matches-create_memory" {
  type        = string
  description = "gcf_matches-create_memory"
}

variable "gcf_matches-create_timeout" {
  type        = number
  description = "gcf_matches-create_timeout"
}

variable "gcf_matches-create_pubsub_topic_name" {
  type        = string
  description = "gcf_matches-create_pubsub_topic_name"
}


variable "gcf_matches-create-notifications_name" {
  description = "gcf_matches-create-notifications_name"
  type        = string
}

variable "gcf_matches-create-notifications_target" {
  type        = string
  description = "gcf_matches-create-notifications_target"
}

variable "gcf_matches-create-notifications_folder" {
  type        = string
  description = "gcf_matches-create-notifications_folder"
}

variable "gcf_matches-create-notifications_memory" {
  type        = string
  description = "gcf_matches-create-notifications_memory"
}

variable "gcf_matches-create-notifications_timeout" {
  type        = number
  description = "gcf_matches-create-notifications_timeout"
}

variable "gcf_matches-create-notifications_pubsub_topic_name" {
  type        = string
  description = "gcf_matches-create-notifications_pubsub_topic_name"
}

variable "gcf_matches_process_rejections_name" {
  description = "gcf_matches_process_rejections_name"
  type        = string
}

variable "gcf_matches_process_rejections_target" {
  type        = string
  description = "gcf_matches_process_rejections_target"
}

variable "gcf_matches_process_rejections_folder" {
  type        = string
  description = "gcf_matches_process_rejections_folder"
}

variable "gcf_matches_process_rejections_memory" {
  type        = string
  description = "gcf_matches_process_rejections_memory"
}

variable "gcf_matches_process_rejections_timeout" {
  type        = number
  description = "gcf_matches_process_rejections_timeout"
}

variable "gcf_matches_process_rejections_pubsub_topic_name" {
  type        = string
  description = "gcf_matches_process_rejections_pubsub_topic_name"
}

variable "gcf_matches_process_timeout_name" {
  description = "gcf_matches_process_timeout_name"
  type        = string
}

variable "gcf_matches_process_timeout_target" {
  type        = string
  description = "gcf_matches_process_timeout_target"
}

variable "gcf_matches_process_timeout_folder" {
  type        = string
  description = "gcf_matches_process_timeout_folder"
}

variable "gcf_matches_process_timeout_memory" {
  type        = string
  description = "gcf_matches_process_timeout_memory"
}

variable "gcf_matches_process_timeout_timeout" {
  type        = number
  description = "gcf_matches_process_timeout_timeout"
}

variable "gcf_matches_process_timeout_pubsub_topic_name" {
  type        = string
  description = "gcf_matches_process_timeout_pubsub_topic_name"
}

variable "gcf_send_notification_email_channel_name" {
  description = "gcf_send_notification_email_channel_name"
  type        = string
}

variable "gcf_send_notification_email_channel_target" {
  type        = string
  description = "gcf_send_notification_email_channel_target"
}

variable "gcf_send_notification_email_channel_folder" {
  type        = string
  description = "gcf_send_notification_email_channel_folder"
}

variable "gcf_send_notification_email_channel_memory" {
  type        = string
  description = "gcf_send_notification_email_channel_memory"
}

variable "gcf_send_notification_email_channel_timeout" {
  type        = number
  description = "gcf_send_notification_email_channel_timeout"
}

variable "gcf_send_notification_email_channel_pubsub_topic_name" {
  type        = string
  description = "gcf_send_notification_email_channel_pubsub_topic_name"
}

variable "gcf_matches-create-match-sealed-notifications_name" {
  description = "gcf_matches-create-match-sealed-notifications_name"
  type        = string
}

variable "gcf_matches-create-match-sealed-notifications_target" {
  type        = string
  description = "gcf_matches-create-match-sealed-notifications_target"
}

variable "gcf_matches-create-match-sealed-notifications_folder" {
  type        = string
  description = "gcf_matches-create-match-sealed-notifications_folder"
}

variable "gcf_matches-create-match-sealed-notifications_memory" {
  type        = string
  description = "gcf_matches-create-match-sealed-notifications_memory"
}

variable "gcf_matches-create-match-sealed-notifications_timeout" {
  type        = number
  description = "gcf_matches-create-match-sealed-notifications_timeout"
}

variable "gcf_matches-create-match-sealed-notifications_pubsub_topic_name" {
  type        = string
  description = "gcf_matches-create-match-sealed-notifications_pubsub_topic_name"
}

variable "gcf_matches-create-offering-notifications_name" {
  description = "gcf_matches-create-offering-notifications_name"
  type        = string
}

variable "gcf_matches-create-offering-notifications_target" {
  type        = string
  description = "gcf_matches-create-offering-notifications_target"
}

variable "gcf_matches-create-offering-notifications_folder" {
  type        = string
  description = "gcf_matches-create-offering-notifications_folder"
}

variable "gcf_matches-create-offering-notifications_memory" {
  type        = string
  description = "gcf_matches-create-offering-notifications_memory"
}

variable "gcf_matches-create-offering-notifications_timeout" {
  type        = number
  description = "gcf_matches-create-offering-notifications_timeout"
}

variable "gcf_matches-create-offering-notifications_pubsub_topic_name" {
  type        = string
  description = "gcf_matches-create-offering-notifications_pubsub_topic_name"
}

variable "gcf_hosts_table_name" {
  type        = string
  description = "gcf_hosts_table_name"
}

variable "gcf_host_initial_status" {
  type        = string
  description = "gcf_host_initial_status"
}

variable "gcf_guests_table_name" {
  type        = string
  description = "gcf_guests_table_name"
}

variable "gcf_guest_initial_status" {
  type        = string
  description = "gcf_guest_initial_status"
}

variable "gcf_matches_table_name" {
  type        = string
  description = "gcf_matches_table_name"
}

variable "gcf_match_initial_status" {
  type        = string
  description = "gcf_match_initial_status"
}
