variable "region" {
  description = "Project resources region"
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
