terraform {
  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = ">= 0.5.8"
    }
{%- if cookiecutter.cloud == "azure" %}
    azuread = {
      source  = "hashicorp/azuread"
      version = ">= 2.15.0"
    }
{%- endif %}
{%- if cookiecutter.cicd_platform == "azureDevOpsServices" %}
    azuredevops = {
      source  = "microsoft/azuredevops"
      version = ">= 0.2.1"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">=3.0.0"
    }
{%- endif %}
  }
  {% if cookiecutter.cloud == "azure" -%}
  // The `backend` block below configures the azurerm backend
  // (docs:
  // https://www.terraform.io/language/settings/backends/azurerm and
  // https://docs.microsoft.com/en-us/azure/developer/terraform/store-state-in-azure-storage)
  // for storing Terraform state in Azure Blob Storage. The targeted Azure Blob Storage bucket is
  // provisioned by the Terraform config under .mlops-setup-scripts/terraform:
  //
  backend "azurerm" {
    resource_group_name  = "{{cookiecutter.project_name_alphanumeric}}"
    storage_account_name = "{{cookiecutter.project_name_alphanumeric}}"
    container_name       = "cicd-setup-tfstate"
    key                  = "cicd-setup.terraform.tfstate"
  }
{% elif cookiecutter.cloud == "aws" -%}
  // The `backend` block below configures the s3 backend
  // (docs: https://www.terraform.io/language/settings/backends/s3)
  // for storing Terraform state in an AWS S3 bucket. The targeted S3 bucket and DynamoDB table are
  // provisioned by the Terraform config under .mlops-setup-scripts/terraform
  // Note: AWS region must be specified via environment variable or via the `region` field
  // in the provider block below, as described
  // in https://registry.terraform.io/providers/hashicorp/aws/latest/docs#environment-variables
  backend "s3" {
    bucket         = "{{cookiecutter.project_name}}-cicd-setup-tfstate"
    dynamodb_table = "{{cookiecutter.project_name}}-cicd-setup-tfstate-lock"
    key            = "cicd-setup.terraform.tfstate"
  }
{%- endif %}
}

provider "databricks" {
  alias   = "staging"
  profile = var.staging_profile
}

provider "databricks" {
  alias   = "prod"
  profile = var.prod_profile
}

{% if cookiecutter.cloud == "azure" -%}
provider "azuread" {}
{% endif -%}

{% if cookiecutter.cicd_platform == "azureDevOpsServices" %}
// Additional providers for Azure DevOps
provider "azuredevops" {
  org_service_url       = var.azure_devops_org_url
  personal_access_token = var.git_token
}

provider "azurerm" {
  features {}
}
{% endif -%}