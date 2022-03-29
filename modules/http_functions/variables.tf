variable "project_id" {
  type        = string
  description = "Google Cloud Project ID where resources should be created"
}

variable "region" {
  type        = string
  description = "Google Cloud region resources should be created, i.e. 'europe-west3'"
}

variable "fnc_name" {
  type        = string
  description = "#todo"
}

variable "fnc_target" {
  type        = string
  description = "#todo"
}

variable "fnc_folder" {
  type        = string
  description = "#todo"
}

variable "fnc_memory" {
  type        = string
  description = "#todo"
}

variable "fnc_timeout" {
  type        = number
  description = "#todo"
  default     = 60
}

variable "fnc_service_account" {
  type        = string
  description = "#todo"
}

variable "fnc_has_custom_iam" {
  type        = bool
  description = "#todo"
  default     = false
}

variable "fnc_iam_member" {
  type        = string
  description = "#todo"
  default     = false
}
