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
    "setup_cicd_and_project,include_feature_store",
    [
        ("CICD_and_Project", "no"),
        ("CICD_and_Project", "no"),
        ("CICD_and_Project", "no"),
        ("CICD_and_Project", "yes"),
        ("CICD_and_Project", "yes"),
        ("CICD_Only", "no"),
    ],
)
@parametrize_by_cloud
def test_generated_gitlab_folder(cloud, generated_project_dir):

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
