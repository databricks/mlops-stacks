terraform {
  required_providers {
    databricks = {
      source                = "databricks/databricks"
      version               = ">= 0.5.8"
      configuration_aliases = [databricks.staging, databricks.prod]
    }
  }
}
