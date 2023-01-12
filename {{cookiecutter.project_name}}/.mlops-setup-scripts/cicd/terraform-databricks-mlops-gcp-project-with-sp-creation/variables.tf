variable "service_principal_name" {
  type        = string
  description = "The display name for the service principals."
  default     = "Databricks Service Account"
}

variable "project_directory_path" {
  type        = string
  description = "Path/Name of Databricks workspace directory to be created for the project. NOTE: The parent directories in the path must already be created."
}

variable "service_principal_group_name" {
  type        = string
  description = "The name of the service principal group in the staging and prod workspace. The created service principals will be added to this group."
}

variable "gcp-project-id" {
  type        = string
  description = "GCP Project ID."
}

