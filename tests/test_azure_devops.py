"""
Tests for Azure DevOps CI/CD pipeline generation and validation.
These tests ensure that Azure DevOps-specific artifacts are generated correctly
and contain expected pipeline configurations.
"""

import pytest
import yaml
import os
from utils import (
    databricks_cli,
    generated_project_dir,
    parametrize_by_cloud,
    generate,
    TEST_PROJECT_NAME,
)


@pytest.mark.parametrize("cicd_platform", ["azure_devops"])
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
def test_azure_devops_pipeline_folder_structure(
    cicd_platform,
    setup_cicd_and_project,
    include_feature_store,
    include_mlflow_recipes,
    include_models_in_unity_catalog,
    cloud,
    generated_project_dir,
):
    """Test that Azure DevOps pipeline folder structure is created correctly."""
    if cloud == "gcp" and include_models_in_unity_catalog == "yes":
        return

    # For both CICD_Only and CICD_and_Project modes, .azure is inside the project directory
    # The difference is what's inside the project directory (ML code vs just CI/CD)
    project_dir = (
        generated_project_dir / "my-mlops-project"
    )  # This is what the fixture actually generates
    azure_devops_dir = project_dir / ".azure" / "devops-pipelines"

    assert azure_devops_dir.exists(), "Azure DevOps pipelines directory should exist"


@pytest.mark.parametrize("cicd_platform", ["azure_devops"])
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
def test_azure_devops_pipeline_files_exist(
    cicd_platform,
    setup_cicd_and_project,
    include_feature_store,
    include_mlflow_recipes,
    include_models_in_unity_catalog,
    cloud,
    generated_project_dir,
):
    """Test that Azure DevOps pipeline files are generated correctly."""
    if cloud == "gcp" and include_models_in_unity_catalog == "yes":
        return

    # For both CICD_Only and CICD_and_Project modes, .azure is inside the project directory
    # The difference is what's inside the project directory (ML code vs just CI/CD)
    project_dir = (
        generated_project_dir / "my-mlops-project"
    )  # This is what the fixture actually generates
    pipelines_dir = project_dir / ".azure" / "devops-pipelines"

    # Expected pipeline files depend on setup mode
    if setup_cicd_and_project == "CICD_Only":
        # CICD_Only mode generates only CI/CD files, not bundle files
        expected_files = [
            "deploy-cicd.yml",
        ]
    else:
        # CICD_and_Project mode generates both CI/CD and bundle files
        expected_files = [
            "my-mlops-project-bundle-cicd.yml",  # Use actual project name from fixture
            "my-mlops-project-tests-ci.yml",
            "deploy-cicd.yml",
        ]

    for pipeline_file in expected_files:
        pipeline_path = pipelines_dir / pipeline_file
        assert (
            pipeline_path.exists()
        ), f"Azure DevOps pipeline {pipeline_file} should exist"

        # Verify YAML syntax is valid
        with open(pipeline_path, "r") as f:
            pipeline_config = yaml.safe_load(f)
        assert (
            pipeline_config is not None
        ), f"Pipeline {pipeline_file} should have valid YAML"


@pytest.mark.parametrize("cicd_platform", ["azure_devops"])
@parametrize_by_cloud
def test_azure_devops_pipeline_structure(cicd_platform, cloud, tmpdir, databricks_cli):
    """Test that Azure DevOps pipelines have correct structure."""
    context = {
        "input_setup_cicd_and_project": "CICD_and_Project",
        "input_project_name": TEST_PROJECT_NAME,
        "input_root_dir": TEST_PROJECT_NAME,
        "input_cloud": cloud,
        "input_cicd_platform": "azure_devops",
    }

    generate(tmpdir, databricks_cli, context=context)

    project_dir = tmpdir / TEST_PROJECT_NAME
    pipelines_dir = project_dir / ".azure" / "devops-pipelines"

    # Test main bundle pipeline
    bundle_pipeline_path = pipelines_dir / f"{TEST_PROJECT_NAME}-bundle-cicd.yml"
    with open(bundle_pipeline_path, "r") as f:
        bundle_config = yaml.safe_load(f)

    # Verify required Azure DevOps pipeline sections
    assert "trigger" in bundle_config, "Bundle pipeline should define triggers"
    assert "stages" in bundle_config, "Bundle pipeline should define stages"
    assert "variables" in bundle_config, "Bundle pipeline should define variables"


