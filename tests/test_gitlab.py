import subprocess
import pytest
from functools import wraps
from utils import (
    databricks_cli,
    generated_project_dir,
    parametrize_by_cloud,
)


@pytest.mark.parametrize("cicd_platform", ["gitlab"])
@pytest.mark.parametrize(
    "setup_cicd_and_project,include_feature_store,include_mlflow_recipes,include_models_in_unity_catalog",
    [
        ("CICD_and_Project", "no", "no", "no"),
        ("CICD_and_Project", "no", "no", "yes"),
        ("CICD_and_Project", "no", "yes", "no"),
        ("CICD_and_Project", "yes", "no", "no"),
        ("CICD_and_Project", "yes", "no", "yes"),
        ("CICD_Only", "no", "no", "no"),
    ],
)
@parametrize_by_cloud
def test_generated_gitlab_folder(
    cloud, include_models_in_unity_catalog, generated_project_dir
):
    if cloud == "gcp" and include_models_in_unity_catalog == "yes":
        # Skip test for GCP with Unity Catalog
        return

    # TEST: Check if gitlab folder has been created.
    subprocess.run(
        """
        ls ./.gitlab/pipelines
        """,
        shell=True,
        check=True,
        executable="/bin/bash",
        cwd=(generated_project_dir / "my-mlops-project"),
    )
    # TODO Check syntax with: gitlab-ci-local --file ./.gitlab/cicd.yml
    # (NOTE: syntax check requires gitlab-ci-local installed on VM)
