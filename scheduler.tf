resource "google_cloud_scheduler_job" "gcf-matches-create-trigger" {
  name        = "gcf-matches-create-trigger"
  description = "gcf-matches-create-trigger"
  schedule    = "0 */3 1 1 *" # every 3 hours

  pubsub_target {
    topic_name = module.gcf_matches-create.pubsub_topic_id
    data       = base64encode("{}")
  }
}

resource "google_cloud_scheduler_job" "gcf_matches-create-match-sealed-notifications-trigger" {
  name        = "gcf_matches-create-match-sealed-notifications-trigger"
  description = "gcf_matches-create-match-sealed-notifications-trigger"
  schedule    = "40 */3 1 1 *" # every 3 hours

  pubsub_target {
    topic_name = module.gcf_matches-create-match-sealed-notifications.pubsub_topic_id
    data       = base64encode("{}")
  }
}

resource "google_cloud_scheduler_job" "gcf_matches-create-offering-notifications-trigger" {
  name        = "gcf_matches-create-offering-notifications-trigger"
  description = "gcf_matches-create-offering-notifications-trigger"
  schedule    = "20 */3 1 1 *" # every 3 hours

  pubsub_target {
    topic_name = module.gcf_matches-create-offering-notifications.pubsub_topic_id
    data       = base64encode("{}")
  }
}

resource "google_cloud_scheduler_job" "gcf_matches-process-timeout-trigger" {
  name        = "gcf_matches-process-timeout-trigger"
  description = "gcf_matches-process-timeout-trigger"
  schedule    = "20 */5 1 1 *" # every 3 hours

  pubsub_target {
    topic_name = module.gcf_matches_process_timeout.pubsub_topic_id
    data       = base64encode("{}")
  }
}

resource "google_cloud_scheduler_job" "gcf_matches-process-rejections-trigger" {
  name        = "gcf_matches-process-rejections-trigger"
  description = "gcf_matches-process-rejections-trigger"
  schedule    = "20 */5 1 1 *" # every 3 hours

  pubsub_target {
    topic_name = module.gcf_matches_process_rejections.pubsub_topic_id
    data       = base64encode("{}")
  }
}
