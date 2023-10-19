import os
import pathlib
import pytest
import subprocess
from utils import (
    read_workflow,
    generate,
    databricks_cli,
    markdown_checker_configs,
    paths,
    generated_project_dir,
    parametrize_by_cloud,
    parametrize_by_project_generation_params,
)
from unittest import mock

DEFAULT_PROJECT_NAME = "my-mlops-project"
DEFAULT_PROJECT_DIRECTORY = "my_mlops_project"
# UUID that when set as project name, prevents the removal of files needed in testing
TEST_PROJECT_NAME = "27896cf3-bb3e-476e-8129-96df0406d5c7"
TEST_PROJECT_DIRECTORY = "27896cf3_bb3e_476e_8129_96df0406d5c7"
DEFAULT_PARAM_VALUES = {
    "input_default_branch": "main",
    "input_release_branch": "release",
    "input_read_user_group": "users",
    "input_include_feature_store": "no",
    "input_include_mlflow_recipes": "no",
    "input_include_models_in_unity_catalog": "no",
    "input_schema_name": "schema_name",
    "input_unity_catalog_read_user_group": "account users",
}
DEFAULT_PARAMS_AZURE = {
    "input_cloud": "azure",
    "input_databricks_staging_workspace_host": "https://adb-xxxx.xx.azuredatabricks.net",
    "input_databricks_prod_workspace_host": "https://adb-xxxx.xx.azuredatabricks.net",
}
DEFAULT_PARAMS_AWS = {
    "input_cloud": "aws",
    "input_databricks_staging_workspace_host": "https://your-staging-workspace.cloud.databricks.com",
    "input_databricks_prod_workspace_host": "https://your-prod-workspace.cloud.databricks.com",
}


def assert_no_disallowed_strings_in_files(
    file_paths, disallowed_strings, exclude_path_matches=None
):
    """
    Assert that all files in file_paths, besides those with paths containing
    one of exclude_path_matches as a substring, do not contain any of the specified disallowed strings

    :param file_paths List of paths of files to check
    :param disallowed_strings: List of disallowed strings
    :param exclude_path_matches: List of substrings e.g. [".github", ".png"]. Any files whose paths
    contain one of these substrings will not be checked for disallowed strings
    """
    if exclude_path_matches is None:
        exclude_path_matches = []
    # Exclude binary files like pngs from being string-matched
    exclude_path_matches = exclude_path_matches + [".png", ".parquet"]
    for path in file_paths:
        assert os.path.exists(path), "Provided nonexistent path to test: %s" % path

    def assert_no_disallowed_strings(filepath):
        with open(filepath, "r") as f:
            data = f.read()
        for s in disallowed_strings:
            assert s not in data

    def should_check_file_for_disallowed_strings(path):
        return not any(
            substring in path for substring in exclude_path_matches
        ) and os.path.isfile(path)

    test_paths = list(filter(should_check_file_for_disallowed_strings, file_paths))
    for path in test_paths:
        assert_no_disallowed_strings(path)


@parametrize_by_project_generation_params
def test_no_template_strings_after_param_substitution(generated_project_dir):
    assert_no_disallowed_strings_in_files(
        file_paths=[
            os.path.join(generated_project_dir, path)
            for path in paths(generated_project_dir)
        ],
        disallowed_strings=["{{", "{%", "%}"],
        exclude_path_matches=[".github", ".yml", ".yaml"],
    )


def test_no_databricks_workspace_urls():
    # Test that there are no accidental hardcoded Databricks workspace URLs included in source files
    template_dir = pathlib.Path(__file__).parent.parent / "template"
    test_paths = [os.path.join(template_dir, path) for path in paths(template_dir)]
    assert_no_disallowed_strings_in_files(
        file_paths=test_paths,
        disallowed_strings=[
            "azuredatabricks.net",
            "cloud.databricks.com",
            "gcp.databricks.com",
        ],
    )


def test_no_databricks_doc_strings_before_project_generation():
    template_dir = pathlib.Path(__file__).parent.parent / "template"
    test_paths = [os.path.join(template_dir, path) for path in paths(template_dir)]
    assert_no_disallowed_strings_in_files(
        file_paths=test_paths,
        disallowed_strings=[
            "https://learn.microsoft.com/en-us/azure/databricks",
            "https://docs.databricks.com/",
            "https://docs.gcp.databricks.com/",
        ],
    )


