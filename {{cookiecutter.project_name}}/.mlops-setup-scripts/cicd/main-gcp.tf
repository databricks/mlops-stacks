# resource "databricks_group" "mlops-service-principal-group-staging" {
#   display_name = "{{cookiecutter.service_principal_group}}"
#   provider     = databricks.staging
# }

# resource "databricks_group" "mlops-service-principal-group-prod" {
#   display_name = "{{cookiecutter.service_principal_group}}"
#   provider     = databricks.prod
# }

# resource "google_project_iam_member" "service_account_token_creator" {
#   project = var.gcp-project-id
#   role  = "roles/iam.serviceAccountTokenCreator"
#   member  = "serviceAccount:${google_service_account.databricks_service_account.email}"
# }

{% if cookiecutter.cicd_platform == "gitHub" -%}
locals {
  git_org_name  = split("/", var.github_repo_url)[length(split("/", var.github_repo_url)) - 2]
  git_repo_name = split("/", var.github_repo_url)[length(split("/", var.github_repo_url)) - 1]
}

resource "google_service_account" "github_action_service_account" {
  account_id   = "github-action-sa"
  display_name = "Service Account for Github Actions"
  project      = var.gcp-project-id
}

resource "google_project_iam_member" "github_action_service_account" {
  project = var.gcp-project-id
  for_each = toset([
    "roles/storage.objectViewer",
    "roles/storage.objectAdmin"
  ])
  role   = each.key
  member = "serviceAccount:${google_service_account.github_action_service_account.email}"
}

module "gh_oidc" {
  source      = "terraform-google-modules/github-actions-runners/google//modules/gh-oidc"
  project_id  = var.gcp-project-id
  pool_id     = "github-action-pool"
  provider_id = "github-action-provider"
  sa_mapping = {
    "github-action-sa" = {
      sa_name   = "projects/${var.gcp-project-id}/serviceAccounts/github-action-sa@${var.gcp-project-id}.iam.gserviceaccount.com"
      attribute = "attribute.repository/${local.git_org_name}/${local.git_repo_name}"
    }
  }
  depends_on = [
    google_service_account.github_action_service_account
  ]
}
{% endif -%}

module "gcp_create_sp" {
  # depends_on = [databricks_group.mlops-service-principal-group-staging, databricks_group.mlops-service-principal-group-prod]
  source = "./terraform-databricks-mlops-gcp-project-with-sp-creation"
  providers = {
    databricks.staging = databricks.staging
    databricks.prod    = databricks.prod
  }
  gcp-project-id               = var.gcp-project-id
  service_principal_name       = "{{cookiecutter.project_name}}-cicd"
  project_directory_path       = "{{cookiecutter.mlflow_experiment_parent_dir}}"
  service_principal_group_name = "{{cookiecutter.service_principal_group}}"
}

data "databricks_current_user" "staging_user" {
  provider = databricks.staging
}

provider "databricks" {
  alias = "staging_sp"
  host  = "{{cookiecutter.databricks_staging_workspace_host}}"
  token = module.gcp_create_sp.staging_service_principal_token
}

provider "databricks" {
  alias = "prod_sp"
  host  = "{{cookiecutter.databricks_prod_workspace_host}}"
  token = module.gcp_create_sp.prod_service_principal_token
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
  # depends_on = [
  #   databricks_group.mlops-service-principal-group-prod,
  #   databricks_group.mlops-service-principal-group-staging
  # ]
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

data "google_project" "default" {
  project_id = var.gcp-project-id
}

output "GOOGLE_CLOUD_WORKLOAD_IDENTITY_PROVIDER" {
  value     = module.gh_oidc.provider_name
  sensitive = false
}

output "GOOGLE_CLOUD_SERVICE_ACCOUNT" {
  value     = google_service_account.github_action_service_account.email
  sensitive = false
}
{% if cookiecutter.cicd_platform == "gitHub" -%}
// We produce the service principal API tokens as output, to enable
// extracting their values and storing them as secrets in your CI system
//
// If using GitHub Actions, you can create new repo secrets through Terraform as well
// e.g. using https://registry.terraform.io/providers/integrations/github/latest/docs/resources/actions_secret

output "STAGING_WORKSPACE_TOKEN" {
  value     = module.gcp_create_sp.staging_service_principal_token
  sensitive = true
}

output "PROD_WORKSPACE_TOKEN" {
  value     = module.gcp_create_sp.prod_service_principal_token
  sensitive = true
}
{%- endif %}
