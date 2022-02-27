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

variable "network_name" {
  description = "Network name"
  type        = string
}

variable "subnet_name1" {
  description = "Subnetwork name 1"
  type        = string
}

variable "subnet_name2" {
  description = "Subnetwork name 2"
  type        = string
}

variable "subnet_name3" {
  description = "Subnetwork name 3"
  type        = string
}

variable "subnet_name4" {
  description = "Subnetwork name 4"
  type        = string
}

variable "vpc_access_connector_name" {
  description = "vpc_access_connector_name"
  type        = string
}
