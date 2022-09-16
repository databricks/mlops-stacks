resource "databricks_mlflow_model" "registered_model" {
  name = "${local.env_prefix}{{cookiecutter.model_name}}"
  depends_on = [
    databricks_job.batch_inference_job,
    databricks_job.model_training_job
  ]
  description = <<EOF
MLflow registered model for the "{{cookiecutter.project_name}}" ML Project. See the corresponding [Git repo](${var.git_repo_url}) for details on the project.

Links:
* [Git Repo](${var.git_repo_url}): contains ML code for the current project.
* [Recurring model training job]({{cookiecutter.databricks_prod_workspace_host}}#job/${databricks_job.model_training_job.id}): trains fresh model versions using the latest ML code.
* [Model deployment pipeline](${var.git_repo_url}/actions/workflows/deploy-model-${local.env}.yml): deploys model versions produced by the training job.
* [Recurring batch inference job]({{cookiecutter.databricks_prod_workspace_host}}#job/${databricks_job.batch_inference_job.id}): applies the latest ${local.env} model version for batch inference.
EOF
}
