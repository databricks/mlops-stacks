resource "databricks_group" "mlops-service-principal-group-staging" {
  display_name = "{{cookiecutter.service_principal_group}}"
  provider     = databricks.staging
}

resource "databricks_group" "mlops-service-principal-group-prod" {
  display_name = "{{cookiecutter.service_principal_group}}"
  provider     = databricks.prod
}

module "azure_create_sp" {
  depends_on = [databricks_group.mlops-service-principal-group-staging, databricks_group.mlops-service-principal-group-prod]
  source     = "databricks/mlops-azure-project-with-sp-creation/databricks"
  providers = {
    databricks.staging = databricks.staging
    databricks.prod    = databricks.prod
    azuread            = azuread
  }
  service_principal_name       = "{{cookiecutter.project_name}}-cicd"
  project_directory_path       = "{{cookiecutter.mlflow_experiment_parent_dir}}"
  azure_tenant_id              = var.azure_tenant_id
  service_principal_group_name = "{{cookiecutter.service_principal_group}}"
}

data "databricks_current_user" "staging_user" {
  provider = databricks.staging
}

provider "databricks" {
  alias = "staging_sp"
  host  = "{{cookiecutter.databricks_staging_workspace_host}}"
  token = module.azure_create_sp.staging_service_principal_aad_token
}

provider "databricks" {
  alias = "prod_sp"
  host  = "{{cookiecutter.databricks_prod_workspace_host}}"
  token = module.azure_create_sp.prod_service_principal_aad_token
}

module "staging_workspace_cicd" {
  source = "./common"
  providers = {
    databricks = databricks.staging_sp
  }
  {%- if cookiecutter.cicd_platform == "gitHub" %}
  git_provider    = var.git_provider
  git_token       = var.git_token
  env             = "staging"
  github_repo_url = var.github_repo_url
  {%- elif cookiecutter.cicd_platform == "azureDevOpsServices" %}
  git_provider = var.git_provider
  git_token    = var.git_token
  {%- endif %}
}

module "prod_workspace_cicd" {
  source = "./common"
  providers = {
    databricks = databricks.prod_sp
  }
  {%- if cookiecutter.cicd_platform == "gitHub" %}
  git_provider    = var.git_provider
  git_token       = var.git_token
  env             = "prod"
  github_repo_url = var.github_repo_url
  {%- elif cookiecutter.cicd_platform == "azureDevOpsServices" %}
  git_provider = var.git_provider
  git_token    = var.git_token
  {%- endif %}
}

{% if cookiecutter.cicd_platform == "azureDevOpsServices" -%}
// Additional steps for Azure DevOps. Create staging and prod service principals for an enterprise application.
data "azuread_client_config" "current" {}

resource "azuread_application" "{{cookiecutter.project_name}}-aad" {
  display_name = "{{cookiecutter.project_name}}"
  owners       = [data.azuread_client_config.current.object_id]
}

resource "azuread_service_principal" "staging_service_principal" {
  application_id               = module.azure_create_sp.staging_service_principal_application_id
  app_role_assignment_required = false
  owners                       = [data.azuread_client_config.current.object_id]
}

resource "azuread_service_principal" "prod_service_principal" {
  application_id               = module.azure_create_sp.prod_service_principal_application_id
  app_role_assignment_required = false
  owners                       = [data.azuread_client_config.current.object_id]
}
{%- endif %}

{% if cookiecutter.cicd_platform == "gitHub" -%}
// We produce the service princpal's application ID, client secret, and tenant ID as output, to enable
// extracting their values and storing them as secrets in your CI system
//
// If using GitHub Actions, you can create new repo secrets through Terraform as well
// e.g. using https://registry.terraform.io/providers/integrations/github/latest/docs/resources/actions_secret
{% elif cookiecutter.cicd_platform == "azureDevOpsServices" -%}
// Output values
{%- endif %}
output "stagingAzureSpApplicationId" {
  value     = module.azure_create_sp.staging_service_principal_application_id
  sensitive = true
}

output "stagingAzureSpClientSecret" {
  value     = module.azure_create_sp.staging_service_principal_client_secret
  sensitive = true
}

output "stagingAzureSpTenantId" {
  value     = var.azure_tenant_id
  sensitive = true
}

output "prodAzureSpApplicationId" {
  value     = module.azure_create_sp.prod_service_principal_application_id
  sensitive = true
}

output "prodAzureSpClientSecret" {
  value     = module.azure_create_sp.prod_service_principal_client_secret
  sensitive = true
}

output "prodAzureSpTenantId" {
  value     = var.azure_tenant_id
  sensitive = true
}
