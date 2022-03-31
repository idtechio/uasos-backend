module "gcf_sa" {
  source     = "terraform-google-modules/service-accounts/google"
  version    = "4.0.3"
  project_id = "${var.project_id}"
  names = [
    "${var.gcf_sa_name}"
  ]
  description   = "Service account for gcf"
  generate_keys = false
  project_roles = [
    "${var.project_id}=>roles/cloudfunctions.invoker",
    "${var.project_id}=>roles/secretmanager.viewer",
    "${var.project_id}=>roles/cloudsql.instanceUser",
    "${var.project_id}=>roles/cloudsql.admin",
    "${var.project_id}=>roles/pubsub.publisher",
    "${var.project_id}=>roles/pubsub.subscriber"
  ]
}

module "gcf_hosts-insert" {
    source = "./modules/pub_sub_functions"
    project_id = "${var.project_id}"
    region = "${var.region}"

    fnc_name    = "${var.gcf_hosts-insert_name}"
    fnc_folder  = "${var.gcf_hosts-insert_name}"
    fnc_target  = "${var.gcf_target}"
    fnc_memory  = "${var.gcf_memory}"
    fnc_timeout = "${var.gcf_timeout}"
    
    fnc_pubsub_topic_name = "${var.gcf_hosts-insert_pubsub_topic_name}"

    fnc_service_account = "${module.gcf_sa.email}"

    environment_variables = {
        PROJECT_ID= "${var.project_id}",
        DB_CONNECTION_NAME= "${var.project_id}:${var.region}:${var.cloud_sql_instance_name}"
        SECRET_CONFIGURATION_CONTEXT= "${var.gcf_secret_configuration_context}"
        HOSTS_TABLE_NAME= "${var.gcf_hosts_table_name}"
        GUESTS_TABLE_NAME= "${var.gcf_guests_table_name}"
        MATCHES_TABLE_NAME= "${var.gcf_matches_table_name}"
    }
}

module "gcf_guests-insert" {
    source = "./modules/pub_sub_functions"
    project_id = "${var.project_id}"
    region = "${var.region}"

    fnc_name    = "${var.gcf_guests-insert_name}"
    fnc_folder  = "${var.gcf_guests-insert_name}"
    fnc_target  = "${var.gcf_target}"
    fnc_memory  = "${var.gcf_memory}"
    fnc_timeout = "${var.gcf_timeout}"
    
    fnc_pubsub_topic_name = "${var.gcf_guests-insert_pubsub_topic_name}"

    fnc_service_account = "${module.gcf_sa.email}"

    environment_variables = {
        PROJECT_ID= "${var.project_id}",
        DB_CONNECTION_NAME= "${var.project_id}:${var.region}:${var.cloud_sql_instance_name}"
        SECRET_CONFIGURATION_CONTEXT= "${var.gcf_secret_configuration_context}"
        HOSTS_TABLE_NAME= "${var.gcf_hosts_table_name}"
        GUESTS_TABLE_NAME= "${var.gcf_guests_table_name}"
        MATCHES_TABLE_NAME= "${var.gcf_matches_table_name}"
    }
}

module "gcf_matches-create" {
    source = "./modules/pub_sub_functions"
    project_id = "${var.project_id}"
    region = "${var.region}"

    fnc_name    = "${var.gcf_matches-create_name}"
    fnc_folder  = "${var.gcf_matches-create_name}"
    fnc_target  = "${var.gcf_target}"
    fnc_memory  = "${var.gcf_matches-create_memory}"
    fnc_timeout = "${var.gcf_timeout}"
    
    fnc_pubsub_topic_name = "${var.gcf_matches-create_pubsub_topic_name}"

    fnc_service_account = "${module.gcf_sa.email}"

    environment_variables = {
        PROJECT_ID= "${var.project_id}",
        DB_CONNECTION_NAME= "${var.project_id}:${var.region}:${var.cloud_sql_instance_name}"
        SECRET_CONFIGURATION_CONTEXT= "${var.gcf_secret_configuration_context}"
        HOSTS_TABLE_NAME= "${var.gcf_hosts_table_name}"
        GUESTS_TABLE_NAME= "${var.gcf_guests_table_name}"
        MATCHES_TABLE_NAME= "${var.gcf_matches_table_name}"
    }
}

module "gcf_change-status" {
    source = "./modules/pub_sub_functions"
    project_id = "${var.project_id}"
    region = "${var.region}"

    fnc_name    = "${var.gcf_matches-change-status_name}"
    fnc_folder  = "${var.gcf_matches-change-status_name}"
    fnc_target  = "${var.gcf_target}"
    fnc_memory  = "${var.gcf_memory}"
    fnc_timeout = "${var.gcf_timeout}"
    