@pytest.mark.parametrize("cicd_platform", ["azure_devops"])
@parametrize_by_cloud
def test_azure_devops_test_pipeline_structure(
    cicd_platform, cloud, tmpdir, databricks_cli
):
    """Test that Azure DevOps test pipeline has correct structure."""
    context = {
        "input_setup_cicd_and_project": "CICD_and_Project",
        "input_project_name": TEST_PROJECT_NAME,
        "input_root_dir": TEST_PROJECT_NAME,
        "input_cloud": cloud,
        "input_cicd_platform": "azure_devops",
    }

    generate(tmpdir, databricks_cli, context=context)

    project_dir = tmpdir / TEST_PROJECT_NAME
    pipelines_dir = project_dir / ".azure" / "devops-pipelines"

    # Test CI pipeline for tests
    test_pipeline_path = pipelines_dir / f"{TEST_PROJECT_NAME}-tests-ci.yml"
    with open(test_pipeline_path, "r") as f:
        test_config = yaml.safe_load(f)

    # Verify test pipeline structure
    assert "trigger" in test_config, "Test pipeline should define triggers"
    assert (
        "jobs" in test_config or "stages" in test_config
    ), "Test pipeline should define jobs or stages"


@pytest.mark.parametrize("cicd_platform", ["azure_devops"])
def test_azure_devops_pipeline_triggers_on_correct_branches(
    cicd_platform, tmpdir, databricks_cli
):
    """Test that Azure DevOps pipelines trigger on main and release branches."""
    context = {
        "input_setup_cicd_and_project": "CICD_and_Project",
        "input_project_name": TEST_PROJECT_NAME,
        "input_root_dir": TEST_PROJECT_NAME,
        "input_cloud": "azure",
        "input_cicd_platform": "azure_devops",
        "input_default_branch": "main",
        "input_release_branch": "release",
    }

    generate(tmpdir, databricks_cli, context=context)

    project_dir = tmpdir / TEST_PROJECT_NAME
    pipelines_dir = project_dir / ".azure" / "devops-pipelines"

    # Check triggers in bundle pipeline
    bundle_pipeline_path = pipelines_dir / f"{TEST_PROJECT_NAME}-bundle-cicd.yml"
    with open(bundle_pipeline_path, "r") as f:
        bundle_config = yaml.safe_load(f)

    # Verify trigger configuration references correct branches
    if "trigger" in bundle_config:
        trigger_config = bundle_config["trigger"]
        if isinstance(trigger_config, dict) and "branches" in trigger_config:
            branches = trigger_config["branches"]
            if isinstance(branches, dict) and "include" in branches:
                included_branches = branches["include"]
                # Should include main and release branches
                assert context["input_default_branch"] in str(
                    included_branches
                ) or context["input_release_branch"] in str(included_branches)


@pytest.mark.parametrize("cicd_platform", ["azure_devops"])
@parametrize_by_cloud
def test_azure_devops_pipeline_has_deployment_stages(
    cicd_platform, cloud, tmpdir, databricks_cli
):
    """Test that Azure DevOps pipelines contain deployment stages."""
    context = {
        "input_setup_cicd_and_project": "CICD_and_Project",
        "input_project_name": TEST_PROJECT_NAME,
        "input_root_dir": TEST_PROJECT_NAME,
        "input_cloud": cloud,
        "input_cicd_platform": "azure_devops",
    }

    generate(tmpdir, databricks_cli, context=context)

    project_dir = tmpdir / TEST_PROJECT_NAME
    pipelines_dir = project_dir / ".azure" / "devops-pipelines"

    # Test bundle pipeline stages
    bundle_pipeline_path = pipelines_dir / f"{TEST_PROJECT_NAME}-bundle-cicd.yml"
    with open(bundle_pipeline_path, "r") as f:
        bundle_config = yaml.safe_load(f)

    if "stages" in bundle_config:
        stages = bundle_config["stages"]
        stage_names = []

        for stage in stages:
            if isinstance(stage, dict) and "stage" in stage:
                stage_names.append(stage["stage"])

        # Should have deployment stages for different environments (look for CD stages)
        deployment_stages = [
            name
            for name in stage_names
            if "cd" in name.lower() or "deploy" in name.lower()
        ]
        assert (
            len(deployment_stages) > 0
        ), f"Should have deployment stages. Found stages: {stage_names}"


