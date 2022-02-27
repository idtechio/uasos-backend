locals {
  services_to_enable = [
    "cloudresourcemanager.googleapis.com",
    "compute.googleapis.com",
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "eventarc.googleapis.com",
    "iam.googleapis.com",
    "vpcaccess.googleapis.com",
    "servicenetworking.googleapis.com"
  ]
}