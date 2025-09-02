import subprocess
import pytest
import yaml
import os
from functools import wraps
from utils import (
    databricks_cli,
    generated_project_dir,
    parametrize_by_cloud,
    generate,
    TEST_PROJECT_NAME,
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
    cicd_platform,
    cloud,
    include_models_in_unity_catalog,
    setup_cicd_and_project,
    generated_project_dir,
):
    """Test that GitLab CI/CD folder structure is created correctly."""
    if cloud == "gcp" and include_models_in_unity_catalog == "yes":
        # Skip test for GCP with Unity Catalog
        return

    # TEST: Check if gitlab folder has been created.
    project_dir = generated_project_dir / "my-mlops-project"
    gitlab_dir = project_dir / ".gitlab"
    gitlab_pipelines_dir = gitlab_dir / "pipelines"

    # Assert that GitLab directories exist
    assert gitlab_dir.exists(), "GitLab .gitlab directory should exist"
    assert gitlab_pipelines_dir.exists(), "GitLab pipelines directory should exist"

    # Also run the subprocess check and verify pipeline files exist
    result = subprocess.run(
        """
        ls ./.gitlab/pipelines
        """,
        shell=True,
        check=True,
        executable="/bin/bash",
        cwd=project_dir,
        capture_output=True,
        text=True,
    )

    # Assert that the output contains expected pipeline files
    pipeline_output = result.stdout.strip()
    assert pipeline_output, "Pipeline directory should contain files"
    assert "bundle-ci.yml" in pipeline_output, "Should contain CI pipeline file"
    if setup_cicd_and_project != "CICD_Only":
        assert (
            "bundle-cd-staging.yml" in pipeline_output
        ), "Should contain staging CD pipeline file"
        assert (
            "bundle-cd-prod.yml" in pipeline_output
        ), "Should contain production CD pipeline file"


@pytest.mark.parametrize("cicd_platform", ["gitlab"])
@pytest.mark.parametrize(
    "setup_cicd_and_project,include_feature_store,include_mlflow_recipes,include_models_in_unity_catalog",
    [
        ("CICD_and_Project", "no", "no", "no"),
        ("CICD_and_Project", "no", "no", "yes"),
        ("CICD_and_Project", "yes", "no", "no"),
        ("CICD_and_Project", "yes", "no", "yes"),
        ("CICD_Only", "no", "no", "no"),
    ],
)
@parametrize_by_cloud
def test_gitlab_pipeline_files_structure(
    cicd_platform, cloud, include_models_in_unity_catalog, generated_project_dir
):
    """Test that GitLab pipeline files have correct structure and content."""
    if cloud == "gcp" and include_models_in_unity_catalog == "yes":
        return

    project_dir = generated_project_dir / "my-mlops-project"
    gitlab_pipelines_dir = project_dir / ".gitlab" / "pipelines"

    # Verify expected pipeline files exist
    expected_files = [
        f"my-mlops-project-bundle-ci.yml",
        f"my-mlops-project-bundle-cd-staging.yml",
        f"my-mlops-project-bundle-cd-prod.yml",
    ]

    for pipeline_file in expected_files:
        pipeline_path = gitlab_pipelines_dir / pipeline_file
        assert pipeline_path.exists(), f"GitLab pipeline {pipeline_file} should exist"

        # Verify YAML syntax is valid
        with open(pipeline_path, "r") as f:
            pipeline_config = yaml.safe_load(f)
        assert (
            pipeline_config is not None
        ), f"Pipeline {pipeline_file} should have valid YAML"


@parametrize_by_cloud
def test_gitlab_docker_configuration(cloud, tmpdir, databricks_cli):
    """Test that GitLab Docker configuration is set up correctly."""
    context = {
        "input_setup_cicd_and_project": "CICD_and_Project",
        "input_project_name": TEST_PROJECT_NAME,
        "input_root_dir": TEST_PROJECT_NAME,
        "input_cloud": cloud,
        "input_cicd_platform": "gitlab",
        "input_docker_image": "custom/mlopsstacks:test",
    }

    generate(tmpdir, databricks_cli, context=context)

    project_dir = tmpdir / TEST_PROJECT_NAME
    gitlab_docker_dir = project_dir / ".gitlab" / "docker"

    # Verify Dockerfile exists
    dockerfile_path = gitlab_docker_dir / "Dockerfile"
    assert dockerfile_path.exists(), "GitLab Dockerfile should exist"

    # Verify Docker image push script exists
    push_script_path = gitlab_docker_dir / "push_image_to_gitlab.sh"
    assert push_script_path.exists(), "GitLab Docker push script should exist"

    # Verify push script is executable
    stat_info = os.stat(push_script_path)
    assert stat_info.st_mode & 0o111, "Push script should be executable"


