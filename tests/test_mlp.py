from utils import (
    databricks_cli,
    generated_project_dir,
    parametrize_by_project_generation_params,
)
import pytest
import os
from mlflow.recipes import Recipe


@pytest.mark.parametrize(
    "profile",
    [
        "databricks-prod",
        "databricks-staging",
        "databricks-test",
        "databricks-dev",
        "local",
    ],
)
@parametrize_by_project_generation_params
def test_mlp_yaml_valid(generated_project_dir, profile, include_mlflow_recipes):
    # There's no MLP YAML configs generated so skip test in that case.
    if include_mlflow_recipes == "no":
        return
    project_dir = generated_project_dir / "my-mlops-project"
    os.chdir(project_dir / "my_mlops_project" / "training" / "notebooks")
    Recipe(profile)
