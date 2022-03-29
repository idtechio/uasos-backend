resource "google_pubsub_topic" "fnc_pubsub_topic" {
  name = "${var.fnc_pubsub_topic_name}"
  project = "${var.project_id}"
}

resource "google_storage_bucket" "fnc_source_archive_bucket" {
  name          = "${var.project_id}-bkt-${var.fnc_name}"
  location      = "${var.region}"
  project       = "${var.project_id}"
  force_destroy = true
  storage_class = "STANDARD"
  labels        = {}

  uniform_bucket_level_access = true
}

data "archive_file" "fnc_archive" {
  type        = "zip"
  source_dir  = "${path.root}/functions_src/raw/${var.fnc_folder}"
  output_path = "${path.root}/functions_src/compressed/${var.fnc_folder}.zip"
}

resource "google_storage_bucket_object" "fnc_source_archive_object" {
  name   = "${data.archive_file.fnc_archive.output_md5}.zip"
  bucket = google_storage_bucket.fnc_source_archive_bucket.name
  source = data.archive_file.fnc_archive.output_path
  metadata = {}
}

resource "google_cloudfunctions_function" "fnc" {
  project     = "${var.project_id}"
  name        = "${var.fnc_name}"
  runtime     = "python39"
  labels      = {}

  environment_variables = "${var.environment_variables}"

  available_memory_mb   = "${var.fnc_memory}"
  source_archive_bucket = google_storage_bucket.fnc_source_archive_bucket.name
  source_archive_object = google_storage_bucket_object.fnc_source_archive_object.name
  entry_point           = "${var.fnc_target}"
  service_account_email = "${var.fnc_service_account}"
  timeout               = "${var.fnc_timeout}"
  
  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = google_pubsub_topic.fnc_pubsub_topic.name
  }
}