@parametrize_by_cloud
def test_gitlab_pipeline_stages_and_jobs(cloud, tmpdir, databricks_cli):
    """Test that GitLab pipelines contain expected stages and jobs."""
    context = {
        "input_setup_cicd_and_project": "CICD_and_Project",
        "input_project_name": TEST_PROJECT_NAME,
        "input_root_dir": TEST_PROJECT_NAME,
        "input_cloud": cloud,
        "input_cicd_platform": "gitlab",
    }

    generate(tmpdir, databricks_cli, context=context)

    project_dir = tmpdir / TEST_PROJECT_NAME
    ci_pipeline_path = (
        project_dir / ".gitlab" / "pipelines" / f"{TEST_PROJECT_NAME}-bundle-ci.yml"
    )

    with open(ci_pipeline_path, "r") as f:
        ci_config = yaml.safe_load(f)

    # Verify CI pipeline has expected structure
    # GitLab CI config can have either top-level "stages" or individual jobs with "stage" properties
    if "stages" in ci_config:
        assert "variables" in ci_config, "CI pipeline should define variables"
        # Verify stages contain expected CI stages
        stages = ci_config["stages"]
        expected_stages = ["unit-tests", "integration-tests"]
        for stage in expected_stages:
            assert stage in stages, f"CI pipeline should have {stage} stage"
    else:
        # Check that we have job definitions with stage properties
        assert (
            "unit-test" in ci_config or "integration-test" in ci_config
        ), "CI pipeline should have test job definitions"
        if "unit-test" in ci_config:
            assert (
                "stage" in ci_config["unit-test"]
            ), "unit-test job should have a stage"
        if "integration-test" in ci_config:
            assert (
                "stage" in ci_config["integration-test"]
            ), "integration-test job should have a stage"


def test_gitlab_environment_variables(tmpdir, databricks_cli):
    """Test that GitLab pipelines use correct environment variables."""
    context = {
        "input_setup_cicd_and_project": "CICD_and_Project",
        "input_project_name": TEST_PROJECT_NAME,
        "input_root_dir": TEST_PROJECT_NAME,
        "input_cloud": "azure",
        "input_cicd_platform": "gitlab",
        "input_docker_image": "databricksfieldeng/mlopsstacks:latest",
    }

    generate(tmpdir, databricks_cli, context=context)

    test_file_contents = (
        tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
    ).read_text("utf-8")

    # Verify Docker image parameter is correctly set for GitLab
    assert (
        "input_docker_image=databricksfieldeng/mlopsstacks:latest" in test_file_contents
    )


@parametrize_by_cloud
def test_gitlab_trigger_pipeline_exists(cloud, tmpdir, databricks_cli):
    """Test that GitLab trigger pipeline configuration exists."""
    context = {
        "input_setup_cicd_and_project": "CICD_and_Project",
        "input_project_name": TEST_PROJECT_NAME,
        "input_root_dir": TEST_PROJECT_NAME,
        "input_cloud": cloud,
        "input_cicd_platform": "gitlab",
    }

    generate(tmpdir, databricks_cli, context=context)

    project_dir = tmpdir / TEST_PROJECT_NAME
    trigger_pipeline_path = (
        project_dir / ".gitlab" / "pipelines" / f"{TEST_PROJECT_NAME}-triggers-cicd.yml"
    )

    assert trigger_pipeline_path.exists(), "GitLab trigger pipeline should exist"

    with open(trigger_pipeline_path, "r") as f:
        trigger_config = yaml.safe_load(f)

    assert trigger_config is not None, "Trigger pipeline should have valid YAML"


def test_gitlab_cd_pipelines_deployment_stages(tmpdir, databricks_cli):
    """Test that GitLab CD pipelines contain proper deployment stages."""
    context = {
        "input_setup_cicd_and_project": "CICD_and_Project",
        "input_project_name": TEST_PROJECT_NAME,
        "input_root_dir": TEST_PROJECT_NAME,
        "input_cloud": "azure",
        "input_cicd_platform": "gitlab",
    }

    generate(tmpdir, databricks_cli, context=context)

    project_dir = tmpdir / TEST_PROJECT_NAME

    # Test staging CD pipeline
    staging_cd_path = (
        project_dir
        / ".gitlab"
        / "pipelines"
        / f"{TEST_PROJECT_NAME}-bundle-cd-staging.yml"
    )
    with open(staging_cd_path, "r") as f:
        staging_config = yaml.safe_load(f)

    # Check for either stages or job definitions with stage properties
    assert (
        "stages" in staging_config or "deploy-stage" in staging_config
    ), "Staging CD should define stages or deployment jobs"

    # Test production CD pipeline
    prod_cd_path = (
        project_dir
        / ".gitlab"
        / "pipelines"
        / f"{TEST_PROJECT_NAME}-bundle-cd-prod.yml"
    )
    with open(prod_cd_path, "r") as f:
        prod_config = yaml.safe_load(f)

    # Check for either stages or job definitions with stage properties
    assert (
        "stages" in prod_config
        or "deploy-prod" in prod_config
        or "deploy-production" in prod_config
    ), "Production CD should define stages or deployment jobs"


def test_gitlab_readme_documentation(tmpdir, databricks_cli):
    """Test that GitLab-specific documentation is generated."""
    context = {
        "input_setup_cicd_and_project": "CICD_and_Project",
        "input_project_name": TEST_PROJECT_NAME,
        "input_root_dir": TEST_PROJECT_NAME,
        "input_cloud": "azure",
        "input_cicd_platform": "gitlab",
    }

    generate(tmpdir, databricks_cli, context=context)

    project_dir = tmpdir / TEST_PROJECT_NAME
    gitlab_readme_path = project_dir / ".gitlab" / "README.md"

    assert gitlab_readme_path.exists(), "GitLab README should exist"

    readme_contents = gitlab_readme_path.read_text("utf-8")
    assert "gitlab" in readme_contents.lower(), "README should mention GitLab"
    assert "pipeline" in readme_contents.lower(), "README should mention pipelines"