@pytest.mark.large
@parametrize_by_project_generation_params
def test_markdown_links(generated_project_dir):
    markdown_checker_configs(generated_project_dir)
    subprocess.run(
        """
        npm install -g markdown-link-check@3.10.3
        find . -name \*.md -print0 | xargs -0 -n1 markdown-link-check -c ./checker-config.json
        """,
        shell=True,
        check=True,
        executable="/bin/bash",
        cwd=(generated_project_dir / "my-mlops-project"),
    )


@pytest.mark.parametrize(
    "invalid_params",
    [
        {"input_databricks_staging_workspace_host": "http://no-https"},
        {"input_databricks_prod_workspace_host": "no-https"},
        {"input_project_name": "a"},
        {"input_project_name": "a-"},
        {"input_project_name": "Name with spaces"},
        {"input_project_name": "name/with/slashes"},
        {"input_project_name": "name\\with\\backslashes"},
        {"input_project_name": "name.with.periods"},
    ],
)
def test_generate_fails_with_invalid_params(tmpdir, databricks_cli, invalid_params):
    with pytest.raises(Exception):
        generate(tmpdir, databricks_cli, invalid_params)


@pytest.mark.parametrize("valid_params", [{}])
def test_generate_succeeds_with_valid_params(tmpdir, databricks_cli, valid_params):
    generate(tmpdir, databricks_cli, valid_params)


@parametrize_by_project_generation_params
def test_generate_project_with_default_values(
    tmpdir,
    databricks_cli,
    cloud,
    cicd_platform,
    include_feature_store,
    include_mlflow_recipes,
    include_models_in_unity_catalog,
):
    """
    Asserts the default parameter values. The project name and experiment
    parent directory are excluded from this test as they covered in other tests. If this test fails
    due to an update of the default values, please do the following checks:
    - The default param value constants in this test are up to date.
    - The default param values in the substitution logic in the pre_gen_project.py hook are up to date.
    - The default param values in the help strings in databricks_template_schema.json are up to date.
    """
    context = {
        "input_project_name": TEST_PROJECT_NAME,
        "input_root_dir": TEST_PROJECT_NAME,
        "input_cloud": cloud,
        "input_cicd_platform": cicd_platform,
    }
    # Testing that Azure is the default option.
    if cloud == "azure":
        del context["input_cloud"]
    generate(tmpdir, databricks_cli, context=context)
    test_file_contents = (
        tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
    ).read_text("utf-8")
    if cloud == "azure":
        params = {**DEFAULT_PARAM_VALUES, **DEFAULT_PARAMS_AZURE}
    elif cloud == "aws":
        params = {**DEFAULT_PARAM_VALUES, **DEFAULT_PARAMS_AWS}
    for param, value in params.items():
        assert f"{param}={value}" in test_file_contents


@parametrize_by_project_generation_params
def test_generate_project_check_delta_output(
    tmpdir,
    databricks_cli,
    cloud,
    cicd_platform,
    include_feature_store,
    include_mlflow_recipes,
    include_models_in_unity_catalog,
):
    """
    Asserts the behavior of Delta Table-related artifacts when generating MLOps Stacks.
    """
    context = {
        "input_project_name": TEST_PROJECT_NAME,
        "input_root_dir": TEST_PROJECT_NAME,
        "input_cloud": cloud,
        "input_cicd_platform": cicd_platform,
        "input_include_feature_store": include_feature_store,
        "input_include_mlflow_recipes": include_mlflow_recipes,
        "input_include_models_in_unity_catalog": include_models_in_unity_catalog,
    }
    generate(tmpdir, databricks_cli, context=context)
    delta_notebook_path = (
        tmpdir
        / TEST_PROJECT_NAME
        / TEST_PROJECT_DIRECTORY
        / "training"
        / "notebooks"
        / "Train.py"
    )
    if include_mlflow_recipes == "no" and include_feature_store == "no":
        assert os.path.isfile(delta_notebook_path)
    else:
        assert not os.path.isfile(delta_notebook_path)