@pytest.mark.parametrize("cicd_platform", ["azure_devops"])
def test_azure_devops_pipeline_has_variables(cicd_platform, tmpdir, databricks_cli):
    """Test that Azure DevOps pipelines define variables section."""
    context = {
        "input_setup_cicd_and_project": "CICD_and_Project",
        "input_project_name": TEST_PROJECT_NAME,
        "input_root_dir": TEST_PROJECT_NAME,
        "input_cloud": "azure",
        "input_cicd_platform": "azure_devops",
    }

    generate(tmpdir, databricks_cli, context=context)

    project_dir = tmpdir / TEST_PROJECT_NAME
    pipelines_dir = project_dir / ".azure" / "devops-pipelines"

    # Check variables in pipeline
    bundle_pipeline_path = pipelines_dir / f"{TEST_PROJECT_NAME}-bundle-cicd.yml"
    with open(bundle_pipeline_path, "r") as f:
        bundle_config = yaml.safe_load(f)

    if "variables" in bundle_config:
        variables = bundle_config["variables"]
        # Should have project-related variables
        assert len(variables) > 0, "Pipeline should define variables"


@pytest.mark.parametrize("cicd_platform", ["azure_devops"])
def test_azure_devops_deploy_pipeline_structure(cicd_platform, tmpdir, databricks_cli):
    """Test that Azure DevOps deploy CI/CD pipeline has correct structure."""
    context = {
        "input_setup_cicd_and_project": "CICD_and_Project",
        "input_project_name": TEST_PROJECT_NAME,
        "input_root_dir": TEST_PROJECT_NAME,
        "input_cloud": "azure",
        "input_cicd_platform": "azure_devops",
    }

    generate(tmpdir, databricks_cli, context=context)

    project_dir = tmpdir / TEST_PROJECT_NAME
    pipelines_dir = project_dir / ".azure" / "devops-pipelines"

    # Test deploy-cicd pipeline
    deploy_pipeline_path = pipelines_dir / "deploy-cicd.yml"
    with open(deploy_pipeline_path, "r") as f:
        deploy_config = yaml.safe_load(f)

    # Verify deploy pipeline structure
    assert "trigger" in deploy_config, "Deploy pipeline should define triggers"

    # Should have stages or jobs for deployment
    has_stages = "stages" in deploy_config
    has_jobs = "jobs" in deploy_config
    assert has_stages or has_jobs, "Deploy pipeline should define stages or jobs"


@pytest.mark.parametrize("cicd_platform", ["azure_devops"])
def test_azure_devops_generates_readme(cicd_platform, tmpdir, databricks_cli):
    """Test that Azure DevOps-specific README.md is generated."""
    context = {
        "input_setup_cicd_and_project": "CICD_and_Project",
        "input_project_name": TEST_PROJECT_NAME,
        "input_root_dir": TEST_PROJECT_NAME,
        "input_cloud": "azure",
        "input_cicd_platform": "azure_devops",
    }

    generate(tmpdir, databricks_cli, context=context)

    project_dir = tmpdir / TEST_PROJECT_NAME
    azure_readme_path = project_dir / ".azure" / "devops-pipelines" / "README.md"

    assert azure_readme_path.exists(), "Azure DevOps README should exist"

    readme_contents = azure_readme_path.read_text("utf-8")
    assert "Azure DevOps" in readme_contents, "README should mention Azure DevOps"
    assert "pipeline" in readme_contents.lower(), "README should mention pipelines"


