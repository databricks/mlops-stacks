import subprocess
import pytest
from utils import (
    generated_project_dir,
    parametrize_by_cloud,
    parametrize_by_project_generation_params,
)


@pytest.mark.parametrize("cicd_platform", ["GitHub Actions"])
@pytest.mark.parametrize("include_feature_store", ["yes", "no"])
@parametrize_by_cloud
def test_generated_yaml_format(cicd_platform, generated_project_dir):
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
@pytest.mark.parametrize("cicd_platform", ["GitHub Actions"])
@pytest.mark.parametrize("include_feature_store", ["yes", "no"])
@parametrize_by_cloud
def test_run_unit_tests_workflow(cicd_platform, generated_project_dir):
    """Test that the GitHub workflow for running unit tests in the materialized project passes"""
    # We only test the unit test workflow, as it's the only one that doesn't require
    # Databricks REST API or Terraform remote state credentials
    subprocess.run(
        """
        git init
        act workflow_dispatch --workflows .github/workflows/run-tests.yml -j "unit_tests"
        """,
        shell=True,
        check=True,
        executable="/bin/bash",
        cwd=(generated_project_dir / "my-mlops-project"),
    )
