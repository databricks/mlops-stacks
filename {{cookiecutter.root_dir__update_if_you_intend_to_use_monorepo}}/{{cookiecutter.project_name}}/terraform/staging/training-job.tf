resource "databricks_job" "model_training_job" {
  name = "${local.env_prefix}{{cookiecutter.project_name}}-model-training-job"

  # Optional validation: we include it here for convenience, to help ensure that the job references a notebook
  # that exists in the current repo. Note that Terraform >= 1.2 is required to use these validations
  lifecycle {
    postcondition {
      condition     = alltrue([for task in self.task : fileexists("../../../${task.notebook_task[0].notebook_path}.py")])
      error_message = "Databricks job must reference a notebook at a relative path from the root of the repo, with file extension omitted. Could not find one or more notebooks in repo"
    }
  }

  task {
    task_key = "Train"

    {% if cookiecutter.include_feature_store == "yes" %}notebook_task {
      notebook_path = "{{cookiecutter.project_name}}/training/notebooks/TrainWithFeatureStore"
      base_parameters = {
        env = local.env
        # TODO: Update training_data_path
        training_data_path = "/databricks-datasets/nyctaxi-with-zipcodes/subsampled"
        experiment_name    = databricks_mlflow_experiment.experiment.name
        model_name         = "${local.env_prefix}{{cookiecutter.model_name}}"
      }
    }
    {%- else -%}notebook_task {
      notebook_path = "{{cookiecutter.project_name}}/training/notebooks/Train"
      base_parameters = {
        env = local.env
      }
    }{% endif %}

    new_cluster {
      num_workers   = 3
      spark_version = "11.0.x-cpu-ml-scala2.12"
      node_type_id  = "{{cookiecutter.cloud_specific_node_type_id}}"
      custom_tags   = { "clusterSource" = "mlops-stack/0.0" }
    }
  }

  task {
    task_key = "ModelValidation"
    depends_on {
      task_key = "Train"
    }

    notebook_task {
      notebook_path = "{{cookiecutter.project_name}}/validation/notebooks/ModelValidation"
      base_parameters = {
        {%- if cookiecutter.include_feature_store == "no" %}
        env             = local.env{% endif %}
        experiment_name = databricks_mlflow_experiment.experiment.name
        # The `run_mode` defines whether model validation is enabled or not.
        # It can be one of the three values:
        # `disabled` : Do not run the model validation notebook.
        # `dry_run`  : Run the model validation notebook. Ignore failed model validation rules and proceed to move
        #               model to Production stage.
        # `enabled`  : Run the model validation notebook. Move model to Production stage only if all model validation
        #               rules are passing.
        # TODO: update run_mode
        run_mode = "disabled"
        # Whether to load the current registered "Production" stage model as baseline.
        # Baseline model is a requirement for relative change and absolute change validation thresholds.
        # TODO: update enable_baseline_comparison
        enable_baseline_comparison = "true"
        # Please refer to data parameter in mlflow.evaluate documentation https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.evaluate
        # TODO: update validation_input
        validation_input = "SELECT * FROM delta.`dbfs:/databricks-datasets/nyctaxi-with-zipcodes/subsampled`"
        {%- if cookiecutter.include_feature_store == "yes" %}
        # A string describing the model type. The model type can be either "regressor" and "classifier".
        # Please refer to model_type parameter in mlflow.evaluate documentation https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.evaluate
        # TODO: update model_type
        model_type = "regressor"
        # The string name of a column from data that contains evaluation labels.
        # Please refer to targets parameter in mlflow.evaluate documentation https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.evaluate
        # TODO: targets
        targets = "mean_squared_error"{% endif %}
        # Specifies the name of the function in {{cookiecutter.project_name}}/validation/validation.py that returns custom metrics.
        # TODO(optional): custom_metrics_loader_function
        custom_metrics_loader_function = "custom_metrics"
        # Specifies the name of the function in {{cookiecutter.project_name}}/validation/validation.py that returns model validation thresholds.
        # TODO(optional): validation_thresholds_loader_function
        validation_thresholds_loader_function = "validation_thresholds"
        # Specifies the name of the function in {{cookiecutter.project_name}}/validation/validation.py that returns evaluator_config.
        # TODO(optional): evaluator_config_loader_function
        evaluator_config_loader_function = "evaluator_config"
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
    task_key = "TriggerModelDeploy"
    depends_on {
      task_key = "ModelValidation"
    }

    notebook_task {
      notebook_path = "{{cookiecutter.project_name}}/deployment/model_deployment/notebooks/TriggerModelDeploy"
      base_parameters = {
        env = local.env
      }
    }

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

  git_source {
    url      = var.git_repo_url
    provider = "{{cookiecutter.cicd_platform}}"
    branch   = "{{cookiecutter.default_branch}}"
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