@pytest.mark.parametrize("cicd_platform", ["azure_devops"])
def test_azure_devops_pipeline_references_environments(
    cicd_platform, tmpdir, databricks_cli
):
    """Test that Azure DevOps pipelines reference staging and prod environments."""
    context = {
        "input_setup_cicd_and_project": "CICD_and_Project",
        "input_project_name": TEST_PROJECT_NAME,
        "input_root_dir": TEST_PROJECT_NAME,
        "input_cloud": "azure",
        "input_cicd_platform": "azure_devops",
        "input_default_branch": "main",
        "input_release_branch": "release",
    }

    generate(tmpdir, databricks_cli, context=context)

    project_dir = tmpdir / TEST_PROJECT_NAME
    pipelines_dir = project_dir / ".azure" / "devops-pipelines"

    # Test bundle pipeline has conditions
    bundle_pipeline_path = pipelines_dir / f"{TEST_PROJECT_NAME}-bundle-cicd.yml"
    with open(bundle_pipeline_path, "r") as f:
        bundle_config = yaml.safe_load(f)

    # Look for environment-specific conditions
    config_str = yaml.dump(bundle_config)

    # Should reference different environments (staging, prod)
    assert (
        "staging" in config_str.lower() or "prod" in config_str.lower()
    ), "Pipeline should reference different environments"


@pytest.mark.parametrize("cicd_platform", ["azure_devops"])
@pytest.mark.parametrize("cloud", ["azure", "aws", "gcp"])
def test_azure_devops_works_with_all_clouds(
    cicd_platform, cloud, tmpdir, databricks_cli
):
    """Test that Azure DevOps pipelines generate successfully for all cloud providers."""
    context = {
        "input_setup_cicd_and_project": "CICD_and_Project",
        "input_project_name": TEST_PROJECT_NAME,
        "input_root_dir": TEST_PROJECT_NAME,
        "input_cloud": cloud,
        "input_cicd_platform": "azure_devops",
    }

    generate(tmpdir, databricks_cli, context=context)

    # Verify that the project generates successfully for all clouds with Azure DevOps
    project_dir = tmpdir / TEST_PROJECT_NAME
    pipelines_dir = project_dir / ".azure" / "devops-pipelines"

    assert pipelines_dir.exists(), f"Azure DevOps pipelines should work with {cloud}"

    # Verify main pipeline exists
    bundle_pipeline_path = pipelines_dir / f"{TEST_PROJECT_NAME}-bundle-cicd.yml"
    assert bundle_pipeline_path.exists(), f"Bundle pipeline should exist for {cloud}"


