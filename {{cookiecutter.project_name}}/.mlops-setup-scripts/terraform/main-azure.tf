// Copied from https://docs.microsoft.com/en-us/azure/developer/terraform/store-state-in-azure-storage?tabs=terraform#code-try-3
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=3.0.1"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "tfstate" {
  // Azure resource names can be at most 24 characters
  name     = substr("{{cookiecutter.project_name_alphanumeric}}", 0, 24)
  location = var.azure_resource_group_location
}

resource "azurerm_storage_account" "tfstate" {
  // Azure resource names can be at most 24 characters
  name                            = substr("{{cookiecutter.project_name_alphanumeric}}", 0, 24)
  resource_group_name             = azurerm_resource_group.tfstate.name
  location                        = azurerm_resource_group.tfstate.location
  account_tier                    = "Standard"
  account_replication_type        = "LRS"
  allow_nested_items_to_be_public = true
}

resource "azurerm_storage_container" "tfstate" {
  name                  = "tfstate"
  storage_account_name  = azurerm_storage_account.tfstate.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "cicd-setup-tfstate" {
  name                  = "cicd-setup-tfstate"
  storage_account_name  = azurerm_storage_account.tfstate.name
  container_access_type = "private"
}

output "ARM_ACCESS_KEY" {
  value     = azurerm_storage_account.tfstate.primary_access_key
  sensitive = true
}
