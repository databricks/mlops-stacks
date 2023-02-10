terraform {
  {% if cookiecutter.cloud == "azure" -%}
  // The `backend` block below configures the azurerm backend
  // (docs:
  // https://www.terraform.io/language/settings/backends/azurerm and
  // https://docs.microsoft.com/en-us/azure/developer/terraform/store-state-in-azure-storage)
  // for storing Terraform state in Azure Blob Storage.
  // You can run the setup scripts in mlops-setup-scripts/terraform to provision the Azure Blob Storage container
  // referenced below and store appropriate credentials for accessing the container from CI/CD.
  //
  backend "azurerm" {
    resource_group_name  = "{{cookiecutter.project_name_alphanumeric}}"
    storage_account_name = "{{cookiecutter.project_name_alphanumeric}}"
    container_name       = "tfstate"
    key                  = "staging.terraform.tfstate"
  }
  {% elif cookiecutter.cloud == "aws" -%}
  // The `backend` block below configures the s3 backend
  // (docs: https://www.terraform.io/language/settings/backends/s3)
  // for storing Terraform state in an AWS S3 bucket. You can run the setup scripts in mlops-setup-scripts/terraform to
  // provision the S3 bucket referenced below and store appropriate credentials for accessing the bucket from CI/CD.
  backend "s3" {
    bucket         = "{{cookiecutter.project_name}}-tfstate"
    key            = "staging.terraform.tfstate"
    dynamodb_table = "{{cookiecutter.project_name}}-tfstate-lock"
    region         = "us-east-1"
  }
  {% endif -%}
  required_providers {
    databricks = {
      source = "databricks/databricks"
    }
  }
}