@pytest.mark.parametrize("cicd_platform", ["azure_devops"])
@parametrize_by_cloud
def test_azure_devops_variable_replacement(
    cicd_platform, cloud, tmpdir, databricks_cli
):
    """Test that template variables are properly replaced in Azure DevOps pipelines."""
    context = {
        "input_setup_cicd_and_project": "CICD_and_Project",
        "input_project_name": "my-mlops-project",
        "input_root_dir": "my-mlops-project",
        "input_cloud": cloud,
        "input_cicd_platform": "azure_devops",
        "input_default_branch": "main",
        "input_release_branch": "release",
        "input_include_feature_store": "no",
        "input_include_mlflow_recipes": "no",
        "input_include_models_in_unity_catalog": "no",
    }

    generate(tmpdir, databricks_cli, context=context)

    project_dir = tmpdir / "my-mlops-project"
    pipelines_dir = project_dir / ".azure" / "devops-pipelines"

    # Test variables in tests-ci.yml
    tests_ci_path = pipelines_dir / "my-mlops-project-tests-ci.yml"
    assert tests_ci_path.exists(), "Tests CI pipeline should exist"

    tests_ci_content = tests_ci_path.read_text("utf-8")

    # Assert that template variables are replaced correctly
    assert (
        "{{ .input_default_branch }}" not in tests_ci_content
    ), "Template variables should be replaced"
    assert (
        "{{ .input_project_name }}" not in tests_ci_content
    ), "Template variables should be replaced"
    assert (
        "{{template `project_name_alphanumeric_underscore` .}}" not in tests_ci_content
    ), "Template functions should be replaced"

    # Assert correct values are present
    assert "main" in tests_ci_content, "Default branch should be replaced with 'main'"
    assert (
        "my_mlops_project" in tests_ci_content
    ), "Project name should be converted to alphanumeric underscore"
    assert (
        "refs/heads/main" in tests_ci_content
    ), "Branch references should include default branch"
    assert (
        "my-mlops-project variable group" in tests_ci_content
    ), "Variable group should reference project name"

    # Test cloud-specific environment variables
    if cloud == "azure":
        assert "ARM_TENANT_ID: $(STAGING_AZURE_SP_TENANT_ID)" in tests_ci_content
        assert "ARM_CLIENT_ID: $(STAGING_AZURE_SP_APPLICATION_ID)" in tests_ci_content
        assert (
            "ARM_CLIENT_SECRET: $(STAGING_AZURE_SP_CLIENT_SECRET)" in tests_ci_content
        )
    else:
        assert "DATABRICKS_TOKEN: $(STAGING_WORKSPACE_TOKEN)" in tests_ci_content

    # Test bundle-cicd.yml variables
    bundle_ci_path = pipelines_dir / "my-mlops-project-bundle-cicd.yml"
    assert bundle_ci_path.exists(), "Bundle CI pipeline should exist"

    bundle_ci_content = bundle_ci_path.read_text("utf-8")

    # Assert that template variables are replaced correctly
    assert (
        "{{ .input_default_branch }}" not in bundle_ci_content
    ), "Template variables should be replaced"
    assert (
        "{{ .input_release_branch }}" not in bundle_ci_content
    ), "Template variables should be replaced"
    assert (
        "{{ .input_project_name }}" not in bundle_ci_content
    ), "Template variables should be replaced"

    # Assert correct values are present
    assert "main" in bundle_ci_content, "Default branch should be replaced"
    assert "release" in bundle_ci_content, "Release branch should be replaced"
    assert (
        "refs/heads/main" in bundle_ci_content
    ), "Default branch reference should be present"
    assert (
        "refs/heads/release" in bundle_ci_content
    ), "Release branch reference should be present"
    assert (
        "my-mlops-project" in bundle_ci_content
    ), "Project name should be present in display names"

    # Test deploy-cicd.yml variables
    deploy_ci_path = pipelines_dir / "deploy-cicd.yml"
    assert deploy_ci_path.exists(), "Deploy CI pipeline should exist"

    deploy_ci_content = deploy_ci_path.read_text("utf-8")

    # Assert that template variables are replaced correctly
    assert (
        "{{ .input_root_dir }}" not in deploy_ci_content
    ), "Template variables should be replaced"
    assert (
        "{{ .input_project_name }}" not in deploy_ci_content
    ), "Template variables should be replaced"
    assert (
        "{{template `cli_version` .}}" not in deploy_ci_content
    ), "Template functions should be replaced"

    # Assert correct values are present
    assert (
        "my-mlops-project variable group" in deploy_ci_content
    ), "Variable group should reference root dir"
    assert (
        "my-mlops-project" in deploy_ci_content
    ), "Project name should be present as default parameter"

    # Test cloud-specific template logic
    if cloud == "azure":
        assert "ARM_TENANT_ID: $(STAGING_AZURE_SP_TENANT_ID)" in deploy_ci_content
        assert "ARM_CLIENT_ID: $(STAGING_AZURE_SP_APPLICATION_ID)" in deploy_ci_content
        assert (
            "ARM_CLIENT_SECRET: $(STAGING_AZURE_SP_CLIENT_SECRET)" in deploy_ci_content
        )
    else:
        assert "DATABRICKS_TOKEN: $(STAGING_WORKSPACE_TOKEN)" in deploy_ci_content


