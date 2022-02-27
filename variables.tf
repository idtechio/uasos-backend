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
