variable "display_name" {
  type        = string
  description = "The display name for the service principal."
}

variable "group_name" {
  type        = string
  description = "The Databricks group name that the service principal will belong to. NOTE: The main purpose of this group is to give the service principal token usage permissions, so the group should have token usage permissions."
}

variable "service_principal_name" {
  type        = string
  description = "The Databricks service principal name."
}
variable "gcp-project-id" {
  type        = string
  description = "GCP Project ID."
}

resource "databricks_service_principal" "sp" {
  display_name         = var.display_name
  allow_cluster_create = true
}

data "databricks_group" "sp_group" {
  display_name = var.group_name
}

resource "databricks_group_member" "add_sp_to_group" {
  group_id  = data.databricks_group.sp_group.id
  member_id = databricks_service_principal.sp.id
}

resource "databricks_obo_token" "token" {
  depends_on       = [databricks_group_member.add_sp_to_group]
  application_id   = databricks_service_principal.sp.application_id
  comment          = "PAT on behalf of ${databricks_service_principal.sp.display_name}"
  lifetime_seconds = 8640000 // 100 day token
}

output "service_principal_application_id" {
  value       = databricks_service_principal.sp.application_id
  description = "Application ID of the created Databricks service principal."
}

output "service_principal_token" {
  value       = databricks_obo_token.token.token_value
  sensitive   = true
  description = "Sensitive personal access token (PAT) value of the created Databricks service principal."
}