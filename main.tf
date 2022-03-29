terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 3.88.0"
    }

    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 4.11.0"
    }
  }

  backend "gcs" {
    bucket = "tf-state-ukrn-hlpr-dev"
  }
}

resource "google_project_service" "project_services" {
  for_each = toset(local.services_to_enable)
  project  = var.project_id
  service  = each.key
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

provider "google" {
  project = var.project_id
  region  = var.region
}
