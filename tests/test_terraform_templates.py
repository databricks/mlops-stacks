import subprocess
import pytest
import json
import os
from collections import Counter
import sys

from utils import (
    generated_project_dir,
    parametrize_by_cloud,
    parametrize_by_project_generation_params,
)

_TERRAFORM_DIRECTORIES = ["staging", "prod"]


def run_test_command(cmd, working_dir):
    subprocess.run(
        f"set -ex\n{cmd}",
        shell=True,
        check=True,
        executable="/bin/bash",
        cwd=working_dir,
    )


@pytest.mark.parametrize("directory", _TERRAFORM_DIRECTORIES)
@parametrize_by_project_generation_params
def test_can_run_terraform_for_ml_resources(generated_project_dir, directory):
    working_dir = (
        generated_project_dir / "my-mlops-project" / "databricks-config" / directory
    )
    run_test_command(
        """
        terraform init -backend=false
        terraform fmt -check -recursive -diff
        terraform validate
        """,
        working_dir=working_dir,
    )


@pytest.mark.large
@pytest.mark.parametrize("subdirectory", ["terraform", "cicd"])
@parametrize_by_project_generation_params
def test_can_run_terraform_for_cicd(generated_project_dir, subdirectory):
    run_test_command(
        """
        terraform init -backend=false
        terraform fmt -check -recursive -diff
        terraform validate
        """,
        working_dir=generated_project_dir
        / "my-mlops-project"
        / ".mlops-setup-scripts"
        / subdirectory,
    )


@pytest.fixture()
def add_script_dir_to_pythonpath(generated_project_dir):
    module_parent_dir = os.path.join(
        generated_project_dir, "my-mlops-project", ".mlops-setup-scripts", "terraform"
    )
    sys.path.append(module_parent_dir)
    yield
    sys.path.remove(module_parent_dir)


@parametrize_by_project_generation_params
def test_can_parse_terraform_output_for_cicd(
    tmpdir, generated_project_dir, add_script_dir_to_pythonpath
):
    from bootstrap import write_formatted_terraform_output

    json_output = json.dumps(
        {
            "service_principal_application_id": {
                "sensitive": True,
                "type": "string",
                "value": "fake-application-id",
            },
            "service_principal_client_secret": {
                "sensitive": True,
                "type": "string",
                "value": "fake-client-secret",
            },
        }
    )
    output_file = tmpdir.join("tf-output").strpath
    write_formatted_terraform_output(json_output, output_file)
    with open(output_file, "r") as handle:
        output = json.load(handle)
        assert output == {
            "service_principal_application_id": "fake-application-id",
            "service_principal_client_secret": "fake-client-secret",
        }
