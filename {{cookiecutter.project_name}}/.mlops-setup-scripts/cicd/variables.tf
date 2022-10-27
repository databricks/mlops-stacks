variable "git_token" {
  type        = string
  {% if cookiecutter.cicd_platform == "gitHub" -%}
  description = "Git token used to (1) checkout ML code to run during CI and (2) call back from Databricks -> GitHub Actions to trigger a model deployment CD workflow when automated model retraining completes. Must have read and write permissions on the Git repo containing the current ML project"
  {% elif cookiecutter.cicd_platform == "azureDevOpsServices" -%}
  description = "Azure DevOps personal access token (PAT) used by the created service principal to create Azure DevOps Pipelines and checkout ML code to run during CI/CD. PAT must have read, write and manage permissions for Build and Code scopes on the Azure DevOps project. See the following on how to create and use PATs (https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops&tabs=Windows)"
  {% endif -%}
  sensitive   = true
  validation {
    condition     = length(var.git_token) > 0
    error_message = "The git_token variable cannot be empty"
  }
}

variable "git_provider" {
  type        = string
  description = "Hosted Git provider, as described in {{ 'dev-tools/api/latest/gitcredentials.html#operation/create-git-credential' | generate_doc_link(cookiecutter.cloud) }}. For example, 'gitHub' if using GitHub."
  default     = "{{cookiecutter.cicd_platform}}"
}

variable "staging_profile" {
  type        = string
  description = "Name of Databricks CLI profile on the current machine configured to run against the staging workspace"
  default     = "{{cookiecutter.project_name}}-staging"
}

variable "prod_profile" {
  type        = string
  description = "Name of Databricks CLI profile on the current machine configured to run against the prod workspace"
  default     = "{{cookiecutter.project_name}}-prod"
}

{% if cookiecutter.cicd_platform == "gitHub" -%}
variable "github_repo_url" {
  type        = string
  description = "URL of the hosted git repo containing the current ML project, e.g. https://github.com/myorg/myrepo"
  validation {
    condition     = length(var.github_repo_url) > 0
    error_message = "The github_repo_url variable cannot be empty"
  }
}
{% endif -%}

{%- if cookiecutter.cloud == "azure" %}
variable "azure_tenant_id" {
  type        = string
  description = "Azure tenant (directory) ID under which to create Service Principals for CI/CD. This should be the same Azure tenant as the one containing your Azure Databricks workspaces"
  validation {
    condition     = length(var.azure_tenant_id) > 0
    error_message = "The azure_tenant_id variable cannot be empty"
  }
}
{% endif -%}

{%- if cookiecutter.cicd_platform == "azureDevOpsServices" %}
variable "azure_devops_org_url" {
  type        = string
  description = "Azure DevOps organization URL. Should be in the form https://dev.azure.com/<organization_name>"
}

variable "azure_devops_project_name" {
  type        = string
  description = "Project name in Azure DevOps."
}

variable "azure_devops_repo_name" {
  type        = string
  description = "Repository name in Azure DevOps."
}

variable "arm_access_key" {
  type        = string
  description = "Azure resource manager key produced when initially bootstrapping Terraform. View this token by running $ vi ~/.{{cookiecutter.project_name}}-cicd-terraform-secrets.json"
  sensitive   = true
}
{% endif -%}
