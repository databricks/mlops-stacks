import subprocess
import pytest
from functools import wraps
from utils import (
    databricks_cli,
    generated_project_dir,
    parametrize_by_cloud,
)


@pytest.mark.parametrize(
    "cicd_platform", ["github_actions", "github_actions_for_github_enterprise_servers"]
)
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
def test_generated_yaml_format(cloud, generated_project_dir):
    # Note: actionlint only works when the directory is a git project. Thus we begin by initiatilizing
    # the generated mlops project with git.
    subprocess.run(
        """
        git init
        bash <(curl https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash)
        ./actionlint -color
        """,
        shell=True,
        check=True,
        executable="/bin/bash",
        cwd=(generated_project_dir / "my-mlops-project"),
    )


@pytest.mark.large
@pytest.mark.parametrize(
    "cicd_platform", ["github_actions", "github_actions_for_github_enterprise_servers"]
)
@pytest.mark.parametrize(
    "setup_cicd_and_project,include_feature_store",
    [
        ("CICD_and_Project", "no"),
        ("CICD_and_Project", "no"),
        ("CICD_and_Project", "yes"),
        ("CICD_and_Project", "yes"),
    ],
)
@parametrize_by_cloud
def test_run_unit_tests_workflow(cloud, generated_project_dir):
    """Test that the GitHub workflow for running unit tests in the materialized project passes"""
    # We only test the unit test workflow, as it's the only one that doesn't require
    # Databricks REST API
    subprocess.run(
        """
        git init
        act -s GITHUB_TOKEN workflow_dispatch --workflows .github/workflows/my-mlops-project-run-tests.yml -j "unit_tests"
        """,
        shell=True,
        check=True,
        executable="/bin/bash",
        cwd=(generated_project_dir / "my-mlops-project"),
    )
