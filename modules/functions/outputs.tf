output "pubsub_topic_id" {
  value       = google_pubsub_topic.fnc_pubsub_topic.id
  description = "PubSub topic id"
}