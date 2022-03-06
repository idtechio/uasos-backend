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
    "${var.project_id}=>roles/cloudsql.admin"
  ]
}

module "gcf_hosts-insert" {
    source = "./modules/functions"
    project_id = "${var.project_id}"
    region = "${var.region}"

    fnc_name    = "${var.gcf_hosts-insert_name}"
    fnc_target  = "${var.gcf_hosts-insert_target}"
    fnc_folder  = "${var.gcf_hosts-insert_folder}"
    fnc_memory  = "${var.gcf_hosts-insert_memory}"
    fnc_timeout = "${var.gcf_hosts-insert_timeout}"
    
    fnc_pubsub_topic_name = "${var.gcf_hosts-insert_pubsub_topic_name}"

    fnc_service_account = "${module.gcf_sa.email}"

    environment_variables = {
        PROJECT_ID= "${var.project_id}",
        DB_CONNECTION_NAME= "${var.project_id}:${var.region}:${var.cloud_sql_instance_name}"
        HOSTS_TABLE_NAME= "${var.gcf_hosts-insert_hosts_table_name}"
        HOST_INITIAL_STATUS= "${var.gcf_hosts-insert_host_initial_status}"
        SECRET_CONFIGURATION_CONTEXT= "${var.gcf_secret_configuration_context}"
    }
}

module "gcf_guests-insert" {
    source = "./modules/functions"
    project_id = "${var.project_id}"
    region = "${var.region}"

    fnc_name    = "${var.gcf_guests-insert_name}"
    fnc_target  = "${var.gcf_guests-insert_target}"
    fnc_folder  = "${var.gcf_guests-insert_folder}"
    fnc_memory  = "${var.gcf_guests-insert_memory}"
    fnc_timeout = "${var.gcf_guests-insert_timeout}"
    
    fnc_pubsub_topic_name = "${var.gcf_guests-insert_pubsub_topic_name}"

    fnc_service_account = "${module.gcf_sa.email}"

    environment_variables = {
        PROJECT_ID= "${var.project_id}",
        DB_CONNECTION_NAME= google_sql_database_instance.master.connection_name
        GUESTS_TABLE_NAME= "${var.gcf_guests-insert_guests_table_name}"
        GUEST_INITIAL_STATUS= "${var.gcf_guests-insert_guest_initial_status}"
        SECRET_CONFIGURATION_CONTEXT= "${var.gcf_secret_configuration_context}"
    }
}

module "gcf_matches-create" {
    source = "./modules/functions"
    project_id = "${var.project_id}"
    region = "${var.region}"

    fnc_name    = "${var.gcf_matches-create_name}"
    fnc_target  = "${var.gcf_matches-create_target}"
    fnc_folder  = "${var.gcf_matches-create_folder}"
    fnc_memory  = "${var.gcf_matches-create_memory}"
    fnc_timeout = "${var.gcf_matches-create_timeout}"
    
    fnc_pubsub_topic_name = "${var.gcf_matches-create_pubsub_topic_name}"

    fnc_service_account = "${module.gcf_sa.email}"

    environment_variables = {
        PROJECT_ID= "${var.project_id}",
        DB_CONNECTION_NAME= google_sql_database_instance.master.connection_name
        SECRET_CONFIGURATION_CONTEXT= "${var.gcf_secret_configuration_context}"
    }
}

module "gcf_change-status" {
    source = "./modules/functions"
    project_id = "${var.project_id}"
    region = "${var.region}"

    fnc_name    = "${var.gcf_matches-change-status_name}"
    fnc_target  = "${var.gcf_matches-change-status_target}"
    fnc_folder  = "${var.gcf_matches-change-status_folder}"
    fnc_memory  = "${var.gcf_matches-change-status_memory}"
    fnc_timeout = "${var.gcf_matches-change-status_timeout}"
    
    fnc_pubsub_topic_name = "${var.gcf_matches-change-status_pubsub_topic_name}"

    fnc_service_account = "${module.gcf_sa.email}"

