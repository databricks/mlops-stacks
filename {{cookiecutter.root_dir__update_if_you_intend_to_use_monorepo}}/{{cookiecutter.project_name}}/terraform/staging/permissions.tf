resource "databricks_permissions" "batch_job_permissions" {
  job_id = databricks_job.batch_inference_job.id

  access_control {
    group_name       = local.read_user_group
    permission_level = "CAN_VIEW"
  }
}

resource "databricks_permissions" "training_job_permissions" {
  job_id = databricks_job.model_training_job.id

  access_control {
    group_name       = local.read_user_group
    permission_level = "CAN_VIEW"
  }
}

{% if cookiecutter.include_feature_store == "yes" %}
resource "databricks_permissions" "feature_job_permissions" {
  job_id = databricks_job.write_feature_table_job.id

  access_control {
    group_name       = local.read_user_group
    permission_level = "CAN_VIEW"
  }
}{% endif %}

resource "databricks_permissions" "mlflow_experiment_permissions" {
  experiment_id = databricks_mlflow_experiment.experiment.id

  access_control {
    group_name       = local.read_user_group
    permission_level = "CAN_READ"
  }
}

resource "databricks_permissions" "mlflow_model_permissions" {
  registered_model_id = databricks_mlflow_model.registered_model.registered_model_id

  access_control {
    group_name       = local.read_user_group
    permission_level = "CAN_READ"
  }
}
