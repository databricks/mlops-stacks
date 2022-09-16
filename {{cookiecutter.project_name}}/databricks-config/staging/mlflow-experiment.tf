resource "databricks_mlflow_experiment" "experiment" {
  name        = "${local.mlflow_experiment_parent_dir}/${local.env_prefix}{{cookiecutter.experiment_base_name}}"
  description = "MLflow Experiment used to track runs for {{cookiecutter.project_name}} project."
}