    environment_variables = {
        PROJECT_ID= "${var.project_id}",
        DB_CONNECTION_NAME= google_sql_database_instance.master.connection_name
        SECRET_CONFIGURATION_CONTEXT= "${var.gcf_secret_configuration_context}"
    }
}
module "gcf_matches-create-notifications" {
    source = "./modules/functions"
    project_id = "${var.project_id}"
    region = "${var.region}"

    fnc_name    = "${var.gcf_matches-create-notifications_name}"
    fnc_target  = "${var.gcf_matches-create-notifications_target}"
    fnc_folder  = "${var.gcf_matches-create-notifications_folder}"
    fnc_memory  = "${var.gcf_matches-create-notifications_memory}"
    fnc_timeout = "${var.gcf_matches-create-notifications_timeout}"
    
    fnc_pubsub_topic_name = "${var.gcf_matches-create-notifications_pubsub_topic_name}"

    fnc_service_account = "${module.gcf_sa.email}"

    environment_variables = {
        PROJECT_ID= "${var.project_id}",
        DB_CONNECTION_NAME= google_sql_database_instance.master.connection_name
        SECRET_CONFIGURATION_CONTEXT= "${var.gcf_secret_configuration_context}"
    }
}


module "gcf_matches_process_rejections" {
  source = "./modules/functions"
  project_id = "${var.project_id}"
  region = "${var.region}"

  fnc_name    = "${var.gcf_matches_process_rejections_name}"
  fnc_target  = "${var.gcf_matches_process_rejections_target}"
  fnc_folder  = "${var.gcf_matches_process_rejections_folder}"
  fnc_memory  = "${var.gcf_matches_process_rejections_memory}"
  fnc_timeout = "${var.gcf_matches_process_rejections_timeout}"

  fnc_pubsub_topic_name = "${var.gcf_matches_process_rejections_pubsub_topic_name}"

  fnc_service_account = "${module.gcf_sa.email}"

  environment_variables = {
    PROJECT_ID= "${var.project_id}",
    DB_CONNECTION_NAME= google_sql_database_instance.master.connection_name
    SECRET_CONFIGURATION_CONTEXT= "${var.gcf_secret_configuration_context}"
  }
}
module "gcf_matches_process_timeout" {
  source = "./modules/functions"
  project_id = "${var.project_id}"
  region = "${var.region}"

  fnc_name    = "${var.gcf_matches_process_timeout_name}"
  fnc_target  = "${var.gcf_matches_process_timeout_target}"
  fnc_folder  = "${var.gcf_matches_process_timeout_folder}"
  fnc_memory  = "${var.gcf_matches_process_timeout_memory}"
  fnc_timeout = "${var.gcf_matches_process_timeout_timeout}"

  fnc_pubsub_topic_name = "${var.gcf_matches_process_timeout_pubsub_topic_name}"

  fnc_service_account = "${module.gcf_sa.email}"

  environment_variables = {
    PROJECT_ID= "${var.project_id}",
    DB_CONNECTION_NAME= google_sql_database_instance.master.connection_name
    SECRET_CONFIGURATION_CONTEXT= "${var.gcf_secret_configuration_context}"
  }
}
module "gcf_send_notification_email_channel" {
  source = "./modules/functions"
  project_id = "${var.project_id}"
  region = "${var.region}"

  fnc_name    = "${var.gcf_send_notification_email_channel_name}"
  fnc_target  = "${var.gcf_send_notification_email_channel_target}"
  fnc_folder  = "${var.gcf_send_notification_email_channel_folder}"
  fnc_memory  = "${var.gcf_send_notification_email_channel_memory}"
  fnc_timeout = "${var.gcf_send_notification_email_channel_timeout}"

  fnc_pubsub_topic_name = "${var.gcf_send_notification_email_channel_pubsub_topic_name}"

  fnc_service_account = "${module.gcf_sa.email}"

  environment_variables = {
    PROJECT_ID= "${var.project_id}",
    DB_CONNECTION_NAME= google_sql_database_instance.master.connection_name
    SECRET_CONFIGURATION_CONTEXT= "${var.gcf_secret_configuration_context}"
  }
}
