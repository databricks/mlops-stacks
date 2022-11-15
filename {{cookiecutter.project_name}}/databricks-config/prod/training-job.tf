resource "databricks_job" "model_training_job" {
  name = "${local.env_prefix}{{cookiecutter.project_name}}-model-training-job"

  # Optional validation: we include it here for convenience, to help ensure that the job references a notebook
  # that exists in the current repo. Note that Terraform >= 1.2 is required to use these validations
  lifecycle {
    postcondition {
      condition     = alltrue([for task in self.task : fileexists("../../${task.notebook_task[0].notebook_path}.py")])
      error_message = "Databricks job must reference a notebook at a relative path from the root of the repo, with file extension omitted. Could not find one or more notebooks in repo"
    }
  }

  task {
    task_key = "Train"

    {% if cookiecutter.include_feature_store == "yes" %}notebook_task {
      notebook_path = "notebooks/TrainWithFeatureStore"
      base_parameters = {
        env                = local.env
        training_data_path = "/databricks-datasets/nyctaxi-with-zipcodes/subsampled"
        experiment_name    = databricks_mlflow_experiment.experiment.name
        model_name         = "${local.env_prefix}{{cookiecutter.model_name}}"
      }
    }
    {%- else -%}notebook_task {
      notebook_path = "notebooks/Train"
      base_parameters = {
        env = local.env
      }
    }{% endif %}

    new_cluster {
      num_workers   = 3
      spark_version = "11.0.x-cpu-ml-scala2.12"
      node_type_id  = "{{cookiecutter.cloud_specific_node_type_id}}"
      # We set the job cluster to single user mode to enable your training job to access
      # the Unity Catalog.
      single_user_name   = data.databricks_current_user.service_principal.user_name
      data_security_mode = "SINGLE_USER"
      custom_tags        = { "clusterSource" = "mlops-stack/0.0" }
    }
  }

  task {
    task_key = "TriggerModelDeploy"
    depends_on {
      task_key = "Train"
    }

    notebook_task {
      notebook_path = "notebooks/TriggerModelDeploy"
      base_parameters = {
        env = local.env
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
