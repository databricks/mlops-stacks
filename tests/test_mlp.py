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
def test_mlp_yaml_valid(
    generated_project_dir,
    profile,
    include_mlflow_recipes,
    cloud,
    include_models_in_unity_catalog,
    setup_cicd_and_project,
    include_feature_store,
):
    # There's no MLP YAML configs generated so skip test in that case.
    if include_mlflow_recipes == "no":
        return
    # Skip test for GCP with Unity Catalog (not supported)
    if cloud == "gcp" and include_models_in_unity_catalog == "yes":
        return
    # Skip test for CICD_Only as it doesn't generate project files
    if setup_cicd_and_project == "CICD_Only":
        return
    # Skip test when MLflow Recipes is incompatible with other features
    # Per databricks_template_schema.json, MLflow Recipes is skipped when:
    # - Unity Catalog is enabled
    # - Feature Store is enabled
    if include_models_in_unity_catalog == "yes":
        return
    if include_feature_store == "yes":
        return
    project_dir = generated_project_dir / "my-mlops-project"
    os.chdir(project_dir / "my_mlops_project" / "training" / "notebooks")
    Recipe(profile)
