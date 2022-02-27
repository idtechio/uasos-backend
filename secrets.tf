resource "google_secret_manager_secret" "secret-key" {
  project  = var.project_id
  for_each = toset(local.secrets)

  provider  = google-beta
  secret_id = each.key

  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
}

resource "google_secret_manager_secret_iam_binding" "secrets" {
  project  = var.project_id
  for_each = toset(local.secrets)

  secret_id = google_secret_manager_secret.secret-key[each.key].id
  role      = "roles/secretmanager.secretAccessor"
  members   = [
    "serviceAccount:${module.run-sa.email}",
  ]
}
