output "project_directory_path" {
  value       = databricks_directory.prod_directory.path
  description = "Path/Name of Azure Databricks workspace directory created for the project."
}

output "staging_service_principal_token" {
  value       = module.staging_sp.service_principal_token
  sensitive   = true
  description = "Sensitive AAD token value of the created Azure Databricks service principal in the staging workspace."
}


output "prod_service_principal_token" {
  value       = module.prod_sp.service_principal_token
  sensitive   = true
  description = "Sensitive AAD token value of the created Azure Databricks service principal in the prod workspace."
}