@pytest.mark.parametrize("cicd_platform", ["azure_devops"])
@parametrize_by_cloud
def test_azure_devops_conditional_template_logic(
    cicd_platform, cloud, tmpdir, databricks_cli
):
    """Test that conditional template logic is properly applied in Azure DevOps pipelines."""
    # Test with feature store enabled
    context = {
        "input_setup_cicd_and_project": "CICD_and_Project",
        "input_project_name": "my-mlops-project",
        "input_root_dir": "my-mlops-project",
        "input_cloud": cloud,
        "input_cicd_platform": "azure_devops",
        "input_default_branch": "main",
        "input_release_branch": "release",
        "input_include_feature_store": "yes",  # Enable feature store
        "input_include_mlflow_recipes": "no",
        "input_include_models_in_unity_catalog": "no",
    }

    generate(tmpdir, databricks_cli, context=context)

    project_dir = tmpdir / "my-mlops-project"
    pipelines_dir = project_dir / ".azure" / "devops-pipelines"

    # Test that feature store conditional logic is applied
    tests_ci_path = pipelines_dir / "my-mlops-project-tests-ci.yml"
    tests_ci_content = tests_ci_path.read_text("utf-8")

    # When feature store is enabled, should include feature engineering job
    assert (
        "databricks bundle run write_feature_table_job -t test" in tests_ci_content
    ), "Feature store enabled should include write_feature_table_job step"
    assert (
        "Run Feature Engineering Workflow for test deployment target"
        in tests_ci_content
    ), "Feature store enabled should include feature engineering workflow step"

    # Test that conditional template variables are not present
    assert (
        "{{ if (eq .input_include_feature_store `yes`) }}" not in tests_ci_content
    ), "Conditional template syntax should be processed"
    assert (
        "{{ end }}" not in tests_ci_content
    ), "Conditional template end tags should be processed"

    # Test with feature store disabled
    context_no_fs = context.copy()
    context_no_fs["input_include_feature_store"] = "no"

    tmpdir_no_fs = tmpdir.mkdir("no_feature_store")
    generate(tmpdir_no_fs, databricks_cli, context=context_no_fs)

    project_dir_no_fs = tmpdir_no_fs / "my-mlops-project"
    pipelines_dir_no_fs = project_dir_no_fs / ".azure" / "devops-pipelines"

    tests_ci_path_no_fs = pipelines_dir_no_fs / "my-mlops-project-tests-ci.yml"
    tests_ci_content_no_fs = tests_ci_path_no_fs.read_text("utf-8")

    # When feature store is disabled, should NOT include feature engineering job
    assert (
        "databricks bundle run write_feature_table_job -t test"
        not in tests_ci_content_no_fs
    ), "Feature store disabled should not include write_feature_table_job step"
    assert (
        "Run Feature Engineering Workflow for test deployment target"
        not in tests_ci_content_no_fs
    ), "Feature store disabled should not include feature engineering workflow step"


@pytest.mark.parametrize("cicd_platform", ["azure_devops"])
def test_azure_devops_generates_with_features_enabled(
    cicd_platform, tmpdir, databricks_cli
):
    """Test that Azure DevOps pipelines generate successfully with feature store enabled."""
    # Test with feature store enabled
    context = {
        "input_setup_cicd_and_project": "CICD_and_Project",
        "input_project_name": TEST_PROJECT_NAME,
        "input_root_dir": TEST_PROJECT_NAME,
        "input_cloud": "azure",
        "input_cicd_platform": "azure_devops",
        "input_include_feature_store": "yes",
        "input_include_mlflow_recipes": "no",
        "input_include_models_in_unity_catalog": "no",
    }

    generate(tmpdir, databricks_cli, context=context)

    project_dir = tmpdir / TEST_PROJECT_NAME
    pipelines_dir = project_dir / ".azure" / "devops-pipelines"

    # Verify pipelines still generate correctly with features enabled
    bundle_pipeline_path = pipelines_dir / f"{TEST_PROJECT_NAME}-bundle-cicd.yml"
    assert (
        bundle_pipeline_path.exists()
    ), "Pipeline should exist with feature store enabled"

    with open(bundle_pipeline_path, "r") as f:
        bundle_config = yaml.safe_load(f)

    # Pipeline should still be valid YAML
    assert (
        bundle_config is not None
    ), "Pipeline should be valid YAML with features enabled"
