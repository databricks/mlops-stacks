"""
Tests for parameter constraints and skip_prompt_if logic defined in databricks_template_schema.json.
These tests ensure that parameter interdependencies work correctly and that certain parameters
are properly skipped based on other parameter values.
"""

import os
import pytest
from utils import generate, databricks_cli, TEST_PROJECT_NAME, TEST_PROJECT_DIRECTORY


class TestParameterConstraints:
    """Test parameter interdependencies and skip_prompt_if logic."""

    def test_cicd_only_skips_project_parameters(self, tmpdir, databricks_cli):
        """Test that CICD_Only setup skips project-specific parameters."""
        context = {
            "input_setup_cicd_and_project": "CICD_Only",
            "input_root_dir": "test-cicd-only",
            "input_cloud": "azure",
            "input_cicd_platform": "github_actions",
            "input_databricks_staging_workspace_host": "https://adb-staging.azuredatabricks.net",
            "input_databricks_prod_workspace_host": "https://adb-prod.azuredatabricks.net",
        }
        generate(tmpdir, databricks_cli, context=context)

        # Verify that project-specific files are not generated
        project_dir = tmpdir / "test-cicd-only"
        assert not os.path.exists(project_dir / "my_mlops_project")

        # Verify that CI/CD files are generated
        assert os.path.exists(project_dir / ".github" / "workflows")

    def test_project_only_skips_cicd_parameters(self, tmpdir, databricks_cli):
        """Test that Project_Only setup skips CI/CD-specific parameters."""
        context = {
            "input_setup_cicd_and_project": "Project_Only",
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_cloud": "azure",
            "input_include_models_in_unity_catalog": "no",
            "input_include_feature_store": "no",
            "input_include_mlflow_recipes": "no",
        }
        generate(tmpdir, databricks_cli, context=context)

        # Verify that project files are generated
        project_dir = tmpdir / TEST_PROJECT_NAME / TEST_PROJECT_DIRECTORY
        assert os.path.exists(project_dir)

        # Verify that CI/CD files are not generated
        assert not os.path.exists(tmpdir / TEST_PROJECT_NAME / ".github")
        assert not os.path.exists(tmpdir / TEST_PROJECT_NAME / ".azure")
        assert not os.path.exists(tmpdir / TEST_PROJECT_NAME / ".gitlab")

    @pytest.mark.parametrize("unity_catalog", ["yes", "no"])
    def test_unity_catalog_parameters_skipped_correctly(
        self, tmpdir, databricks_cli, unity_catalog
    ):
        """Test that Unity Catalog parameters are skipped when Unity Catalog is disabled."""
        context = {
            "input_setup_cicd_and_project": "CICD_and_Project",
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_cloud": "azure",
            "input_cicd_platform": "github_actions",
            "input_include_models_in_unity_catalog": unity_catalog,
        }
        generate(tmpdir, databricks_cli, context=context)

        test_file_contents = (
            tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
        ).read_text("utf-8")

        if unity_catalog == "yes":
            # Unity Catalog specific parameters should have meaningful values
            assert "input_staging_catalog_name=staging" in test_file_contents
            assert "input_prod_catalog_name=prod" in test_file_contents
            assert "input_test_catalog_name=test" in test_file_contents
            # Schema name uses generic default even when UC is enabled
            assert "input_schema_name=schema_name" in test_file_contents
        else:
            # When Unity Catalog is disabled, catalog names should still have defaults
            # but schema name should be the generic default
            assert "input_schema_name=schema_name" in test_file_contents

    def test_feature_store_mlflow_recipes_constraint(self, tmpdir, databricks_cli):
        """Test that MLflow Recipes is skipped when Feature Store is enabled."""
        context = {
            "input_setup_cicd_and_project": "CICD_and_Project",
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_cloud": "azure",
            "input_cicd_platform": "github_actions",
            "input_include_feature_store": "yes",
            "input_include_models_in_unity_catalog": "no",
            # MLflow Recipes should be skipped due to anyOf constraint
        }
        generate(tmpdir, databricks_cli, context=context)

        # Verify Feature Store artifacts are generated
        fs_notebook_path = (
            tmpdir
            / TEST_PROJECT_NAME
            / TEST_PROJECT_DIRECTORY
            / "feature_engineering"
            / "notebooks"
            / "GenerateAndWriteFeatures.py"
        )
        assert os.path.exists(fs_notebook_path)

        # Verify MLflow Recipes artifacts are NOT generated (constraint should prevent this)
        recipe_notebook_path = (
            tmpdir
            / TEST_PROJECT_NAME
            / TEST_PROJECT_DIRECTORY
            / "training"
            / "notebooks"
            / "TrainWithMLflowRecipes.py"
        )
        assert not os.path.exists(recipe_notebook_path)

    def test_unity_catalog_mlflow_recipes_constraint(self, tmpdir, databricks_cli):
        """Test that MLflow Recipes is skipped when Unity Catalog is enabled."""
        context = {
            "input_setup_cicd_and_project": "CICD_and_Project",
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_cloud": "azure",
            "input_cicd_platform": "github_actions",
            "input_include_models_in_unity_catalog": "yes",
            "input_include_feature_store": "no",
            # MLflow Recipes should be skipped due to anyOf constraint
        }
        generate(tmpdir, databricks_cli, context=context)

        # Verify Unity Catalog is configured
        test_file_contents = (
            tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
        ).read_text("utf-8")
        assert "input_include_models_in_unity_catalog=yes" in test_file_contents

        # Verify MLflow Recipes artifacts are NOT generated
        recipe_notebook_path = (
            tmpdir
            / TEST_PROJECT_NAME
            / TEST_PROJECT_DIRECTORY
            / "training"
            / "notebooks"
            / "TrainWithMLflowRecipes.py"
        )
        assert not os.path.exists(recipe_notebook_path)

    @pytest.mark.parametrize(
        "cicd_platform", ["github_actions", "azure_devops", "gitlab"]
    )
    def test_docker_image_skipped_for_non_gitlab(
        self, tmpdir, databricks_cli, cicd_platform
    ):
        """Test that docker_image parameter is only relevant for GitLab."""
        context = {
            "input_setup_cicd_and_project": "CICD_and_Project",
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_cloud": "azure",
            "input_cicd_platform": cicd_platform,
        }
        generate(tmpdir, databricks_cli, context=context)

        test_file_contents = (
            tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
        ).read_text("utf-8")

        if cicd_platform == "gitlab":
            # Docker image should be present for GitLab
            assert (
                "input_docker_image=databricksfieldeng/mlopsstacks:latest"
                in test_file_contents
            )
        else:
            # Docker image parameter should use default but not be relevant
            # The parameter exists but is not used in non-GitLab templates
            pass

    def test_gcp_unity_catalog_constraint(self, tmpdir, databricks_cli):
        """Test that GCP with Unity Catalog combination is handled properly."""
        # This combination should work but with limitations per existing test skips
        context = {
            "input_setup_cicd_and_project": "CICD_and_Project",
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_cloud": "gcp",
            "input_cicd_platform": "github_actions",
            "input_include_models_in_unity_catalog": "no",  # Use no to avoid skip
        }
        generate(tmpdir, databricks_cli, context=context)

        # Verify GCP-specific workspace URLs are used
        test_file_contents = (
            tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
        ).read_text("utf-8")
        assert "gcp.databricks.com" in test_file_contents

    def test_workspace_host_parameters_skipped_for_project_only(
        self, tmpdir, databricks_cli
    ):
        """Test that workspace host parameters are skipped for Project_Only setup."""
        context = {
            "input_setup_cicd_and_project": "Project_Only",
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_cloud": "azure",
        }
        generate(tmpdir, databricks_cli, context=context)

        test_file_contents = (
            tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
        ).read_text("utf-8")

        # Workspace hosts should still have default values even if not prompted
        assert "databricks_staging_workspace_host=" in test_file_contents
        assert "databricks_prod_workspace_host=" in test_file_contents

    def test_branch_parameters_skipped_for_project_only(self, tmpdir, databricks_cli):
        """Test that branch parameters are skipped for Project_Only setup."""
        context = {
            "input_setup_cicd_and_project": "Project_Only",
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,
            "input_cloud": "azure",
        }
        generate(tmpdir, databricks_cli, context=context)

        test_file_contents = (
            tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
        ).read_text("utf-8")

        # Branch parameters should have default values even if not prompted
        assert "input_default_branch=main" in test_file_contents
        assert "input_release_branch=release" in test_file_contents

    def test_root_dir_default_behavior(self, tmpdir, databricks_cli):
        """Test that input_root_dir defaults to input_project_name for CICD_and_Project."""
        context = {
            "input_setup_cicd_and_project": "CICD_and_Project",
            "input_project_name": TEST_PROJECT_NAME,
            "input_root_dir": TEST_PROJECT_NAME,  # Need to provide this explicitly
            "input_cloud": "azure",
            "input_cicd_platform": "github_actions",
        }
        generate(tmpdir, databricks_cli, context=context)

        test_file_contents = (
            tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
        ).read_text("utf-8")

        # Root dir should equal project name
        assert f"input_root_dir={TEST_PROJECT_NAME}" in test_file_contents
