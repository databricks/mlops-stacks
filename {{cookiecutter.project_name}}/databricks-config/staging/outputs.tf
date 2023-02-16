# This file declares values to include in the output json of the terraform deployment.
# To utilize infra as code, you may read values from the output json in your ML code, as we do out
# of the box for the mlflow experiment name and registered model name values.


# Batch inference job

output "{{cookiecutter.project_name}}_batch_inference_job_id" {
  value = databricks_job.batch_inference_job.id
}


# Mlflow experiment

output "{{cookiecutter.project_name}}_experiment_id" {
  value = databricks_mlflow_experiment.experiment.id
}

output "{{cookiecutter.project_name}}_experiment_name" {
  value = databricks_mlflow_experiment.experiment.name
}


# Model Registry registered model

output "{{cookiecutter.project_name}}_model_name" {
  value = databricks_mlflow_model.registered_model.name
}


# Training job

output "{{cookiecutter.project_name}}_training_job_id" {
  value = databricks_job.model_training_job.id
}
