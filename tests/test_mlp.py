from utils import generated_project_dir, parametrize_by_cloud, parametrize_by_cicd_platform
import pytest
import os
import json
from mlflow.pipelines import Pipeline


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
@parametrize_by_cloud
@parametrize_by_cicd_platform
def test_mlp_yaml_valid(generated_project_dir, profile):
    project_dir = generated_project_dir / "my-mlops-project"
    os.chdir(project_dir / "notebooks")
    for env in ["staging", "prod"]:
        tf_output_dir = project_dir / "databricks-config" / "output"
        if not os.path.exists(tf_output_dir):
            tf_output_dir.mkdir()
        tf_output_file = tf_output_dir / f"{env}.json"
        fake_terraform_output = {
            "my-mlops-project_experiment_name": {
                "value": "fake-exp",
            },
            "my-mlops-project_model_name": {
                "value": "fake-model",
            },
        }
        tf_output_file.write_text(json.dumps(fake_terraform_output), encoding="utf-8")
    Pipeline(profile)
