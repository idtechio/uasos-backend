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

variable "gcf_sa_name" {
  type        = string
  description = "gcf_sa_name"
}

variable "gcf_target" {
  type        = string
}

variable "gcf_matches_table_name" {
  type        = string
}

variable "gcf_guests_table_name" {
  type        = string
}

variable "gcf_hosts_table_name" {
  type        = string
}

variable "gcf_accounts_table_name" {
  type        = string
}

variable "gcf_memory" {
  type        = number
}

variable "gcf_matches-create_memory" {
  type        = number
}

variable "gcf_timeout" {
  type        = number
}

variable "gcf_hosts-insert_name" {
  description = "gcf_hosts-insert_name"
  type        = string
}

variable "gcf_hosts-insert_pubsub_topic_name" {
  type        = string
  description = "gcf_hosts-insert_pubsub_topic_name"
}

variable "gcf_guests-insert_name" {
  description = "gcf_guests-insert_name"
  type        = string
}

variable "gcf_guests-insert_pubsub_topic_name" {
  type        = string
  description = "gcf_guests-insert_pubsub_topic_name"
}

variable "gcf_matches-change-status_name" {
  description = "gcf_matches-change-status_name"
  type        = string
}

variable "gcf_matches-change-status_pubsub_topic_name" {
  type        = string
  description = "gcf_matches-change-status_pubsub_topic_name"
}


variable "gcf_matches-create_name" {
  description = "gcf_matches-create_name"
  type        = string
}

variable "gcf_matches-create_pubsub_topic_name" {
  type        = string
  description = "gcf_matches-create_pubsub_topic_name"
}

variable "gcf_matches_process_rejections_name" {
  description = "gcf_matches_process_rejections_name"
  type        = string
}

variable "gcf_matches_process_rejections_pubsub_topic_name" {
  type        = string
  description = "gcf_matches_process_rejections_pubsub_topic_name"
}

variable "gcf_matches_process_timeout_name" {
  description = "gcf_matches_process_timeout_name"
  type        = string
}

variable "gcf_matches_process_timeout_pubsub_topic_name" {
  type        = string
  description = "gcf_matches_process_timeout_pubsub_topic_name"
}

variable "gcf_send_notification_email_channel_name" {
  description = "gcf_send_notification_email_channel_name"
  type        = string
}

variable "gcf_send_notification_email_channel_pubsub_topic_name" {
  type        = string
  description = "gcf_send_notification_email_channel_pubsub_topic_name"
}

variable "gcf_send_notification_sms_channel_name" {
  description = "gcf_send_notification_sms_channel_name"
  type        = string
}

variable "gcf_send_notification_sms_channel_pubsub_topic_name" {
  type        = string
  description = "gcf_send_notification_sms_channel_pubsub_topic_name"
}

variable "gcf_matches-create-match-sealed-notifications_name" {
  description = "gcf_matches-create-match-sealed-notifications_name"
  type        = string
}

variable "gcf_matches-create-match-sealed-notifications_pubsub_topic_name" {
  type        = string
  description = "gcf_matches-create-match-sealed-notifications_pubsub_topic_name"
}

variable "gcf_matches-create-offering-notifications_name" {
  description = "gcf_matches-create-offering-notifications_name"
  type        = string
}

variable "gcf_matches-create-offering-notifications_pubsub_topic_name" {
  type        = string
  description = "gcf_matches-create-offering-notifications_pubsub_topic_name"
}

variable "gcf_unsubscribe-user_name" {
  description = "gcf_unsubscribe-user_name"
  type        = string
}

variable "gcf_unsubscribe-user_pubsub_topic_name" {
  type        = string
  description = "gcf_unsubscribe-user_pubsub_topic_name"
}

variable "gcf_remove-users-by-email_name" {
  description = "gcf_remove-users-by-email_name"
  type        = string
}

variable "gcf_remove-users-by-email_pubsub_topic_name" {
  type        = string
  description = "gcf_remove-users-by-email_pubsub_topic_name"
}

variable "gcf_listing-delete_name" {
  description = "gcf_listing-delete_name"
  type        = string
}

variable "gcf_listing-delete_pubsub_topic_name" {
  type        = string
  description = "gcf_listing-delete_pubsub_topic_name"
}

variable "gcf_refresh_beds_stats_name" {
  description = "gcf_refresh_beds_stats_name"
  type        = string
}

variable "gcf_refresh_beds_stats_pubsub_topic_name" {
  type        = string
  description = "gcf_refresh_beds_stats_pubsub_topic_name"
}

variable "gcf_accounts-insert_name" {
  description = "gcf_accounts-insert_name"
  type        = string
}

variable "gcf_accounts-insert_pubsub_topic_name" {
  type        = string
  description = "gcf_accounts-insert_pubsub_topic_name"
}
variable "gcf_accounts-update_name" {
  description = "gcf_accounts-update_name"
  type        = string
}

variable "gcf_accounts-update_pubsub_topic_name" {
  type        = string
  description = "gcf_accounts-update_pubsub_topic_name"
}
variable "gcf_hosts-update_name" {
  description = "gcf_hosts-update_name"
  type        = string
}

variable "gcf_hosts-update_pubsub_topic_name" {
  type        = string
  description = "gcf_hosts-update_pubsub_topic_name"
}
variable "gcf_guests-update_name" {
  description = "gcf_guests-update_name"
  type        = string
}

variable "gcf_guests-update_pubsub_topic_name" {
  type        = string
  description = "gcf_guests-update_pubsub_topic_name"
}
