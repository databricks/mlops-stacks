import subprocess
import pytest
from functools import wraps
from utils import (
    databricks_cli,
    generated_project_dir,
    parametrize_by_cloud,
)

@pytest.mark.parametrize(
    "cicd_platform", ["gitlab"]
)
@pytest.mark.parametrize(
    "setup_cicd_and_project,include_feature_store,include_mlflow_recipes,include_models_in_unity_catalog",
    [
        ("CICD_and_Project", "no", "no", "yes"),
    ],
)
@parametrize_by_cloud
@pytest.mark.parametrize("cloud", [  "azure" ])
def test_generated_yaml_format(
    cloud, include_models_in_unity_catalog, generated_project_dir
):
    print("generated_project_dir:", generated_project_dir)

    # TEST: Check if gitlab file has been created.
    # TODO Check syntax with: gitlab-ci-local --file ./.gitlab/cicd.yml 
    # (NOTE  requires gitlab-ci-local installed on ubuntu)
    subprocess.run(
        """
        ls ./.gitlab/cicd.yml
        """,
        shell=True,
        check=True,
        executable="/bin/bash",
        cwd=(generated_project_dir / "my-mlops-project"),
    )


 