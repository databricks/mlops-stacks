from utils import generated_project_dir, parametrize_by_project_generation_params
import pytest
import os
import json
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
def test_mlp_yaml_valid(generated_project_dir, profile, include_feature_store):
    # There's no MLP YAML configs generated when feature store is added,
    # so skip test in that case.
    if include_feature_store == "yes":
        return
    project_dir = generated_project_dir / "my-mlops-project"
    os.chdir(project_dir / "my_mlops_project" / "training" / "notebooks")
    Recipe(profile)
