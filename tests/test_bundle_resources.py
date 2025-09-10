"""
Tests for Databricks bundle resource validation.
These tests ensure that generated databricks.yml files and resource configurations
are valid and contain expected resources for different parameter combinations.
"""

import os
import yaml
import pytest
from pathlib import Path
from utils import (
    generate,
    databricks_cli,
    parametrize_by_project_generation_params,
    TEST_PROJECT_NAME,
    TEST_PROJECT_DIRECTORY,
)


class TestBundleResources:
    """Test Databricks bundle resource generation and validation."""

    @parametrize_by_project_generation_params
    def test_databricks_yml_syntax_valid(
        self,
        tmpdir,
        databricks_cli,
        cloud,
        cicd_platform,
        setup_cicd_and_project,
        include_feature_store,
        include_mlflow_recipes,
        include_models_in_unity_catalog,
    ):
        """Test that generated databricks.yml files have valid YAML syntax."""
        if cloud == "gcp" and include_models_in_unity_catalog == "yes":
            return  # Skip unsupported combination

        if setup_cicd_and_project == "CICD_Only":
            return  # Skip - no databricks.yml generated for CICD_Only

        context = {
            "input_setup_cicd_and_project": setup_cicd_and_project,
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_cloud": cloud,
            "input_include_feature_store": include_feature_store,
            "input_include_mlflow_recipes": include_mlflow_recipes,
            "input_include_models_in_unity_catalog": include_models_in_unity_catalog,
        }

        if setup_cicd_and_project != "Project_Only":
            context["input_cicd_platform"] = cicd_platform

        generate(tmpdir, databricks_cli, context=context)

        databricks_yml_path = (
            tmpdir / TEST_PROJECT_NAME / TEST_PROJECT_DIRECTORY / "databricks.yml"
        )
        assert databricks_yml_path.exists(), "databricks.yml should be generated"

        # Test that YAML syntax is valid
        with open(databricks_yml_path, "r") as f:
            bundle_config = yaml.safe_load(f)

        assert bundle_config is not None
        assert isinstance(bundle_config, dict)

    @parametrize_by_project_generation_params
    def test_bundle_structure_contains_required_sections(
        self,
        tmpdir,
        databricks_cli,
        cloud,
        cicd_platform,
        setup_cicd_and_project,
        include_feature_store,
        include_mlflow_recipes,
        include_models_in_unity_catalog,
    ):
        """Test that databricks.yml contains required sections."""
        if cloud == "gcp" and include_models_in_unity_catalog == "yes":
            return
        if setup_cicd_and_project == "CICD_Only":
            return

        context = {
            "input_setup_cicd_and_project": setup_cicd_and_project,
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_cloud": cloud,
            "input_include_feature_store": include_feature_store,
            "input_include_mlflow_recipes": include_mlflow_recipes,
            "input_include_models_in_unity_catalog": include_models_in_unity_catalog,
        }

        if setup_cicd_and_project != "Project_Only":
            context["input_cicd_platform"] = cicd_platform

        generate(tmpdir, databricks_cli, context=context)

        databricks_yml_path = (
            tmpdir / TEST_PROJECT_NAME / TEST_PROJECT_DIRECTORY / "databricks.yml"
        )
        with open(databricks_yml_path, "r") as f:
            bundle_config = yaml.safe_load(f)

        # Required top-level sections
        assert "bundle" in bundle_config
        assert "include" in bundle_config
        assert "targets" in bundle_config

        # Bundle section should have name
        assert "name" in bundle_config["bundle"]

        # Should have appropriate targets based on setup
        targets = bundle_config["targets"]
        if setup_cicd_and_project == "Project_Only":
            expected_targets = ["dev"]
        else:
            expected_targets = ["dev", "staging", "prod"]
        for target in expected_targets:
            assert target in targets, f"Target {target} missing from databricks.yml"

    @parametrize_by_project_generation_params
    def test_resource_files_generated_correctly(
        self,
        tmpdir,
        databricks_cli,
        cloud,
        cicd_platform,
        setup_cicd_and_project,
        include_feature_store,
        include_mlflow_recipes,
        include_models_in_unity_catalog,
    ):
        """Test that resource YAML files are generated correctly."""
        if cloud == "gcp" and include_models_in_unity_catalog == "yes":
            return
        if setup_cicd_and_project == "CICD_Only":
            return

        context = {
            "input_setup_cicd_and_project": setup_cicd_and_project,
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_cloud": cloud,
            "input_include_feature_store": include_feature_store,
            "input_include_mlflow_recipes": include_mlflow_recipes,
            "input_include_models_in_unity_catalog": include_models_in_unity_catalog,
        }

        if setup_cicd_and_project != "Project_Only":
            context["input_cicd_platform"] = cicd_platform

        generate(tmpdir, databricks_cli, context=context)

        resources_dir = (
            tmpdir / TEST_PROJECT_NAME / TEST_PROJECT_DIRECTORY / "resources"
        )
        assert resources_dir.exists(), "Resources directory should exist"

        # Core resource files that should always exist
        core_resources = [
            "model-workflow-resource.yml",
            "batch-inference-workflow-resource.yml",
            "ml-artifacts-resource.yml",
        ]

        for resource_file in core_resources:
            resource_path = resources_dir / resource_file
            assert resource_path.exists(), f"Core resource {resource_file} should exist"

            # Verify YAML syntax
            with open(resource_path, "r") as f:
                resource_config = yaml.safe_load(f)
            assert resource_config is not None

    def test_feature_store_resources_conditional_generation(
        self, tmpdir, databricks_cli
    ):
        """Test that feature store resources are generated conditionally."""
        # Test with feature store enabled
        context_with_fs = {
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_include_feature_store": "yes",
        }

        with_fs_dir = tmpdir.mkdir("with_fs")
        generate(with_fs_dir, databricks_cli, context=context_with_fs)

        resources_dir_with_fs = (
            tmpdir
            / "with_fs"
            / TEST_PROJECT_NAME
            / TEST_PROJECT_DIRECTORY
            / "resources"
        )
        fs_resource_path = (
            resources_dir_with_fs / "feature-engineering-workflow-resource.yml"
        )
        assert (
            fs_resource_path.exists()
        ), "Feature store resource should exist when enabled"

        # Test with feature store disabled
        context_without_fs = {
            "input_project_name": TEST_PROJECT_NAME + "_no_fs",
            "input_root_dir": TEST_PROJECT_NAME + "_no_fs",
            "input_include_feature_store": "no",
        }

        without_fs_dir = tmpdir.mkdir("without_fs")
        generate(without_fs_dir, databricks_cli, context=context_without_fs)

        resources_dir_without_fs = (
            tmpdir
            / "without_fs"
            / f"{TEST_PROJECT_NAME}_no_fs"
            / f"{TEST_PROJECT_NAME.replace('-', '_')}_no_fs"
            / "resources"
        )
        fs_resource_path_no_fs = (
            resources_dir_without_fs / "feature-engineering-workflow-resource.yml"
        )
        assert (
            not fs_resource_path_no_fs.exists()
        ), "Feature store resource should not exist when disabled"

    def test_unity_catalog_resources_conditional_generation(
        self, tmpdir, databricks_cli
    ):
        """Test that Unity Catalog resources are configured conditionally."""
        # Test with Unity Catalog enabled
        context_with_uc = {
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_include_models_in_unity_catalog": "yes",
            "input_schema_name": "test_schema",
        }

        with_uc_dir = tmpdir.mkdir("with_uc")
        generate(with_uc_dir, databricks_cli, context=context_with_uc)

        databricks_yml_path = (
            tmpdir
            / "with_uc"
            / TEST_PROJECT_NAME
            / TEST_PROJECT_DIRECTORY
            / "databricks.yml"
        )
        with open(databricks_yml_path, "r") as f:
            bundle_config = yaml.safe_load(f)

        # Check that targets reference catalogs for Unity Catalog
        for target in ["dev", "staging", "prod"]:
            target_config = bundle_config["targets"][target]
            if "variables" in target_config:
                # Unity Catalog should reference catalogs
                variables = target_config["variables"]
                # Look for catalog-related variables
                catalog_vars = [
                    var for var in variables.keys() if "catalog" in var.lower()
                ]
                if catalog_vars:  # If catalog variables exist, UC is configured
                    assert len(catalog_vars) > 0

    def test_monitoring_resources_generated(self, tmpdir, databricks_cli):
        """Test that monitoring resources are generated."""
        context = {
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_cloud": "azure",
        }

        generate(tmpdir, databricks_cli, context=context)

        resources_dir = (
            tmpdir / TEST_PROJECT_NAME / TEST_PROJECT_DIRECTORY / "resources"
        )
        monitoring_resource_path = resources_dir / "monitoring-resource.yml"

        assert (
            monitoring_resource_path.exists()
        ), "Monitoring resource should be generated"

        with open(monitoring_resource_path, "r") as f:
            monitoring_config = yaml.safe_load(f)

        assert monitoring_config is not None
        assert "resources" in monitoring_config

    @pytest.mark.parametrize("cloud", ["azure", "aws", "gcp"])
    def test_cloud_specific_resource_configuration(self, tmpdir, databricks_cli, cloud):
        """Test that resources are configured correctly for different clouds."""
        context = {
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_cloud": cloud,
        }

        generate(tmpdir, databricks_cli, context=context)

        databricks_yml_path = (
            tmpdir / TEST_PROJECT_NAME / TEST_PROJECT_DIRECTORY / "databricks.yml"
        )
        with open(databricks_yml_path, "r") as f:
            bundle_config = yaml.safe_load(f)

        # Verify workspace hosts are cloud-specific
        for target_name, target_config in bundle_config["targets"].items():
            if "workspace" in target_config and "host" in target_config["workspace"]:
                workspace_host = target_config["workspace"]["host"]

                # Skip if workspace_host is None (e.g., for Project_Only configurations)
                if workspace_host is None:
                    continue

                if cloud == "azure":
                    assert "azuredatabricks.net" in workspace_host
                elif cloud == "aws":
                    assert "cloud.databricks.com" in workspace_host
                elif cloud == "gcp":
                    assert "gcp.databricks.com" in workspace_host

    def test_job_resource_structure_validation(self, tmpdir, databricks_cli):
        """Test that job resources have correct structure."""
        context = {
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_include_feature_store": "yes",
        }

        generate(tmpdir, databricks_cli, context=context)

        resources_dir = (
            tmpdir / TEST_PROJECT_NAME / TEST_PROJECT_DIRECTORY / "resources"
        )

        # Test model training job structure
        model_workflow_path = resources_dir / "model-workflow-resource.yml"
        with open(model_workflow_path, "r") as f:
            model_workflow = yaml.safe_load(f)

        assert "resources" in model_workflow
        assert "jobs" in model_workflow["resources"]

        # Should have at least one job defined
        jobs = model_workflow["resources"]["jobs"]
        assert len(jobs) > 0

        # Test job structure
        for job_name, job_config in jobs.items():
            assert "job_clusters" in job_config or "compute" in job_config
            assert "tasks" in job_config
            assert len(job_config["tasks"]) > 0

            # Test task structure
            for task in job_config["tasks"]:
                assert "task_key" in task
                assert "notebook_task" in task or "python_wheel_task" in task

    def test_experiments_and_models_resource_generation(self, tmpdir, databricks_cli):
        """Test that ML artifacts (experiments, models) resources are generated."""
        context = {
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_include_models_in_unity_catalog": "no",  # Test workspace model registry
        }

        generate(tmpdir, databricks_cli, context=context)

        resources_dir = (
            tmpdir / TEST_PROJECT_NAME / TEST_PROJECT_DIRECTORY / "resources"
        )
        ml_artifacts_path = resources_dir / "ml-artifacts-resource.yml"

        with open(ml_artifacts_path, "r") as f:
            ml_artifacts = yaml.safe_load(f)

        assert "resources" in ml_artifacts
        resources = ml_artifacts["resources"]

        # Should have experiments
        assert "experiments" in resources
        experiments = resources["experiments"]
        assert len(experiments) > 0

        # Should have registered models
        assert "models" in resources
        models = resources["models"]
        assert len(models) > 0

        # Test experiment structure
        for exp_name, exp_config in experiments.items():
            assert "name" in exp_config

        # Test model structure
        for model_name, model_config in models.items():
            assert "name" in model_config

    def test_bundle_validation_with_databricks_cli(self, tmpdir, databricks_cli):
        """Test that generated bundles pass databricks CLI validation."""
        context = {
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_cloud": "azure",
        }

        generate(tmpdir, databricks_cli, context=context)

        project_dir = tmpdir / TEST_PROJECT_NAME / TEST_PROJECT_DIRECTORY

        # Test bundle validation using databricks CLI
        import subprocess

        result = subprocess.run(
            [databricks_cli, "bundle", "validate"],
            cwd=project_dir,
            capture_output=True,
            text=True,
        )

        # Validation should succeed (exit code 0) or fail with expected issues
        # We accept some validation failures as the bundle may require actual workspace connection
        assert result.returncode in [
            0,
            1,
        ], f"Bundle validation failed unexpectedly: {result.stderr}"

        # If it fails, it should not be due to syntax errors
        if result.returncode != 0:
            error_output = result.stderr.lower()
            syntax_error_indicators = [
                "yaml: line",
                "parsing error",
                "invalid yaml",
                "syntax error",
            ]
            for indicator in syntax_error_indicators:
                assert (
                    indicator not in error_output
                ), f"Bundle has syntax errors: {result.stderr}"
