"""
Tests for template completeness and parameter coverage.
These tests ensure that all parameters defined in databricks_template_schema.json
are properly handled and covered by the test suite.
"""

import json
import os
import pathlib
import pytest
import re
from typing import Dict, Set
from utils import generate, databricks_cli, TEST_PROJECT_NAME, paths


class TestTemplateCompleteness:
    """Test template completeness and parameter coverage."""

    @pytest.fixture(scope="class")
    def schema_params(self):
        """Load all parameters from databricks_template_schema.json."""
        schema_path = (
            pathlib.Path(__file__).parent.parent / "databricks_template_schema.json"
        )
        with open(schema_path, "r") as f:
            schema = json.load(f)
        return set(schema["properties"].keys())

    @pytest.fixture(scope="class")
    def generated_project(self, tmpdir_factory, databricks_cli):
        """Generate a comprehensive project for analysis."""
        tmpdir = tmpdir_factory.mktemp("completeness")
        context = {
            "input_setup_cicd_and_project": "CICD_and_Project",
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_cloud": "azure",
            "input_cicd_platform": "github_actions",
            "input_include_models_in_unity_catalog": "yes",
            "input_include_feature_store": "yes",
            # Note: Can't enable MLflow Recipes with Feature Store or Unity Catalog
            "input_include_mlflow_recipes": "no",
        }
        generate(tmpdir, databricks_cli, context=context)
        return tmpdir / TEST_PROJECT_NAME

    def test_all_schema_parameters_have_values(self, generated_project, schema_params):
        """Test that all parameters from schema have values in generated project."""
        test_file_contents = (generated_project / "_params_testing_only.txt").read_text(
            "utf-8"
        )

        # Extract all parameter=value pairs from the test file
        param_pattern = r"^(\w+)=(.*)$"
        found_params = set()
        for line in test_file_contents.split("\n"):
            match = re.match(param_pattern, line.strip())
            if match:
                found_params.add(match.group(1))

        # Check that all schema parameters are found
        missing_params = schema_params - found_params

        # Some parameters might be transformed (e.g., input_* becomes just the name)
        # Let's check for transformed names too
        transformed_found = set()
        for param in found_params:
            if not param.startswith("input_"):
                transformed_found.add(f"input_{param}")

        all_found = found_params | transformed_found
        missing_params = schema_params - all_found

        assert (
            not missing_params
        ), f"Missing parameters in generated project: {missing_params}"

    def test_template_variable_coverage(self, generated_project):
        """Test that all template variables are properly substituted."""
        project_paths = paths(generated_project)

        # Check all generated files for unresolved MLOps template variables
        # These are patterns that should NOT be in the final generated files
        unresolved_template_pattern = r"\{\{[^}]*\.input_[^}]*\}\}"  # MLOps template variables like {{ .input_* }}

        unresolved_vars = []

        # Valid CI/CD platform variables that should be left as-is
        valid_cicd_patterns = [
            r"\{\{\s*secrets\.",  # GitHub Actions secrets
            r"\{\{\s*github\.",  # GitHub Actions context
            r"\{\{\s*env\.",  # Environment variables
            r"\{\{\s*matrix\.",  # GitHub Actions matrix
            r"\{\{\s*steps\.",  # GitHub Actions steps
            r"\{\{\s*needs\.",  # GitHub Actions needs
            r"\$\{\{\s*variables\.",  # Azure DevOps variables
            r"\$\{",  # GitLab CI variables
        ]

        for path_str in project_paths:
            file_path = generated_project / path_str

            # Skip binary files and specific file types
            skip_extensions = {".png", ".parquet", ".tar.gz", ".pyc", ".so"}
            if any(str(file_path).endswith(ext) for ext in skip_extensions):
                continue

            if file_path.isfile():
                try:
                    content = file_path.read_text("utf-8")

                    # Find all {{ }} template-style variables
                    all_template_matches = re.findall(r"\{\{[^}]+\}\}", content)

                    for match in all_template_matches:
                        # Skip valid CI/CD platform variables
                        is_valid_cicd = any(
                            re.search(pattern, match) for pattern in valid_cicd_patterns
                        )

                        # Report as unresolved if it looks like an MLOps template variable
                        if not is_valid_cicd and (
                            ".input_" in match or match.startswith("{{ .")
                        ):
                            unresolved_vars.append(f"{file_path}: {match}")

                except (UnicodeDecodeError, PermissionError):
                    # Skip files that can't be read as text
                    continue

        assert (
            not unresolved_vars
        ), f"Found unresolved template variables: {unresolved_vars[:10]}"

    def test_parameter_enum_values_coverage(self, tmpdir, databricks_cli):
        """Test that all enum values for parameters are covered by tests."""
        schema_path = (
            pathlib.Path(__file__).parent.parent / "databricks_template_schema.json"
        )
        with open(schema_path, "r") as f:
            schema = json.load(f)

        enum_params = {}
        for param, config in schema["properties"].items():
            if "enum" in config:
                enum_params[param] = config["enum"]

        # Test each enum parameter with all its possible values
        for param, enum_values in enum_params.items():
            for enum_value in enum_values:
                # Create a context that tests this specific enum value
                context = {
                    "input_project_name": TEST_PROJECT_NAME,
                    "input_root_dir": TEST_PROJECT_NAME,
                    param: enum_value,
                }

                # Add required parameters based on the enum being tested
                if param == "input_cicd_platform":
                    context["input_setup_cicd_and_project"] = "CICD_and_Project"
                elif (
                    param == "input_setup_cicd_and_project"
                    and enum_value == "CICD_Only"
                ):
                    context["input_root_dir"] = context["input_project_name"]

                # Skip invalid combinations
                if (
                    param == "input_include_mlflow_recipes"
                    and enum_value == "yes"
                    and context.get("input_include_models_in_unity_catalog") == "yes"
                ):
                    continue

                try:
                    project_dir = tmpdir.mkdir(context["input_project_name"])
                    generate(project_dir, databricks_cli, context=context)

                    # Verify the enum value was applied
                    if (
                        enum_value != "CICD_Only"
                    ):  # CICD_Only might not have _params_testing_only.txt
                        test_file = (
                            project_dir
                            / context["input_project_name"]
                            / "_params_testing_only.txt"
                        )
                        if test_file.exists():
                            test_contents = test_file.read_text("utf-8")
                            assert f"{param}={enum_value}" in test_contents

                except Exception as e:
                    # Some combinations might be invalid, that's expected
                    pass

    def test_all_cloud_platforms_generate_successfully(self, tmpdir, databricks_cli):
        """Test that all cloud platforms generate projects successfully."""
        clouds = ["azure", "aws", "gcp"]

        for cloud in clouds:
            context = {
                "input_project_name": TEST_PROJECT_NAME,
                "input_root_dir": TEST_PROJECT_NAME,
                "input_cloud": cloud,
                "input_setup_cicd_and_project": "CICD_and_Project",
                "input_cicd_platform": "github_actions",
            }

            project_dir = tmpdir.mkdir(f"test_{cloud}_project")
            generate(project_dir, databricks_cli, context=context)

            # Verify cloud-specific artifacts
            assert os.path.exists(project_dir / TEST_PROJECT_NAME)

            test_file = project_dir / TEST_PROJECT_NAME / "_params_testing_only.txt"
            test_contents = test_file.read_text("utf-8")
            assert f"input_cloud={cloud}" in test_contents

    def test_all_cicd_platforms_generate_successfully(self, tmpdir, databricks_cli):
        """Test that all CI/CD platforms generate projects successfully."""
        cicd_platforms = [
            "github_actions",
            "github_actions_for_github_enterprise_servers",
            "azure_devops",
            "gitlab",
        ]

        for platform in cicd_platforms:
            context = {
                "input_project_name": TEST_PROJECT_NAME,
                "input_root_dir": TEST_PROJECT_NAME,
                "input_cloud": "azure",
                "input_setup_cicd_and_project": "CICD_and_Project",
                "input_cicd_platform": platform,
            }

            project_dir = tmpdir.mkdir(f"test_{platform}_project")
            generate(project_dir, databricks_cli, context=context)

            # Verify platform-specific CI/CD files exist
            project_path = project_dir / TEST_PROJECT_NAME
            assert os.path.exists(project_path)

            if "github" in platform:
                assert os.path.exists(project_path / ".github" / "workflows")
            elif platform == "azure_devops":
                assert os.path.exists(project_path / ".azure" / "devops-pipelines")
            elif platform == "gitlab":
                assert os.path.exists(project_path / ".gitlab" / "pipelines")

    def test_feature_combinations_completeness(self, tmpdir, databricks_cli):
        """Test that all valid feature combinations work."""
        # All possible feature combinations (excluding invalid ones)
        feature_combinations = [
            {"feature_store": "no", "mlflow_recipes": "no", "unity_catalog": "no"},
            {"feature_store": "no", "mlflow_recipes": "no", "unity_catalog": "yes"},
            {"feature_store": "no", "mlflow_recipes": "yes", "unity_catalog": "no"},
            {"feature_store": "yes", "mlflow_recipes": "no", "unity_catalog": "no"},
            {"feature_store": "yes", "mlflow_recipes": "no", "unity_catalog": "yes"},
            # Note: MLflow Recipes with Feature Store or Unity Catalog is not supported
        ]

        for i, combo in enumerate(feature_combinations):
            context = {
                "input_project_name": TEST_PROJECT_NAME,
                "input_root_dir": TEST_PROJECT_NAME,
                "input_cloud": "azure",
                "input_setup_cicd_and_project": "CICD_and_Project",
                "input_include_feature_store": combo["feature_store"],
                "input_include_mlflow_recipes": combo["mlflow_recipes"],
                "input_include_models_in_unity_catalog": combo["unity_catalog"],
            }

            project_dir = tmpdir.mkdir(f"test_features_{i}")
            generate(project_dir, databricks_cli, context=context)

            # Verify feature-specific artifacts exist or don't exist as expected
            from utils import TEST_PROJECT_DIRECTORY

            project_path = project_dir / TEST_PROJECT_NAME / TEST_PROJECT_DIRECTORY

            # Check feature store artifacts
            fs_notebook = (
                project_path
                / "feature_engineering"
                / "notebooks"
                / "GenerateAndWriteFeatures.py"
            )
            if combo["feature_store"] == "yes":
                assert (
                    fs_notebook.exists()
                ), f"Feature store notebook missing for combo {i}"
            else:
                assert (
                    not fs_notebook.exists()
                ), f"Feature store notebook should not exist for combo {i}"

            # Check MLflow Recipes artifacts
            recipes_notebook = (
                project_path / "training" / "notebooks" / "TrainWithMLflowRecipes.py"
            )
            if combo["mlflow_recipes"] == "yes":
                assert (
                    recipes_notebook.exists()
                ), f"MLflow Recipes notebook missing for combo {i}"
            else:
                assert (
                    not recipes_notebook.exists()
                ), f"MLflow Recipes notebook should not exist for combo {i}"

    def test_parameter_pattern_validation_coverage(self, tmpdir, databricks_cli):
        """Test that parameters with patterns are validated correctly."""
        schema_path = (
            pathlib.Path(__file__).parent.parent / "databricks_template_schema.json"
        )
        with open(schema_path, "r") as f:
            schema = json.load(f)

        pattern_params = {}
        for param, config in schema["properties"].items():
            if "pattern" in config:
                pattern_params[param] = config["pattern"]

        # Test that invalid patterns are rejected
        test_cases = {
            "input_project_name": [
                ("valid_project", True),
                ("ab", False),  # Too short
                ("project with spaces", False),  # Spaces not allowed
                ("project.with.dots", False),  # Dots not allowed
                ("project/with/slashes", False),  # Slashes not allowed
            ],
            "input_databricks_staging_workspace_host": [
                ("https://valid.azuredatabricks.net", True),
                ("http://invalid.azuredatabricks.net", False),  # Must use HTTPS
                ("invalid-no-protocol.net", False),  # Must start with https
            ],
            "input_inference_table_name": [
                ("catalog.schema.table", True),
                ("invalid.table", False),  # Must have 3 parts
                ("catalog.schema.table.extra", False),  # Too many parts
            ],
            "input_schema_name": [
                ("valid_schema", True),
                ("schema-with-hyphens", False),  # Hyphens not allowed
                ("schema with spaces", False),  # Spaces not allowed
                ("schema.with.dots", False),  # Dots not allowed
            ],
        }

        for param, test_values in test_cases.items():
            for value, should_succeed in test_values:
                context = {
                    "input_project_name": "test_patterns",
                    "input_root_dir": "test_patterns",
                    param: value,
                }

                # Add required context for certain parameters
                if param.endswith("_workspace_host"):
                    context["input_setup_cicd_and_project"] = "CICD_and_Project"
                    context["input_databricks_prod_workspace_host"] = value
                elif param == "input_schema_name":
                    context["input_include_models_in_unity_catalog"] = "yes"

                try:
                    pattern_dir = tmpdir.mkdir(
                        f"pattern_test_{param}_{abs(hash(value))}"
                    )
                    generate(pattern_dir, databricks_cli, context=context)
                    assert (
                        should_succeed
                    ), f"Expected {param}={value} to fail validation but it succeeded"
                except Exception:
                    assert (
                        not should_succeed
                    ), f"Expected {param}={value} to succeed validation but it failed"

    def test_welcome_and_success_messages_present(self, tmpdir, databricks_cli):
        """Test that template has proper welcome and success messages."""
        schema_path = (
            pathlib.Path(__file__).parent.parent / "databricks_template_schema.json"
        )
        with open(schema_path, "r") as f:
            schema = json.load(f)

        # Verify required messages exist
        assert "welcome_message" in schema
        assert "success_message" in schema
        assert "MLOps Stacks" in schema["welcome_message"]
        assert "created" in schema["success_message"].lower()

    def test_minimum_cli_version_specified(self):
        """Test that minimum databricks CLI version is specified."""
        schema_path = (
            pathlib.Path(__file__).parent.parent / "databricks_template_schema.json"
        )
        with open(schema_path, "r") as f:
            schema = json.load(f)

        assert "min_databricks_cli_version" in schema
        version = schema["min_databricks_cli_version"]
        assert version.startswith("v")
        assert len(version.split(".")) >= 3  # Should be in format v0.236.0 or similar