    fnc_pubsub_topic_name = "${var.gcf_matches-change-status_pubsub_topic_name}"

    fnc_service_account = "${module.gcf_sa.email}"

    environment_variables = {
        PROJECT_ID= "${var.project_id}",
        DB_CONNECTION_NAME= "${var.project_id}:${var.region}:${var.cloud_sql_instance_name}"
        SECRET_CONFIGURATION_CONTEXT= "${var.gcf_secret_configuration_context}"
        HOSTS_TABLE_NAME= "${var.gcf_hosts_table_name}"
        GUESTS_TABLE_NAME= "${var.gcf_guests_table_name}"
        MATCHES_TABLE_NAME= "${var.gcf_matches_table_name}"
    }
}

module "gcf_matches_process_rejections" {
  source = "./modules/pub_sub_functions"
  project_id = "${var.project_id}"
  region = "${var.region}"

  fnc_name    = "${var.gcf_matches_process_rejections_name}"
  fnc_folder  = "${var.gcf_matches_process_rejections_name}"
  fnc_target  = "${var.gcf_target}"
  fnc_memory  = "${var.gcf_memory}"
  fnc_timeout = "${var.gcf_timeout}"

  fnc_pubsub_topic_name = "${var.gcf_matches_process_rejections_pubsub_topic_name}"

  fnc_service_account = "${module.gcf_sa.email}"

  environment_variables = {
    PROJECT_ID= "${var.project_id}",
    DB_CONNECTION_NAME= "${var.project_id}:${var.region}:${var.cloud_sql_instance_name}"
    SECRET_CONFIGURATION_CONTEXT= "${var.gcf_secret_configuration_context}"
    HOSTS_TABLE_NAME= "${var.gcf_hosts_table_name}"
    GUESTS_TABLE_NAME= "${var.gcf_guests_table_name}"
    MATCHES_TABLE_NAME= "${var.gcf_matches_table_name}"
  }
}
module "gcf_matches_process_timeout" {
  source = "./modules/pub_sub_functions"
  project_id = "${var.project_id}"
  region = "${var.region}"

  fnc_name    = "${var.gcf_matches_process_timeout_name}"
  fnc_folder  = "${var.gcf_matches_process_timeout_name}"
  fnc_target  = "${var.gcf_target}"
  fnc_memory  = "${var.gcf_memory}"
  fnc_timeout = "${var.gcf_timeout}"

  fnc_pubsub_topic_name = "${var.gcf_matches_process_timeout_pubsub_topic_name}"

  fnc_service_account = "${module.gcf_sa.email}"

  environment_variables = {
    PROJECT_ID= "${var.project_id}",
    DB_CONNECTION_NAME= "${var.project_id}:${var.region}:${var.cloud_sql_instance_name}"
    SECRET_CONFIGURATION_CONTEXT= "${var.gcf_secret_configuration_context}"
    HOSTS_TABLE_NAME= "${var.gcf_hosts_table_name}"
    GUESTS_TABLE_NAME= "${var.gcf_guests_table_name}"
    MATCHES_TABLE_NAME= "${var.gcf_matches_table_name}"
  }
}
module "gcf_send_notification_email_channel" {
  source = "./modules/pub_sub_functions"
  project_id = "${var.project_id}"
  region = "${var.region}"

  fnc_name    = "${var.gcf_send_notification_email_channel_name}"
  fnc_folder  = "${var.gcf_send_notification_email_channel_name}"
  fnc_target  = "${var.gcf_target}"
  fnc_memory  = "${var.gcf_memory}"
  fnc_timeout = "${var.gcf_timeout}"

  fnc_pubsub_topic_name = "${var.gcf_send_notification_email_channel_pubsub_topic_name}"

  fnc_service_account = "${module.gcf_sa.email}"

  environment_variables = {
    PROJECT_ID= "${var.project_id}",
    DB_CONNECTION_NAME= "${var.project_id}:${var.region}:${var.cloud_sql_instance_name}"
    SECRET_CONFIGURATION_CONTEXT= "${var.gcf_secret_configuration_context}"
    HOSTS_TABLE_NAME= "${var.gcf_hosts_table_name}"
    GUESTS_TABLE_NAME= "${var.gcf_guests_table_name}"
    MATCHES_TABLE_NAME= "${var.gcf_matches_table_name}"
  }
}

module "gcf_send_notification_sms_channel" {
  source = "./modules/pub_sub_functions"
  project_id = "${var.project_id}"
  region = "${var.region}"

