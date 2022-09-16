locals {
  // Base workspace directory under which to create resources in the workspace for the current MLOps project
  // We assume the service principal used to deploy resources has CAN MANAGE permissions on directory
  // You may need to modify this value if you'd like to use a different directory for per-project resources
  mlflow_experiment_parent_dir = "{{cookiecutter.mlflow_experiment_parent_dir}}"
  // Current environment
  env = "staging"
  // Env-specific prefix to prepend to resource names. We recommend creating staging/prod resources
  // in separate workspaces to isolate prod resources from code running in CI, but this prefix
  // unblocks using a shared workspace across envs.
  env_prefix = "${local.env}-"
  // User group to give read permissions for the batch inference and model training jobs
  read_user_group = "{{cookiecutter.read_user_group}}"
}
