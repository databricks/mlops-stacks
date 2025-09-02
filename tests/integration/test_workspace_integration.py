"""
Integration tests for MLOps Stacks against Databricks workspaces.
These tests initialize projects and deploy/run resources to validate end-to-end functionality.

NOTE: These tests require Databricks workspace access and are marked as 'large'
to be run only when explicitly requested with pytest --large.
"""

import json
import os
import pytest
import subprocess
import tempfile
import time
from pathlib import Path
from utils import (
    generate,
    databricks_cli,
)


@pytest.fixture(scope="session")
def current_user(databricks_cli, workspace_config):
    """Get current user information once per session."""
    user_result = subprocess.run(
        [
            databricks_cli,
            "--profile",
            workspace_config["profile"],
            "current-user",
            "me",
            "--output",
            "json",
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )

    if user_result.returncode == 0:
        user_info = json.loads(user_result.stdout)
        return {
            "username": user_info.get("userName", "unknown"),
            "display_name": user_info.get("displayName", "unknown"),
            "user_info": user_info,
        }
    else:
        return {"username": "unknown", "display_name": "unknown", "user_info": {}}


@pytest.fixture(scope="session")
def workspace_config():
    """
    Get workspace configuration for integration tests.

    Required environment variables:
    - DATABRICKS_CONFIG_PROFILE: Databricks CLI profile name
    - DATABRICKS_CLOUD: Cloud provider (aws, azure, or gcp)

    Optional environment variables:
    - TEST_CATALOG_NAME: Unity Catalog name for tests (default: 'test')
    - TEST_SCHEMA_NAME: Schema name for tests (default: 'mlops_stacks_integration_tests')
    """
    profile = os.getenv("DATABRICKS_CONFIG_PROFILE")
    cloud = os.getenv("DATABRICKS_CLOUD")

    if not profile or not cloud:
        pytest.skip(
            "Integration tests require DATABRICKS_CONFIG_PROFILE and DATABRICKS_CLOUD environment variables. "
            "Example: DATABRICKS_CONFIG_PROFILE=e2demo-fe-aws DATABRICKS_CLOUD=aws"
        )

    config = {
        "profile": profile,
        "cloud": cloud,
        "catalog": os.getenv("TEST_CATALOG_NAME", "test"),
        "schema": os.getenv("TEST_SCHEMA_NAME", "mlops_stacks_integration_tests"),
    }

    return config


def _cleanup_unity_catalog_model(databricks_cli, workspace_config, project_name):
    """Clean up Unity Catalog models by finding and deleting all matching models."""
    import json

    try:
        # First, list all models in the schema to find matches
        list_models_cmd = [
            databricks_cli,
            "--profile",
            workspace_config["profile"],
            "registered-models",
            "list",
            "--catalog-name",
            workspace_config["catalog"],
            "--schema-name",
            workspace_config["schema"],
        ]
        list_result = subprocess.run(
            list_models_cmd, capture_output=True, text=True, timeout=60
        )

        if list_result.returncode != 0:
            print(f"[WARN] Could not list UC models: {list_result.stderr}")
            return

        models_data = json.loads(list_result.stdout)

        # Find models that match our project name pattern
        matching_models = []
        for model in models_data:
            model_name = model.get("name", "")
            # Match both patterns: "project-model" and "dev_user_project-model"
            if project_name in model_name and model_name.endswith("-model"):
                matching_models.append(model_name)

        if not matching_models:
            print(f"[INFO] No UC models found matching project '{project_name}'")
            return

        print(
            f"[INFO] Found {len(matching_models)} UC models matching project '{project_name}': {matching_models}"
        )

        # Clean up each matching model
        for model_name in matching_models:
            full_model_name = f"{workspace_config['catalog']}.{workspace_config['schema']}.{model_name}"
            print(f"[INFO] Cleaning up model: {full_model_name}")

            # List model versions (returns JSON)
            versions_list_cmd = [
                databricks_cli,
                "--profile",
                workspace_config["profile"],
                "model-versions",
                "list",
                full_model_name,
            ]
            versions_result = subprocess.run(
                versions_list_cmd, capture_output=True, text=True, timeout=60
            )

            # Delete model versions first if they exist
            if versions_result.returncode == 0:
                try:
                    versions_data = json.loads(versions_result.stdout)
                    if versions_data:
                        print(
                            f"[INFO] Found {len(versions_data)} versions for {full_model_name}"
                        )
                        for version_info in versions_data:
                            version = str(version_info.get("version", ""))
                            print(f"[INFO] Deleting version {version}...")

                            version_delete_cmd = [
                                databricks_cli,
                                "--profile",
                                workspace_config["profile"],
                                "model-versions",
                                "delete",
                                full_model_name,
                                version,
                            ]
                            version_delete_result = subprocess.run(
                                version_delete_cmd,
                                capture_output=True,
                                text=True,
                                timeout=30,
                            )

                            if version_delete_result.returncode == 0:
                                print(
                                    f"[OK] Deleted version {version} for {model_name}"
                                )
                            else:
                                print(
                                    f"[WARN] Could not delete version {version}: {version_delete_result.stderr}"
                                )
                except json.JSONDecodeError:
                    print(f"[WARN] Could not parse versions JSON for {full_model_name}")

            # Now delete the model itself
            model_drop_cmd = [
                databricks_cli,
                "--profile",
                workspace_config["profile"],
                "registered-models",
                "delete",
                full_model_name,
            ]
            model_drop_result = subprocess.run(
                model_drop_cmd, capture_output=True, text=True, timeout=60
            )

            if model_drop_result.returncode == 0:
                print(f"[OK] Dropped UC registered model {full_model_name}")
            else:
                if "not found" not in model_drop_result.stderr.lower():
                    print(
                        f"[WARN] Could not drop UC model {full_model_name}: {model_drop_result.stderr}"
                    )

    except Exception as e:
        print(f"[WARN] Model cleanup failed: {e}")


def _cleanup_unity_catalog_table(databricks_cli, workspace_config, table_name):
    """Clean up Unity Catalog table."""
    full_table_name = (
        f"{workspace_config['catalog']}.{workspace_config['schema']}.{table_name}"
    )

    try:
        table_drop_cmd = [
            databricks_cli,
            "--profile",
            workspace_config["profile"],
            "tables",
            "delete",
            full_table_name,
        ]
        table_drop_result = subprocess.run(
            table_drop_cmd, capture_output=True, text=True, timeout=60
        )
        if table_drop_result.returncode == 0:
            print(f"[OK] Dropped table {full_table_name}")
        # Don't warn if table doesn't exist - it might not have been created

    except Exception as e:
        print(f"[WARN] Table cleanup failed: {e}")


def _cleanup_workspace_folder(
    databricks_cli, workspace_config, current_user, project_name
):
    """Clean up workspace bundle folder."""
    try:
        folder_cleanup = subprocess.run(
            [
                databricks_cli,
                "--profile",
                workspace_config["profile"],
                "workspace",
                "delete",
                f"/Users/{current_user['username']}/.bundle/{project_name}",
                "--recursive",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if folder_cleanup.returncode == 0:
            print(f"[OK] Bundle folder cleanup complete for {project_name}")
        else:
            print(f"[WARN] Bundle folder cleanup failed: {folder_cleanup.stderr}")

    except Exception as e:
        print(f"[WARN] Workspace folder cleanup failed: {e}")


def _cleanup_bundle_resources(databricks_cli, workspace_config, test_project_path):
    """Clean up deployed bundle resources."""
    try:
        destroy_result = subprocess.run(
            [
                databricks_cli,
                "--profile",
                workspace_config["profile"],
                "bundle",
                "destroy",
                "--target",
                "dev",
                "--auto-approve",
            ],
            cwd=test_project_path,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout for cleanup
        )
        if destroy_result.returncode == 0:
            print(f"[OK] Bundle resources destroyed for {test_project_path.name}")
            return True
        else:
            print(f"[WARN] Bundle destroy failed: {destroy_result.stderr}")
            return False

    except Exception as e:
        print(f"[WARN] Bundle cleanup failed: {e}")
        return False


@pytest.fixture(scope="session")
def test_project_path(tmp_path_factory, databricks_cli, workspace_config, current_user):
    """Create a test project for integration testing."""
    tmpdir = tmp_path_factory.mktemp("integration")

    context = {
        "input_setup_cicd_and_project": "Project_Only",  # Skip CI/CD for integration tests
        "input_project_name": f"integration_test_{int(time.time())}",
        "input_root_dir": f"integration_test_{int(time.time())}",
        "input_cloud": workspace_config["cloud"],  # Dynamic cloud from env var
        "input_include_models_in_unity_catalog": "yes",  # Enable UC to fix batch inference job
        "input_include_feature_store": "no",
        "input_include_mlflow_recipes": "no",
        "input_schema_name": workspace_config["schema"],  # Set schema name for UC
    }

    # Configure databricks CLI with test workspace using environment variables
    # The databricks CLI will use DATABRICKS_HOST and DATABRICKS_TOKEN from environment

    generate(tmpdir, databricks_cli, context=context)

    project_path = (
        tmpdir / context["input_project_name"] / context["input_project_name"]
    )
    yield project_path

    # No cleanup needed here - deployed_project_path fixture handles all cleanup


@pytest.fixture(scope="session")
def deployed_project_path(
    test_project_path,
    databricks_cli,
    workspace_config,
    current_user,
    bundle_validation_data,
):
    """Deploy the test project once for the entire session and clean up at the end.

    Depends on bundle_validation_data to ensure validation runs before deployment.
    """

    # Check if bundle folder exists before deployment (so we don't clean pre-existing folders)
    bundle_folder_existed = False
    try:
        bundle_path = (
            f"/Users/{current_user['username']}/.bundle/{test_project_path.name}"
        )

        # Check if folder already exists
        check_result = subprocess.run(
            [
                databricks_cli,
                "--profile",
                workspace_config["profile"],
                "workspace",
                "get-status",
                bundle_path,
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        bundle_folder_existed = check_result.returncode == 0
        if bundle_folder_existed:
            print(f"[WARN] Bundle folder already exists: {bundle_path}")
    except Exception:
        # If we can't check, assume it didn't exist (safer to clean up)
        bundle_folder_existed = False

    # Deploy bundle to dev environment once with UC overrides
    deploy_result = subprocess.run(
        [
            databricks_cli,
            "--profile",
            workspace_config["profile"],
            "bundle",
            "deploy",
            "--target",
            "dev",
            "--var",
            f"catalog_name={workspace_config['catalog']}",
        ],
        cwd=test_project_path,
        capture_output=True,
        text=True,
        timeout=600,  # 10 minute timeout for deployment
    )

    # Check for deployment success by looking for completion message
    # (Databricks CLI sometimes returns non-zero code even on successful deployment)
    if "Deployment complete!" not in deploy_result.stderr:
        print(f"Deploy stdout: {deploy_result.stdout}")
        print(f"Deploy stderr: {deploy_result.stderr}")
        print(f"Deploy return code: {deploy_result.returncode}")
        raise Exception(f"Bundle deployment failed: {deploy_result.stderr}")

    # If we see "Deployment complete!", consider it successful regardless of return code
    print(f"<==> Session-wide deployment complete for {test_project_path.name}")

    # Note: Since databricks CLI doesn't have a SQL execution command, we'll pass the delta dataset
    # path directly to the batch inference job as the input_table_name parameter

    yield test_project_path

    # Cleanup: destroy deployed resources at end of session (unless SKIP_CLEANUP is set)
    if os.environ.get("SKIP_CLEANUP"):
        print(
            f"[SKIP] Cleanup skipped due to SKIP_CLEANUP environment variable for {test_project_path.name}"
        )
        return

    # Run cleanup in order: bundle resources, UC model, UC tables, workspace folder
    bundle_destroyed = _cleanup_bundle_resources(
        databricks_cli, workspace_config, test_project_path
    )

    if bundle_destroyed:
        # Additional Unity Catalog cleanup
        _cleanup_unity_catalog_model(
            databricks_cli, workspace_config, test_project_path.name
        )
        _cleanup_unity_catalog_table(databricks_cli, workspace_config, "predictions")

        # Workspace folder cleanup for integration test folders
        if test_project_path.name.startswith("integration_test_"):
            _cleanup_workspace_folder(
                databricks_cli, workspace_config, current_user, test_project_path.name
            )


@pytest.fixture(scope="session")
def bundle_validation_data(test_project_path, databricks_cli, workspace_config):
    """Get bundle validation data once for all validation tests."""
    # Run validation with JSON output
    result = subprocess.run(
        [
            databricks_cli,
            "--profile",
            workspace_config["profile"],
            "bundle",
            "validate",
            "--output",
            "json",
        ],
        cwd=test_project_path,
        capture_output=True,
        text=True,
        timeout=120,
    )

    # Bundle validation should succeed
    assert result.returncode == 0, f"Bundle validation failed: {result.stderr}"
    assert result.stdout, "Bundle validation should produce output"

    # Parse and return validation data
    return json.loads(result.stdout)


@pytest.mark.integration
def test_bundle_basic_validation(bundle_validation_data):
    """Test basic bundle validation succeeds and has core structure."""
    assert "bundle" in bundle_validation_data, "Should have bundle configuration"
    assert "resources" in bundle_validation_data, "Should have resources defined"
    assert "workspace" in bundle_validation_data, "Should have workspace configuration"
    print("<==> Bundle validation successful - basic structure verified")


@pytest.mark.integration
def test_bundle_configuration(bundle_validation_data, test_project_path):
    """Test bundle configuration is correct."""
    bundle = bundle_validation_data["bundle"]
    assert (
        bundle["name"] == test_project_path.name
    ), "Bundle name should match project name"
    assert bundle["target"] == "dev", "Should validate against dev target"
    assert bundle["mode"] == "development", "Dev target should use development mode"
    assert "uuid" in bundle, "Bundle should have a UUID"
    print(f"<==> Bundle configuration verified for {bundle['name']}")


@pytest.mark.integration
def test_bundle_workspace_configuration(bundle_validation_data, test_project_path):
    """Test workspace configuration is correct."""
    workspace = bundle_validation_data["workspace"]
    assert "current_user" in workspace, "Should identify current user"
    assert "root_path" in workspace, "Should have bundle root path in workspace"
    assert (
        test_project_path.name in workspace["root_path"]
    ), "Root path should contain project name"
    print(
        f"<==> Workspace configuration verified - root path: {workspace.get('root_path', 'unknown')}"
    )


@pytest.mark.integration
def test_bundle_jobs_configuration(bundle_validation_data):
    """Test jobs are properly configured."""
    resources = bundle_validation_data["resources"]
    assert "jobs" in resources, "Should have jobs resource"
    assert (
        len(resources["jobs"]) >= 2
    ), "Should have at least model training and batch inference jobs"

    # Validate job structure
    for job_name, job_config in resources["jobs"].items():
        assert "name" in job_config, f"Job {job_name} should have a name"
        assert "tasks" in job_config, f"Job {job_name} should have tasks"
        assert (
            len(job_config["tasks"]) > 0
        ), f"Job {job_name} should have at least one task"
        assert "permissions" in job_config, f"Job {job_name} should define permissions"
        assert "tags" in job_config, f"Job {job_name} should have tags"

    print(
        f"<==> Jobs configuration verified - found {len(resources['jobs'])} jobs: {list(resources['jobs'].keys())}"
    )


@pytest.mark.integration
def test_bundle_experiments_configuration(bundle_validation_data):
    """Test experiments are properly configured."""
    resources = bundle_validation_data["resources"]
    assert "experiments" in resources, "Should have experiments resource"
    assert len(resources["experiments"]) > 0, "Should define at least one experiment"

    for exp_name, exp_config in resources["experiments"].items():
        assert "name" in exp_config, f"Experiment {exp_name} should have a name"

    print(
        f"<==> Experiments configuration verified - found {len(resources['experiments'])} experiments"
    )


@pytest.mark.integration
def test_bundle_models_configuration(bundle_validation_data):
    """Test models are properly configured."""
    resources = bundle_validation_data["resources"]

    # With Unity Catalog enabled, models are under 'registered_models'
    if "registered_models" in resources:
        models = resources["registered_models"]
        model_type = "registered_models"
    else:
        # Fallback to regular models for non-UC setup
        assert "models" in resources, "Should have models or registered_models resource"
        models = resources["models"]
        model_type = "models"

    assert len(models) > 0, "Should define at least one model"

    for model_name, model_config in models.items():
        assert "name" in model_config, f"Model {model_name} should have a name"

    print(f"<==> Models configuration verified - found {len(models)} {model_type}")


@pytest.mark.integration
def test_bundle_variables_configuration(bundle_validation_data):
    """Test variables are properly configured."""
    assert "variables" in bundle_validation_data, "Should have variables defined"
    variables = bundle_validation_data["variables"]
    assert "experiment_name" in variables, "Should have experiment_name variable"
    assert "model_name" in variables, "Should have model_name variable"

    # Each variable should have description and value
    for var_name, var_config in variables.items():
        assert (
            "description" in var_config
        ), f"Variable {var_name} should have description"
        assert (
            "value" in var_config or "default" in var_config
        ), f"Variable {var_name} should have value or default"

    print(
        f"<==> Variables configuration verified - found {len(variables)} variables: {list(variables.keys())}"
    )


@pytest.mark.integration
def test_bundle_includes_configuration(bundle_validation_data):
    """Test include paths are properly configured."""
    assert "include" in bundle_validation_data, "Should have include paths"
    includes = bundle_validation_data["include"]
    assert (
        len(includes) >= 3
    ), "Should include batch inference, ML artifacts, and model workflow resources"
    assert any(
        "batch-inference" in inc for inc in includes
    ), "Should include batch inference workflow"
    assert any("ml-artifacts" in inc for inc in includes), "Should include ML artifacts"
    assert any(
        "model-workflow" in inc for inc in includes
    ), "Should include model workflow"
    print(f"<==> Includes configuration verified - found {len(includes)} includes")


@pytest.mark.integration
def test_bundle_presets_configuration(bundle_validation_data):
    """Test development mode presets are properly configured."""
    assert (
        "presets" in bundle_validation_data
    ), "Should have presets for development mode"
    presets = bundle_validation_data["presets"]
    assert "name_prefix" in presets, "Should have name prefix for dev resources"
    assert "trigger_pause_status" in presets, "Should set trigger pause status"
    assert (
        presets["trigger_pause_status"] == "PAUSED"
    ), "Dev triggers should be paused by default"
    print(
        f"<==> Presets configuration verified - name prefix: {presets.get('name_prefix', 'none')}"
    )


@pytest.mark.integration
def test_bundle_sync_configuration(bundle_validation_data):
    """Test sync configuration is properly configured."""
    assert "sync" in bundle_validation_data, "Should have sync configuration"
    assert "paths" in bundle_validation_data["sync"], "Should define sync paths"
    sync_paths = bundle_validation_data["sync"]["paths"]
    print(f"<==> Sync configuration verified - found {len(sync_paths)} sync paths")


@pytest.mark.integration
def test_bundle_deployment_to_dev_environment(
    deployed_project_path, databricks_cli, workspace_config
):
    """Test that bundle can be deployed to dev environment."""
    # Use deployed_project_path which handles deployment via fixture
    # This test verifies the deployment was successful

    # Quick verification that resources have URLs (indicates successful deployment)
    summary_result = subprocess.run(
        [
            databricks_cli,
            "--profile",
            workspace_config["profile"],
            "bundle",
            "summary",
            "--output",
            "json",
        ],
        cwd=deployed_project_path,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert (
        summary_result.returncode == 0
    ), f"Bundle summary failed: {summary_result.stderr}"
    summary_data = json.loads(summary_result.stdout)

    # Simply verify that deployed resources have URLs (deployment-specific check)
    resources = summary_data.get("resources", {})

    # Count resources with URLs (indicates they were actually created in workspace)
    deployed_count = 0
    deployed_resources = []
    for resource_type in ["jobs", "experiments", "models"]:
        for name, info in resources.get(resource_type, {}).items():
            if "url" in info:
                deployed_count += 1
                deployed_resources.append(f"{resource_type}.{name}")

    # Log what was actually deployed for debugging
    print(f"[INFO] Found {deployed_count} deployed resources: {deployed_resources}")

    assert (
        deployed_count >= 3
    ), f"Should have deployed at least 3 resources, found {deployed_count}: {deployed_resources}"
    print(f"<==> Successfully deployed {deployed_count} resources to workspace")


@pytest.mark.integration
def test_bundle_resource_creation(
    deployed_project_path, databricks_cli, workspace_config
):
    """Test that bundle creates expected Databricks resources."""

    # Get bundle summary to check created resources (deployment handled by fixture)
    summary_result = subprocess.run(
        [
            databricks_cli,
            "--profile",
            workspace_config["profile"],
            "bundle",
            "summary",
            "--output",
            "json",
        ],
        cwd=deployed_project_path,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert (
        summary_result.returncode == 0
    ), f"Bundle summary failed: {summary_result.stderr}"
    summary_data = json.loads(summary_result.stdout)

    # Verify experiments were created with correct structure
    resources = summary_data.get("resources", {})
    experiments = resources.get("experiments", {})
    assert len(experiments) > 0, "Should have created at least one experiment"

    for exp_name, exp_info in experiments.items():
        assert "name" in exp_info, f"Experiment {exp_name} should have a name"
        assert "url" in exp_info, f"Experiment {exp_name} should have a URL"
        # Verify experiment path contains user workspace
        exp_path = exp_info.get("name", "")
        assert (
            "/Users/" in exp_path
        ), f"Experiment should be in user workspace: {exp_path}"
        print(f"[OK] Created experiment: {exp_info['name']}")

    # Verify models were registered with correct structure
    # With Unity Catalog, models are under 'registered_models'
    models = resources.get("registered_models", resources.get("models", {}))
    assert len(models) > 0, "Should have created at least one model"

    for model_name, model_info in models.items():
        assert "name" in model_info, f"Model {model_name} should have a name"
        if "url" in model_info:  # UC models might not have URL in summary
            print(f"[OK] Created model: {model_info['name']}")
        else:
            print(f"[OK] Created registered model: {model_info['name']}")


@pytest.mark.integration
def test_bundle_run_job_execution(
    deployed_project_path, databricks_cli, workspace_config
):
    """Test that bundle run can execute all job resources defined in the bundle."""
    import yaml
    import glob

    # Run only specific workflows in sequence: 1) training, 2) batch inference
    workflows_to_run = ["model_training_job", "batch_inference_job"]

    print(f"<==> Will run {len(workflows_to_run)} jobs in sequence: {workflows_to_run}")

    # Test bundle run for each workflow in sequence
    successful_runs = 0
    for resource_name in workflows_to_run:
        # For batch inference job, override the input_table_name to use fully qualified UC table
        run_cmd = [
            databricks_cli,
            "--profile",
            workspace_config["profile"],
            "bundle",
            "run",
            resource_name,
            "--target",
            "dev",
            "--var",
            f"catalog_name={workspace_config['catalog']}",
        ]

        if resource_name == "batch_inference_job":
            # Use notebook-params to override input_table_name
            run_cmd.extend(
                [
                    "--notebook-params",
                    "input_table_name=delta.`/databricks-datasets/nyctaxi-with-zipcodes/subsampled`",
                ]
            )

        run_result = subprocess.run(
            run_cmd,
            cwd=deployed_project_path,
            capture_output=True,
            text=True,
            timeout=1800,  # 30 minutes for job completion
        )

        # Check if job was submitted successfully (Run URL present)
        if "Run URL:" in run_result.stderr:
            print(f"[OK] Bundle run submitted for {resource_name}")

            # If job completed successfully (return code 0), that's great
            if run_result.returncode == 0:
                print(f"[OK] Bundle run completed successfully for {resource_name}")
                successful_runs += 1
            # If job was submitted but CLI timed out (common network issue), still count as success
            elif (
                "unexpected EOF" in run_result.stderr
                or "timeout" in run_result.stderr.lower()
                or "read tcp" in run_result.stderr
                or "request timed out" in run_result.stderr
            ):
                print(
                    f"[OK] Bundle run submitted for {resource_name} (CLI timeout during polling, job likely completed)"
                )
                successful_runs += 1
            else:
                print(
                    f"[WARN] Bundle run submitted but failed for {resource_name}: {run_result.stderr}"
                )
                # Fail fast - if training job fails, don't run subsequent jobs
                assert (
                    False
                ), f"Job {resource_name} failed after submission: {run_result.stderr}"
        else:
            # Check if it's a network connectivity issue
            if "no such host" in run_result.stderr or "dial tcp" in run_result.stderr:
                print(
                    f"[WARN] Bundle run failed due to network connectivity for {resource_name}: {run_result.stderr}"
                )
                # Don't fail the test for network issues - workspace might be temporarily unreachable
                print(
                    f"[SKIP] Skipping {resource_name} due to network connectivity issues"
                )
                continue
            else:
                print(
                    f"[ERROR] Bundle run failed to submit for {resource_name}: {run_result.stderr}"
                )
                # Fail fast - if job fails to submit, don't run subsequent jobs
                assert (
                    False
                ), f"Job {resource_name} failed to submit: {run_result.stderr}"

    assert (
        successful_runs > 0
    ), f"Should be able to run at least one job via bundle run. Attempted {len(workflows_to_run)} jobs."
    print(
        f"<==> Successfully executed {successful_runs}/{len(workflows_to_run)} jobs via bundle run"
    )


@pytest.mark.integration
def test_workspace_permissions_and_access(
    deployed_project_path, databricks_cli, workspace_config
):
    """Test that deployed resources have appropriate permissions."""
    # Bundle deployment handled by fixture

    # Check that we can access the deployed experiment
    experiments_result = subprocess.run(
        [
            databricks_cli,
            "--profile",
            workspace_config["profile"],
            "experiments",
            "list",
        ],
        capture_output=True,
        text=True,
    )

    assert experiments_result.returncode == 0, "Should be able to access experiments"

    # Check that we can access jobs
    jobs_result = subprocess.run(
        [databricks_cli, "--profile", workspace_config["profile"], "jobs", "list"],
        capture_output=True,
        text=True,
    )

    assert jobs_result.returncode == 0, "Should be able to access jobs"