  fnc_name    = "${var.gcf_send_notification_sms_channel_name}"
  fnc_folder  = "${var.gcf_send_notification_sms_channel_name}"
  fnc_target  = "${var.gcf_target}"
  fnc_memory  = "${var.gcf_memory}"
  fnc_timeout = "${var.gcf_timeout}"

  fnc_pubsub_topic_name = "${var.gcf_send_notification_sms_channel_pubsub_topic_name}"

  fnc_service_account = "${module.gcf_sa.email}"

  environment_variables = {
    PROJECT_ID= "${var.project_id}",
    DB_CONNECTION_NAME= "${var.project_id}:${var.region}:${var.cloud_sql_instance_name}"
    SECRET_CONFIGURATION_CONTEXT= "${var.gcf_secret_configuration_context}"
  }
}

module "gcf_matches-create-match-sealed-notifications" {
  source = "./modules/pub_sub_functions"
  project_id = "${var.project_id}"
  region = "${var.region}"

  fnc_name    = "${var.gcf_matches-create-match-sealed-notifications_name}"
  fnc_folder  = "${var.gcf_matches-create-match-sealed-notifications_name}"
  fnc_target  = "${var.gcf_target}"
  fnc_memory  = "${var.gcf_memory}"
  fnc_timeout = "${var.gcf_timeout}"

  fnc_pubsub_topic_name = "${var.gcf_matches-create-match-sealed-notifications_pubsub_topic_name}"

  fnc_service_account = "${module.gcf_sa.email}"

  environment_variables = {
    PROJECT_ID= "${var.project_id}"
    DB_CONNECTION_NAME= "${var.project_id}:${var.region}:${var.cloud_sql_instance_name}"
    SECRET_CONFIGURATION_CONTEXT= "${var.gcf_secret_configuration_context}"
    HOSTS_TABLE_NAME= "${var.gcf_hosts_table_name}"
    GUESTS_TABLE_NAME= "${var.gcf_guests_table_name}"
    MATCHES_TABLE_NAME= "${var.gcf_matches_table_name}"
    SEND_EMAIL_TOPIC = "${var.gcf_send_notification_email_channel_pubsub_topic_name}"
    SEND_SMS_TOPIC = "${var.gcf_send_notification_sms_channel_pubsub_topic_name}"
  }
}

module "gcf_matches-create-offering-notifications" {
  source = "./modules/pub_sub_functions"
  project_id = "${var.project_id}"
  region = "${var.region}"

  fnc_name    = "${var.gcf_matches-create-offering-notifications_name}"
  fnc_folder  = "${var.gcf_matches-create-offering-notifications_name}"
  fnc_target  = "${var.gcf_target}"
  fnc_memory  = "${var.gcf_memory}"
  fnc_timeout = "${var.gcf_timeout}"

  fnc_pubsub_topic_name = "${var.gcf_matches-create-offering-notifications_pubsub_topic_name}"

  fnc_service_account = "${module.gcf_sa.email}"

  environment_variables = {
    PROJECT_ID= "${var.project_id}"
    DB_CONNECTION_NAME= "${var.project_id}:${var.region}:${var.cloud_sql_instance_name}"
    SECRET_CONFIGURATION_CONTEXT= "${var.gcf_secret_configuration_context}"
    HOSTS_TABLE_NAME= "${var.gcf_hosts_table_name}"
    GUESTS_TABLE_NAME= "${var.gcf_guests_table_name}"
    MATCHES_TABLE_NAME= "${var.gcf_matches_table_name}"
    SEND_EMAIL_TOPIC = "${var.gcf_send_notification_email_channel_pubsub_topic_name}"
    SEND_SMS_TOPIC = "${var.gcf_send_notification_sms_channel_pubsub_topic_name}"
  }
}

module "gcf_unsubscribe-user" {
  source = "./modules/pub_sub_functions"
  project_id = "${var.project_id}"
  region = "${var.region}"

  fnc_name    = "${var.gcf_unsubscribe-user_name}"
  fnc_folder  = "${var.gcf_unsubscribe-user_name}"
  fnc_target  = "${var.gcf_target}"
  fnc_memory  = "${var.gcf_memory}"
  fnc_timeout = "${var.gcf_timeout}"

  fnc_pubsub_topic_name = "${var.gcf_unsubscribe-user_pubsub_topic_name}"

  fnc_service_account = "${module.gcf_sa.email}"

  environment_variables = {
    PROJECT_ID= "${var.project_id}"
    DB_CONNECTION_NAME= "${var.project_id}:${var.region}:${var.cloud_sql_instance_name}"
    SECRET_CONFIGURATION_CONTEXT= "${var.gcf_secret_configuration_context}"
    HOSTS_TABLE_NAME= "${var.gcf_hosts_table_name}"
    GUESTS_TABLE_NAME= "${var.gcf_guests_table_name}"
    MATCHES_TABLE_NAME= "${var.gcf_matches_table_name}"
  }
}

