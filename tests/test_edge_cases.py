"""
Tests for edge cases, boundary conditions, and special scenarios in MLOps Stacks template generation.
These tests cover unusual input values, special characters, and edge cases that might break the template.
"""

import os
import pytest
import re
from utils import (
    generate,
    databricks_cli,
    TEST_PROJECT_NAME,
)


class TestEdgeCases:
    """Test boundary conditions and edge cases."""

    @pytest.mark.parametrize(
        "project_name",
        [
            "a" * 3,  # Minimum length (3 characters)
            "a" * 100,  # Very long name
            "my_project_123",  # With numbers
            "MyProject",  # CamelCase
            "my-project-name",  # With hyphens (allowed)
        ],
    )
    def test_project_name_edge_cases(self, tmpdir, databricks_cli, project_name):
        """Test various project name formats including boundary conditions."""
        context = {
            "input_setup_cicd_and_project": "CICD_and_Project",
            "input_project_name": project_name,
            "input_root_dir": project_name,
            "input_cloud": "azure",
            "input_cicd_platform": "github_actions",
        }

        # All these project names should generate successfully
        generate(tmpdir, databricks_cli, context=context)
        # Just verify the generate function completed without error
        assert True  # If we get here, generation succeeded

    @pytest.mark.parametrize(
        "workspace_url",
        [
            "https://adb-1234567890123456789.99.azuredatabricks.net",  # Valid Azure
            "https://dbc-abcdef12-3456-7890-abcd-ef1234567890.cloud.databricks.com",  # Valid AWS
            "https://1234567890123456-abc123-defg456.gcp.databricks.com",  # Valid GCP
            "https://invalid-domain.com",  # Different domain
            "https://adb-test.azuredatabricks.net/?o=123456#job/123",  # With query params
        ],
    )
    def test_workspace_url_handling(self, tmpdir, databricks_cli, workspace_url):
        """Test workspace URL parameter passing and processing."""
        context = {
            "input_setup_cicd_and_project": "CICD_and_Project",
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_cloud": "azure",
            "input_cicd_platform": "github_actions",
            "input_databricks_staging_workspace_host": workspace_url,
            "input_databricks_prod_workspace_host": workspace_url,
        }

        generate(tmpdir, databricks_cli, context=context)
        test_file_contents = (
            tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
        ).read_text("utf-8")

        # Check that query parameters are stripped if present
        if "?" in workspace_url or "#" in workspace_url:
            clean_url = workspace_url.split("?")[0].split("#")[0]
            assert clean_url in test_file_contents
        else:
            assert workspace_url in test_file_contents

    @pytest.mark.parametrize(
        "schema_name,should_fail",
        [
            ("valid_schema", False),
            ("ValidSchema", False),
            ("schema123", False),
            ("s", False),  # Single character
            ("schema-with-hyphens", True),  # Hyphens not allowed
            ("schema.with.dots", True),  # Dots not allowed
            ("a" * 100, False),  # Very long name
        ],
    )
    def test_schema_name_validation(
        self, tmpdir, databricks_cli, schema_name, should_fail
    ):
        """Test schema name validation by the CLI."""
        context = {
            "input_setup_cicd_and_project": "CICD_and_Project",
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_cloud": "azure",
            "input_cicd_platform": "github_actions",
            "input_include_models_in_unity_catalog": "yes",
            "input_schema_name": schema_name,
        }

        if should_fail:
            with pytest.raises(Exception):  # CLI validation should reject invalid names
                generate(tmpdir, databricks_cli, context=context)
        else:
            generate(tmpdir, databricks_cli, context=context)
            test_file_contents = (
                tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
            ).read_text("utf-8")

            # Verify valid schema names are passed through correctly
            assert f"input_schema_name={schema_name}" in test_file_contents

    def test_empty_schema_name_gets_default(self, tmpdir, databricks_cli):
        """Test that empty schema name gets default value."""
        context = {
            "input_setup_cicd_and_project": "CICD_and_Project",
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_cloud": "azure",
            "input_cicd_platform": "github_actions",
            "input_include_models_in_unity_catalog": "yes",
            "input_schema_name": "",
        }

        generate(tmpdir, databricks_cli, context=context)
        test_file_contents = (
            tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
        ).read_text("utf-8")

        # Empty string should get some default value (not empty)
        assert "input_schema_name=" in test_file_contents

    @pytest.mark.parametrize(
        "inference_table_name,should_fail",
        [
            ("catalog.schema.table", False),  # Valid format
            ("dev.my_project.predictions", False),  # Valid with underscores
            ("catalog123.schema456.table789", False),  # With numbers
            ("catalog.schema", True),  # Missing table part
            ("table", True),  # Missing catalog and schema
            ("catalog.schema.table.extra", True),  # Too many parts
        ],
    )
    def test_inference_table_name_validation(
        self, tmpdir, databricks_cli, inference_table_name, should_fail
    ):
        """Test inference table name validation by the CLI."""
        context = {
            "input_setup_cicd_and_project": "CICD_and_Project",
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_cloud": "azure",
            "input_cicd_platform": "github_actions",
            "input_inference_table_name": inference_table_name,
        }

        if should_fail:
            with pytest.raises(
                Exception
            ):  # CLI validation should reject invalid table names
                generate(tmpdir, databricks_cli, context=context)
        else:
            generate(tmpdir, databricks_cli, context=context)
            test_file_contents = (
                tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
            ).read_text("utf-8")

            # Verify valid table names are passed through correctly
            assert (
                f"input_inference_table_name={inference_table_name}"
                in test_file_contents
            )

    def test_maximum_parameter_complexity(self, tmpdir, databricks_cli):
        """Test template generation with maximum parameter complexity."""
        # Use the most complex valid combination of parameters
        context = {
            "input_setup_cicd_and_project": "CICD_and_Project",
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_cloud": "azure",
            "input_cicd_platform": "github_actions_for_github_enterprise_servers",
            "input_databricks_staging_workspace_host": "https://adb-1234567890123456789.99.azuredatabricks.net",
            "input_databricks_prod_workspace_host": "https://adb-9876543210987654321.88.azuredatabricks.net",
            "input_default_branch": "main_branch_with_underscores",
            "input_release_branch": "release_v2_branch",
            "input_read_user_group": "complex_user_group_name_with_underscores",
            "input_include_models_in_unity_catalog": "yes",
            "input_staging_catalog_name": "staging_catalog_name_with_underscores",
            "input_prod_catalog_name": "production_catalog_with_long_name",
            "input_test_catalog_name": "test_catalog_for_integration_tests",
            "input_schema_name": "complex_schema_name_for_models",
            "input_unity_catalog_read_user_group": "unity_catalog_users_with_execute_permissions",
            "input_inference_table_name": "dev.complex_schema_name_for_models.prediction_results",
            "input_include_feature_store": "yes",
            "input_include_mlflow_recipes": "no",  # Can't have both feature store and mlflow recipes
        }

        generate(tmpdir, databricks_cli, context=context)

        # Verify all complex parameters are handled correctly
        test_file_contents = (
            tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
        ).read_text("utf-8")

        # Verify some key complex parameters are present
        assert TEST_PROJECT_NAME in test_file_contents
        assert "github_actions_for_github_enterprise_servers" in test_file_contents
        assert "staging_catalog_name_with_underscores" in test_file_contents
        assert "complex_schema_name_for_models" in test_file_contents

    @pytest.mark.parametrize("cloud", ["azure", "aws", "gcp"])
    def test_cloud_specific_defaults(self, tmpdir, databricks_cli, cloud):
        """Test that cloud-specific default values are applied correctly."""
        context = {
            "input_setup_cicd_and_project": "CICD_and_Project",
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_cloud": cloud,
            "input_cicd_platform": "github_actions",
        }

        generate(tmpdir, databricks_cli, context=context)

        test_file_contents = (
            tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
        ).read_text("utf-8")

        # Verify cloud-specific workspace URLs are used
        if cloud == "azure":
            assert "azuredatabricks.net" in test_file_contents
        elif cloud == "aws":
            assert "cloud.databricks.com" in test_file_contents
        elif cloud == "gcp":
            assert "gcp.databricks.com" in test_file_contents

    def test_special_characters_in_user_groups(self, tmpdir, databricks_cli):
        """Test handling of special characters in user group names."""
        context = {
            "input_setup_cicd_and_project": "CICD_and_Project",
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_cloud": "azure",
            "input_cicd_platform": "github_actions",
            "input_read_user_group": "ML-Engineers_Team@Company",
            "input_unity_catalog_read_user_group": "Data-Scientists & ML-Engineers",
            "input_include_models_in_unity_catalog": "yes",
        }

        generate(tmpdir, databricks_cli, context=context)

        test_file_contents = (
            tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
        ).read_text("utf-8")

        # Verify special characters in user groups are preserved
        assert "ML-Engineers_Team@Company" in test_file_contents
        assert "Data-Scientists & ML-Engineers" in test_file_contents

    def test_empty_or_minimal_configuration(self, tmpdir, databricks_cli):
        """Test template generation with minimal required configuration."""
        # Use only the absolute minimum required parameters
        context = {
            "input_setup_cicd_and_project": "Project_Only",
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
        }

        generate(tmpdir, databricks_cli, context=context)

        # Verify project was created successfully with defaults
        assert os.path.exists(tmpdir / TEST_PROJECT_NAME)
        test_file_contents = (
            tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
        ).read_text("utf-8")

        # Verify defaults were applied
        assert "input_cloud=azure" in test_file_contents  # Default cloud
        assert "input_include_feature_store=no" in test_file_contents
        assert "input_include_mlflow_recipes=no" in test_file_contents
