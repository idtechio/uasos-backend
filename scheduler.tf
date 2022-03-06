resource "google_cloud_scheduler_job" "job" {
  name        = "gcf-matches-create-trigger"
  description = "gcf-matches-create-trigger"
  schedule    = "0 */3 * * *" # every 3 hours

  pubsub_target {
    topic_name = module.gcf_matches-create.pubsub_topic_id
    data       = base64encode("test")
  }
}
