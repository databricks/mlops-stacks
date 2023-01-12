// Copied from https://docs.microsoft.com/en-us/azure/developer/terraform/store-state-in-azure-storage?tabs=terraform#code-try-3
terraform {
  required_version = ">= 1.1.3"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.40.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "2.2.3"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "4.40.0"
    }
  }
}

provider "google" {
}

resource "google_storage_bucket" "tfstate" {
  name                        = "{{cookiecutter.project_name}}-tfstate"
  location                    = var.gcp_storage_bucket_location
  project                     = var.gcp_project_id
  uniform_bucket_level_access = true
}