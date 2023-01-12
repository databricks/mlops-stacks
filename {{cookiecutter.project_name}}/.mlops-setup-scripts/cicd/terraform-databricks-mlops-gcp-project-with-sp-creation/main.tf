data "databricks_group" "staging_sp_group" {
  provider     = databricks.staging
  display_name = var.service_principal_group_name
}

data "databricks_group" "prod_sp_group" {
  provider     = databricks.prod
  display_name = var.service_principal_group_name
}

module "staging_sp" {
  source = "./modules/gcp-service-principal"
  providers = {
    databricks = databricks.staging
  }
  display_name           = var.service_principal_name
  group_name             = var.service_principal_group_name
  service_principal_name = var.service_principal_name
  gcp-project-id         = var.gcp-project-id
}

module "prod_sp" {
  source = "./modules/gcp-service-principal"
  providers = {
    databricks = databricks.prod
  }
  display_name           = var.service_principal_name
  group_name             = var.service_principal_group_name
  service_principal_name = var.service_principal_name
  gcp-project-id         = var.gcp-project-id
}

resource "databricks_directory" "staging_directory" {
  provider = databricks.staging
  path     = var.project_directory_path
}

resource "databricks_permissions" "staging_directory_usage" {
  provider       = databricks.staging
  directory_path = databricks_directory.staging_directory.path

  access_control {
    service_principal_name = module.staging_sp.service_principal_application_id
    permission_level       = "CAN_MANAGE"
  }
}

resource "databricks_directory" "prod_directory" {
  provider = databricks.prod
  path     = var.project_directory_path
}

resource "databricks_permissions" "prod_directory_usage" {
  provider       = databricks.prod
  directory_path = databricks_directory.prod_directory.path

  access_control {
    service_principal_name = module.prod_sp.service_principal_application_id
    permission_level       = "CAN_MANAGE"
  }
}

