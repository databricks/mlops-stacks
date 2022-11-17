resource "databricks_job" "write_feature_table_job" {
  name = "${local.env_prefix}{{cookiecutter.project_name}}-write-feature-table-job"

  # Optional validation: we include it here for convenience, to help ensure that the job references a notebook
  # that exists in the current repo. Note that Terraform >= 1.2 is required to use these validations
  lifecycle {
    postcondition {
      condition     = alltrue([for task in self.task : fileexists("../../${task.notebook_task[0].notebook_path}.py")])
      error_message = "Databricks job must reference a notebook at a relative path from the root of the repo, with file extension omitted. Could not find one or more notebooks in repo"
    }
  }

  task {
    task_key = "PickupFeatures"

    notebook_task {
      notebook_path = "notebooks/GenerateAndWriteFeatures"
      base_parameters = {
        env = local.env
        # TODO modify these arguments to reflect your setup.
        input_table_path = "/databricks-datasets/nyctaxi-with-zipcodes/subsampled"
        # TODO: Empty start/end dates will process the whole range. Update this as needed to process recent data.
        input_start_date          = ""
        input_end_date            = ""
        timestamp_column          = "tpep_pickup_datetime"
        output_table_name         = "feature_store_taxi_example.trip_pickup_features"
        features_transform_module = "pickup_features"
        primary_keys              = "zip"
      }
    }

    new_cluster {
      num_workers   = 3
      spark_version = "11.0.x-cpu-ml-scala2.12"
      node_type_id  = "{{cookiecutter.cloud_specific_node_type_id}}"
      custom_tags   = { "clusterSource" = "mlops-stack/0.0" }
    }
  }

  task {
    task_key = "DropoffFeatures"

    notebook_task {
      notebook_path = "notebooks/GenerateAndWriteFeatures"
      base_parameters = {
        env = local.env
        # TODO: modify these arguments to reflect your setup.
        input_table_path = "/databricks-datasets/nyctaxi-with-zipcodes/subsampled"
        # TODO: Empty start/end dates will process the whole range. Update this as needed to process recent data.
        input_start_date          = ""
        input_end_date            = ""
        timestamp_column          = "tpep_dropoff_datetime"
        output_table_name         = "feature_store_taxi_example.trip_dropoff_features"
        features_transform_module = "dropoff_features"
        primary_keys              = "zip"
      }
    }

    new_cluster {
      num_workers   = 3
      spark_version = "11.0.x-cpu-ml-scala2.12"
      node_type_id  = "{{cookiecutter.cloud_specific_node_type_id}}"
      custom_tags   = { "clusterSource" = "mlops-stack/0.0" }
    }
  }

  git_source {
    url      = var.git_repo_url
    provider = "{{cookiecutter.cicd_platform}}"
    branch   = "{{cookiecutter.release_branch}}"
  }

  schedule {
    quartz_cron_expression = "0 0 9 * * ?" # daily at 9am
    timezone_id            = "UTC"
  }

  # If you want to turn on notifications for this job, please uncomment the below code,
  # and provide a list of emails to the on_failure argument.
  #
  #  email_notifications {
  #    on_failure: []
  #  }
}

