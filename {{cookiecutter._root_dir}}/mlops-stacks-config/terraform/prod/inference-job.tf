resource "databricks_job" "batch_inference_job" {
  name = "${local.env_prefix}{{cookiecutter.project_name}}-batch-inference-job"

  # Optional validation: we include it here for convenience, to help ensure that the job references a notebook
  # that exists in the current repo. Note that Terraform >= 1.2 is required to use these validations
  lifecycle {
    postcondition {
      condition     = fileexists("../../${self.notebook_task[0].notebook_path}.py")
      error_message = "Databricks job must reference a notebook at a relative path from the root of the repo, with file extension omitted. Could not find ${self.notebook_task[0].notebook_path}.py in repo"
    }
  }

  new_cluster {
    num_workers   = 3
    spark_version = "11.0.x-cpu-ml-scala2.12"
    node_type_id  = "{{cookiecutter.cloud_specific_node_type_id}}"
    # We set the job cluster to single user mode to enable your batch inference job to access
    # the Unity Catalog.
    single_user_name   = data.databricks_current_user.service_principal.user_name
    data_security_mode = "SINGLE_USER"
    custom_tags        = { "clusterSource" = "mlops-stack/0.0" }
  }

  notebook_task {
    notebook_path = "notebooks/BatchInference"
    base_parameters = {
      env = local.env
      # TODO: Specify input and output table names for batch inference here
      input_table_name  = ""
      output_table_name = "{{cookiecutter.project_name_alphanumeric}}_predictions"
    }
  }

  git_source {
    url      = var.git_repo_url
    provider = "{{cookiecutter.cicd_platform}}"
    branch   = "{{cookiecutter.release_branch}}"
  }

  schedule {
    quartz_cron_expression = "0 0 11 * * ?" # daily at 11am
    timezone_id            = "UTC"
  }

  # If you want to turn on notifications for this job, please uncomment the below code,
  # and provide a list of emails to the on_failure argument.
  #
  #  email_notifications {
  #    on_failure: []
  #  }
}