module "gcf_remove-users-by-email" {
  source = "./modules/pub_sub_functions"
  project_id = "${var.project_id}"
  region = "${var.region}"

  fnc_name    = "${var.gcf_remove-users-by-email_name}"
  fnc_folder  = "${var.gcf_remove-users-by-email_name}"
  fnc_target  = "${var.gcf_target}"
  fnc_memory  = "${var.gcf_memory}"
  fnc_timeout = "${var.gcf_timeout}"

  fnc_pubsub_topic_name = "${var.gcf_remove-users-by-email_pubsub_topic_name}"

  fnc_service_account = "${module.gcf_sa.email}"

  environment_variables = {
    PROJECT_ID= "${var.project_id}"
    DB_CONNECTION_NAME= "${var.project_id}:${var.region}:${var.cloud_sql_instance_name}"
    SECRET_CONFIGURATION_CONTEXT= "${var.gcf_secret_configuration_context}"
    HOSTS_TABLE_NAME= "${var.gcf_hosts_table_name}"
    GUESTS_TABLE_NAME= "${var.gcf_guests_table_name}"
    MATCHES_TABLE_NAME= "${var.gcf_matches_table_name}"
    UNSUBSCRIBE_USER_TOPIC= "${var.gcf_unsubscribe-user_pubsub_topic_name}"
  }
}

module "gcf_listing-delete" {
  source = "./modules/pub_sub_functions"
  project_id = "${var.project_id}"
  region = "${var.region}"

  fnc_name    = "${var.gcf_listing-delete_name}"
  fnc_folder  = "${var.gcf_listing-delete_name}"
  fnc_target  = "${var.gcf_target}"
  fnc_memory  = "${var.gcf_memory}"
  fnc_timeout = "${var.gcf_timeout}"

  fnc_pubsub_topic_name = "${var.gcf_listing-delete_pubsub_topic_name}"

  fnc_service_account = "${module.gcf_sa.email}"

  environment_variables = {
    PROJECT_ID= "${var.project_id}"
    DB_CONNECTION_NAME= "${var.project_id}:${var.region}:${var.cloud_sql_instance_name}"
    SECRET_CONFIGURATION_CONTEXT= "${var.gcf_secret_configuration_context}"
    HOSTS_TABLE_NAME= "${var.gcf_hosts_table_name}"
    GUESTS_TABLE_NAME= "${var.gcf_guests_table_name}"
    LISTING_DELETE_TOPIC= "${var.gcf_unsubscribe-user_pubsub_topic_name}"
  }
}

module "gcf_refresh_beds_stats" {
  source = "./modules/pub_sub_functions"
  project_id = "${var.project_id}"
  region = "${var.region}"

  fnc_name    = "${var.gcf_refresh_beds_stats_name}"
  fnc_folder  = "${var.gcf_refresh_beds_stats_name}"
  fnc_target  = "${var.gcf_target}"
  fnc_memory  = "${var.gcf_memory}"
  fnc_timeout = "${var.gcf_timeout}"

  fnc_pubsub_topic_name = "${var.gcf_refresh_beds_stats_pubsub_topic_name}"

  fnc_service_account = "${module.gcf_sa.email}"

  environment_variables = {
    PROJECT_ID= "${var.project_id}"
    DB_CONNECTION_NAME= "${var.project_id}:${var.region}:${var.cloud_sql_instance_name}"
    SECRET_CONFIGURATION_CONTEXT= "${var.gcf_secret_configuration_context}"
  }
}

module "gcf_accounts_upsert" {
  source = "./modules/pub_sub_functions"
  project_id = "${var.project_id}"
  region = "${var.region}"

  fnc_name    = "${var.gcf_accounts_upsert_name}"
  fnc_folder  = "${var.gcf_accounts_upsert_name}"
  fnc_target  = "${var.gcf_target}"
  fnc_memory  = "${var.gcf_memory}"
  fnc_timeout = "${var.gcf_timeout}"

  fnc_pubsub_topic_name = "${var.gcf_accounts_upsert_pubsub_topic_name}"

  fnc_service_account = "${module.gcf_sa.email}"

  environment_variables = {
    PROJECT_ID= "${var.project_id}"
    DB_CONNECTION_NAME= "${var.project_id}:${var.region}:${var.cloud_sql_instance_name}"
    SECRET_CONFIGURATION_CONTEXT= "${var.gcf_secret_configuration_context}"
  }
}