@parametrize_by_project_generation_params
def test_generate_project_check_feature_store_output(
    tmpdir,
    databricks_cli,
    cloud,
    cicd_platform,
    include_feature_store,
    include_mlflow_recipes,
    include_models_in_unity_catalog,
):
    """
    Asserts the behavior of feature store-related artifacts when generating MLOps Stacks.
    """
    context = {
        "input_project_name": TEST_PROJECT_NAME,
        "input_root_dir": TEST_PROJECT_NAME,
        "input_cloud": cloud,
        "input_cicd_platform": cicd_platform,
        "input_include_feature_store": include_feature_store,
        "input_include_mlflow_recipes": include_mlflow_recipes,
        "input_include_models_in_unity_catalog": include_models_in_unity_catalog,
    }
    generate(tmpdir, databricks_cli, context=context)
    fs_notebook_path = (
        tmpdir
        / TEST_PROJECT_NAME
        / TEST_PROJECT_DIRECTORY
        / "feature_engineering"
        / "notebooks"
        / "GenerateAndWriteFeatures.py"
    )
    if include_feature_store == "yes":
        assert os.path.isfile(fs_notebook_path)
    else:
        assert not os.path.isfile(fs_notebook_path)


@parametrize_by_project_generation_params
def test_generate_project_check_recipe_output(
    tmpdir,
    databricks_cli,
    cloud,
    cicd_platform,
    include_feature_store,
    include_mlflow_recipes,
    include_models_in_unity_catalog,
):
    """
    Asserts the behavior of MLflow Recipes-related artifacts when generating MLOps Stacks.
    """
    context = {
        "input_project_name": TEST_PROJECT_NAME,
        "input_root_dir": TEST_PROJECT_NAME,
        "input_cloud": cloud,
        "input_cicd_platform": cicd_platform,
        "input_include_feature_store": include_feature_store,
        "input_include_mlflow_recipes": include_mlflow_recipes,
        "input_include_models_in_unity_catalog": include_models_in_unity_catalog,
    }
    generate(tmpdir, databricks_cli, context=context)
    recipe_notebook_path = (
        tmpdir
        / TEST_PROJECT_NAME
        / TEST_PROJECT_DIRECTORY
        / "training"
        / "notebooks"
        / "TrainWithMLflowRecipes.py"
    )
    if include_mlflow_recipes == "yes":
        assert os.path.isfile(recipe_notebook_path)
    else:
        assert not os.path.isfile(recipe_notebook_path)


@pytest.mark.parametrize(
    "workspace_url_suffix",
    [
        "/?o=123456789#job/1234/run/9234",
        "/?o=123456789#",
        "/?o=123456789#ml/dashboard",
        "#ml/dashboard",
    ],
)
@parametrize_by_cloud
def test_workspace_dir_strip_query_params(
    tmpdir, databricks_cli, cloud, workspace_url_suffix
):
    workspace_host = {
        "aws": "https://dbc-my-aws-workspace.cloud.databricks.com",
        "azure": "https://adb-mycoolworkspace.11.azuredatabricks.net",
    }[cloud]
    workspace_url = f"{workspace_host}{workspace_url_suffix}"
    context = {
        "input_project_name": TEST_PROJECT_NAME,
        "input_root_dir": TEST_PROJECT_NAME,
        "input_databricks_staging_workspace_host": workspace_url,
        "input_databricks_prod_workspace_host": workspace_url,
        "input_cloud": cloud,
    }
    generate(tmpdir, databricks_cli, context=context)
    test_file_contents = (
        tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
    ).read_text("utf-8")
    assert (
        f"\ndatabricks_staging_workspace_host={workspace_host}\n" in test_file_contents
    )
    assert f"\ndatabricks_prod_workspace_host={workspace_host}\n" in test_file_contents


def test_generate_project_default_project_name_params(tmpdir, databricks_cli):
    # Asserts default parameter values for parameters that involve the project name
    generate(tmpdir, databricks_cli, context={})
    readme_contents = (tmpdir / DEFAULT_PROJECT_NAME / "README.md").read_text("utf-8")
    assert DEFAULT_PROJECT_NAME in readme_contents
