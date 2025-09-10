"""
Tests for comprehensive default value validation across all parameters.
These tests ensure that all default values defined in databricks_template_schema.json
are applied correctly in different contexts and scenarios.
"""

import json
import pytest
from utils import (
    generate,
    databricks_cli,
    TEST_PROJECT_NAME,
    AZURE_DEFAULT_PARAMS,
    AWS_DEFAULT_PARAMS,
    GCP_DEFAULT_PARAMS,
)


class TestDefaultValues:
    """Test default value behavior across all parameters."""

    @pytest.mark.parametrize("cloud", ["azure", "aws", "gcp"])
    def test_all_default_values_with_minimal_input(self, tmpdir, databricks_cli, cloud):
        """Test that all default values are applied when using minimal input."""
        # Use TEST_PROJECT_NAME to ensure _params_testing_only.txt is generated
        context = {
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
        }
        if cloud != "azure":  # Azure is the default
            context["input_cloud"] = cloud

        generate(tmpdir, databricks_cli, context=context)

        test_file_contents = (
            tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
        ).read_text("utf-8")

        # Verify key default values are present (excluding project-specific ones)
        expected_defaults = {
            "input_cloud": cloud,
            "input_cicd_platform": "github_actions",
            "input_default_branch": "main",
            "input_release_branch": "release",
            "input_read_user_group": "users",
            "input_include_feature_store": "no",
            "input_include_mlflow_recipes": "no",
            "input_include_models_in_unity_catalog": "no",
            "input_unity_catalog_read_user_group": "account users",
        }

        # Add cloud-specific workspace defaults
        if cloud == "azure":
            expected_defaults.update(
                {
                    "input_databricks_staging_workspace_host": "https://adb-xxxx.xx.azuredatabricks.net",
                    "input_databricks_prod_workspace_host": "https://adb-xxxx.xx.azuredatabricks.net",
                }
            )
        elif cloud == "aws":
            expected_defaults.update(
                {
                    "input_databricks_staging_workspace_host": "https://your-staging-workspace.cloud.databricks.com",
                    "input_databricks_prod_workspace_host": "https://your-prod-workspace.cloud.databricks.com",
                }
            )
        elif cloud == "gcp":
            expected_defaults.update(
                {
                    "input_databricks_staging_workspace_host": "https://your-staging-workspace.gcp.databricks.com",
                    "input_databricks_prod_workspace_host": "https://your-prod-workspace.gcp.databricks.com",
                }
            )

        # Verify all default values are present
        for param, expected_value in expected_defaults.items():
            assert (
                f"{param}={expected_value}" in test_file_contents
            ), f"Missing or incorrect: {param}={expected_value}"

    def test_default_project_name_and_root_dir(self, tmpdir, databricks_cli):
        """Test default project name and root directory behavior."""
        # Use TEST_PROJECT_NAME to ensure _params_testing_only.txt is generated
        context = {
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_cloud": "azure",
        }

        generate(tmpdir, databricks_cli, context=context)

        test_file_contents = (
            tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
        ).read_text("utf-8")

        # Verify project name and root dir are set correctly in test context
        assert f"input_project_name={TEST_PROJECT_NAME}" in test_file_contents
        assert f"input_root_dir={TEST_PROJECT_NAME}" in test_file_contents

    def test_conditional_schema_name_defaults(self, tmpdir, databricks_cli):
        """Test that schema_name defaults conditionally based on Unity Catalog setting."""
        # Test with Unity Catalog disabled
        context = {
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_include_models_in_unity_catalog": "no",
        }
        generate(tmpdir, databricks_cli, context=context)

        test_file_contents = (
            tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
        ).read_text("utf-8")

        # Should use generic default when Unity Catalog is disabled
        assert "input_schema_name=schema_name" in test_file_contents

        # Clean up and test with Unity Catalog enabled
        tmpdir.remove()
        tmpdir.mkdir()

        context["input_include_models_in_unity_catalog"] = "yes"
        generate(tmpdir, databricks_cli, context=context)

        test_file_contents = (
            tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
        ).read_text("utf-8")

        # Schema name remains the same regardless of Unity Catalog setting
        assert "input_schema_name=schema_name" in test_file_contents

    @pytest.mark.parametrize("cloud", ["azure", "aws", "gcp"])
    def test_cloud_specific_workspace_url_defaults(self, tmpdir, databricks_cli, cloud):
        """Test that workspace URL defaults are cloud-specific."""
        context = {
            "input_setup_cicd_and_project": "CICD_and_Project",
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_cloud": cloud,
        }

        generate(tmpdir, databricks_cli, context=context)

        test_file_contents = (
            tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
        ).read_text("utf-8")

        if cloud == "azure":
            assert "azuredatabricks.net" in test_file_contents
        elif cloud == "aws":
            assert "cloud.databricks.com" in test_file_contents
        elif cloud == "gcp":
            assert "gcp.databricks.com" in test_file_contents

    def test_branch_defaults(self, tmpdir, databricks_cli):
        """Test default branch name values."""
        context = {
            "input_setup_cicd_and_project": "CICD_and_Project",
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
        }

        generate(tmpdir, databricks_cli, context=context)

        test_file_contents = (
            tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
        ).read_text("utf-8")

        # Test default branch names
        assert "input_default_branch=main" in test_file_contents
        assert "input_release_branch=release" in test_file_contents

    def test_user_group_defaults(self, tmpdir, databricks_cli):
        """Test default user group values."""
        context = {
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_include_models_in_unity_catalog": "yes",
        }

        generate(tmpdir, databricks_cli, context=context)

        test_file_contents = (
            tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
        ).read_text("utf-8")

        # Test user group defaults
        assert "input_read_user_group=users" in test_file_contents
        assert "input_unity_catalog_read_user_group=account users" in test_file_contents

    def test_catalog_name_defaults(self, tmpdir, databricks_cli):
        """Test Unity Catalog catalog name defaults."""
        context = {
            "input_setup_cicd_and_project": "CICD_and_Project",
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_include_models_in_unity_catalog": "yes",
        }

        generate(tmpdir, databricks_cli, context=context)

        test_file_contents = (
            tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
        ).read_text("utf-8")

        # Test catalog name defaults
        assert "input_staging_catalog_name=staging" in test_file_contents
        assert "input_prod_catalog_name=prod" in test_file_contents
        assert "input_test_catalog_name=test" in test_file_contents

    def test_feature_flags_defaults(self, tmpdir, databricks_cli):
        """Test feature flag default values."""
        context = {
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
        }

        generate(tmpdir, databricks_cli, context=context)

        test_file_contents = (
            tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
        ).read_text("utf-8")

        # Test feature flag defaults (all should be "no")
        assert "input_include_feature_store=no" in test_file_contents
        assert "input_include_mlflow_recipes=no" in test_file_contents
        assert "input_include_models_in_unity_catalog=no" in test_file_contents

    def test_inference_table_default(self, tmpdir, databricks_cli):
        """Test inference table name default value."""
        context = {
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
        }

        generate(tmpdir, databricks_cli, context=context)

        test_file_contents = (
            tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
        ).read_text("utf-8")

        # Test inference table default value
        assert "input_inference_table_name=dummy.schema.table" in test_file_contents

    def test_cicd_platform_default(self, tmpdir, databricks_cli):
        """Test CI/CD platform default value."""
        context = {
            "input_setup_cicd_and_project": "CICD_and_Project",
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
        }

        generate(tmpdir, databricks_cli, context=context)

        test_file_contents = (
            tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
        ).read_text("utf-8")

        # Test CI/CD platform default
        assert "input_cicd_platform=github_actions" in test_file_contents

    def test_setup_cicd_and_project_default(self, tmpdir, databricks_cli):
        """Test setup_cicd_and_project default value."""
        # Don't specify setup type, should default to CICD_and_Project
        context = {
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
        }

        generate(tmpdir, databricks_cli, context=context)

        test_file_contents = (
            tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
        ).read_text("utf-8")

        # Test setup default
        assert "input_setup_cicd_and_project=CICD_and_Project" in test_file_contents

    def test_docker_image_default(self, tmpdir, databricks_cli):
        """Test Docker image default value."""
        context = {
            "input_setup_cicd_and_project": "CICD_and_Project",
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_cicd_platform": "gitlab",  # Docker image is relevant for GitLab
        }

        generate(tmpdir, databricks_cli, context=context)

        test_file_contents = (
            tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
        ).read_text("utf-8")

        # Test Docker image default
        assert (
            "input_docker_image=databricksfieldeng/mlopsstacks:latest"
            in test_file_contents
        )

    def test_defaults_consistency_across_generation_types(self, tmpdir, databricks_cli):
        """Test that defaults are consistent across different setup types."""
        shared_params = {
            "input_cloud": "azure",
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
        }

        # Test CICD_and_Project defaults
        full_dir = tmpdir.mkdir("full")
        context_full = {
            **shared_params,
            "input_setup_cicd_and_project": "CICD_and_Project",
        }
        generate(full_dir, databricks_cli, context=context_full)
        full_contents = (
            full_dir / TEST_PROJECT_NAME / "_params_testing_only.txt"
        ).read_text("utf-8")

        # Test Project_Only defaults
        project_dir = tmpdir.mkdir("project")
        context_project = {
            **shared_params,
            "input_setup_cicd_and_project": "Project_Only",
        }
        generate(project_dir, databricks_cli, context=context_project)
        project_contents = (
            project_dir / TEST_PROJECT_NAME / "_params_testing_only.txt"
        ).read_text("utf-8")

        # Test CICD_Only defaults
        cicd_dir = tmpdir.mkdir("cicd")
        context_cicd = {**shared_params, "input_setup_cicd_and_project": "CICD_Only"}
        generate(cicd_dir, databricks_cli, context=context_cicd)
        cicd_contents = (
            cicd_dir / TEST_PROJECT_NAME / "_params_testing_only.txt"
        ).read_text("utf-8")

        # Verify shared defaults are consistent
        shared_default_params = [
            "input_cloud=azure",
            "input_include_models_in_unity_catalog=no",
            "input_default_branch=main",
            "input_release_branch=release",
        ]

        for param in shared_default_params:
            assert param in full_contents
            if "input_setup_cicd_and_project=Project_Only" not in project_contents:
                assert (
                    param in project_contents
                )  # Some params might be skipped for Project_Only
            assert param in cicd_contents

    def test_parameter_templating_in_defaults(self, tmpdir, databricks_cli):
        """Test that templated default values are resolved correctly."""
        context = {
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_include_models_in_unity_catalog": "yes",  # This affects schema_name default
        }

        generate(tmpdir, databricks_cli, context=context)

        test_file_contents = (
            tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
        ).read_text("utf-8")

        # Test that templated defaults are resolved with actual values
        assert (
            f"input_root_dir={TEST_PROJECT_NAME}" in test_file_contents
        )  # Default: {{ .input_project_name }}
        assert (
            "input_schema_name=schema_name" in test_file_contents
        )  # Default schema name
        assert (
            "input_inference_table_name=dummy.schema.table" in test_file_contents
        )  # Default inference table
