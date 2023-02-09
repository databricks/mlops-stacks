from cookiecutter.exceptions import FailedHookException
import os
import pathlib
import pytest
import subprocess
from utils import (
    read_workflow,
    generate,
    markdown_checker_configs,
    paths,
    generated_project_dir,
    parametrize_by_cloud,
    parametrize_by_project_generation_params,
)
from unittest import mock

DEFAULT_PROJECT_NAME = "my-mlops-project"
# UUID that when set as project name, prevents the removal of files needed in testing
TEST_PROJECT_NAME = "27896cf3-bb3e-476e-8129-96df0406d5c7"
DEFAULT_PARAM_VALUES = {
    "default_branch": "main",
    "release_branch": "release",
    "read_user_group": "users",
    "include_feature_store": "no",
}
DEFAULT_PARAMS_AZURE = {
    "cloud": "azure",
    "databricks_staging_workspace_host": "https://adb-xxxx.xx.azuredatabricks.net",
    "databricks_prod_workspace_host": "https://adb-xxxx.xx.azuredatabricks.net",
}
DEFAULT_PARAMS_AWS = {
    "cloud": "aws",
    "databricks_staging_workspace_host": "https://your-staging-workspace.cloud.databricks.com",
    "databricks_prod_workspace_host": "https://your-prod-workspace.cloud.databricks.com",
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
    # Test that there are no accidental hardcoded Databricks workspace URLs included in stack source files
    cookiecutter_dir = (
        pathlib.Path(__file__).parent.parent / "{{cookiecutter.project_name}}"
    )
    test_paths = [
        os.path.join(cookiecutter_dir, path) for path in paths(cookiecutter_dir)
    ]
    assert_no_disallowed_strings_in_files(
        file_paths=test_paths,
        disallowed_strings=[
            "azuredatabricks.net",
            "cloud.databricks.com",
            "gcp.databricks.com",
        ],
    )


def test_no_databricks_doc_strings_before_project_generation():
    cookiecutter_dir = (
        pathlib.Path(__file__).parent.parent / "{{cookiecutter.project_name}}"
    )
    test_paths = [
        os.path.join(cookiecutter_dir, path) for path in paths(cookiecutter_dir)
    ]
    assert_no_disallowed_strings_in_files(
        file_paths=test_paths,
        disallowed_strings=[
            "https://docs.microsoft.com/en-us/azure/databricks",
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
        npm install -g markdown-link-check
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
        {
            "mlflow_experiment_parent_dir": "bad-dir-with-no-slash",
        },
        {
            "mlflow_experiment_parent_dir": "/Repos",
        },
        {
            "mlflow_experiment_parent_dir": "/Repos/my-ml-model",
        },
        {
            "mlflow_experiment_parent_dir": "/Users",
        },
        {
            "mlflow_experiment_parent_dir": "/Users/test@databricks.com",
        },
        {
            "mlflow_experiment_parent_dir": "/Users/test@databricks.com/",
        },
        {
            "mlflow_experiment_parent_dir": "/",
        },
        {
            "mlflow_experiment_parent_dir": "///",
        },
        {
            "databricks_staging_workspace_host": "http://no-https",
        },
        {
            "databricks_prod_workspace_host": "no-https",
        },
        {
            "project_name": "a",
        },
        {
            "project_name": "a-b",
        },
        {
            "project_name": "Name with spaces",
        },
        {
            "project_name": "name/with/slashes",
        },
        {
            "project_name": "name\\with\\backslashes",
        },
        {
            "project_name": "name.with.periods",
        },
    ],
)
def test_generate_fails_with_invalid_params(tmpdir, invalid_params):
    with pytest.raises(FailedHookException):
        generate(tmpdir, invalid_params)


@pytest.mark.parametrize(
    "valid_params",
    [
        {
            "mlflow_experiment_parent_dir": "/Users/test@databricks.com/project",
        },
        {
            "mlflow_experiment_parent_dir": "/Users/test@databricks.com/project/",
        },
        {
            "mlflow_experiment_parent_dir": "/Repos-fake",
        },
        {
            "mlflow_experiment_parent_dir": "/Users-fake",
        },
        {
            "mlflow_experiment_parent_dir": "/ml-projects/my-ml-project",
        },
    ],
)
def test_generate_succeeds_with_valid_params(tmpdir, valid_params):
    generate(tmpdir, valid_params)


@pytest.mark.parametrize(
    "experiment_parent_dir,expected_dir",
    [
        ("/mlops-project-directory/", "/mlops-project-directory"),
        ("/Users/test@databricks.com/project/", "/Users/test@databricks.com/project"),
    ],
)
def test_strip_slash_if_needed_from_mlflow_experiment_parent_dir(
    tmpdir, experiment_parent_dir, expected_dir
):
    params = {
        "mlflow_experiment_parent_dir": experiment_parent_dir,
    }
    generate(tmpdir, params)
    tf_config_contents = (
        tmpdir / DEFAULT_PROJECT_NAME / "databricks-config/prod/locals.tf"
    ).read_text("utf-8")
    assert f'mlflow_experiment_parent_dir = "{expected_dir}"' in tf_config_contents


@parametrize_by_project_generation_params
def test_generate_project_with_default_values(
    tmpdir, cloud, cicd_platform, include_feature_store
):
    """
    Asserts the default parameter values for the stack. The project name and experiment
    parent directory are excluded from this test as they covered in other tests. If this test fails
    due to an update of the default values, please do the following checks:
    - The default param value constants in this test are up to date.
    - The default param values in the substitution logic in the pre_gen_project.py hook are up to date.
    - The default param values in the help strings in cookiecutter.json are up to date.
    """
    context = {
        "project_name": TEST_PROJECT_NAME,
        "cloud": cloud,
        "cicd_platform": cicd_platform,
    }
    if cloud == "azure":
        del context["cloud"]
    generate(tmpdir, context=context)
    test_file_contents = (
        tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
    ).read_text("utf-8")
    if cloud == "azure":
        params = {**DEFAULT_PARAM_VALUES, **DEFAULT_PARAMS_AZURE}
    elif cloud == "aws":
        params = {**DEFAULT_PARAM_VALUES, **DEFAULT_PARAMS_AWS}
    for param, value in params.items():
        assert f"{param}={value}" in test_file_contents


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
def test_workspace_dir_strip_query_params(tmpdir, cloud, workspace_url_suffix):
    workspace_host = {
        "aws": "https://dbc-my-aws-workspace.cloud.databricks.com",
        "azure": "https://adb-mycoolworkspace.11.azuredatabricks.net",
    }[cloud]
    workspace_url = f"{workspace_host}{workspace_url_suffix}"
    context = {
        "project_name": TEST_PROJECT_NAME,
        "databricks_staging_workspace_host": workspace_url,
        "databricks_prod_workspace_host": workspace_url,
        "cloud": cloud,
    }
    generate(tmpdir, context=context)
    test_file_contents = (
        tmpdir / TEST_PROJECT_NAME / "_params_testing_only.txt"
    ).read_text("utf-8")
    assert f"databricks_staging_workspace_host={workspace_host}\n" in test_file_contents
    assert f"databricks_prod_workspace_host={workspace_host}\n" in test_file_contents


def test_generate_project_default_project_name_params(tmpdir):
    # Asserts default parameter values for parameters that involve the project name
    generate(tmpdir, context={})
    readme_contents = (tmpdir / DEFAULT_PROJECT_NAME / "README.md").read_text("utf-8")
    assert DEFAULT_PROJECT_NAME in readme_contents
    tf_config_contents = (
        tmpdir / DEFAULT_PROJECT_NAME / "databricks-config/prod/locals.tf"
    ).read_text("utf-8")
    assert (
        f'mlflow_experiment_parent_dir = "/{DEFAULT_PROJECT_NAME}"'
        in tf_config_contents
    )


@pytest.mark.parametrize(
    "cookiecutter_version, is_valid",
    [
        ("2.0.5", False),
        ("2.1.0", True),
        ("2.1.1", True),
        ("2.1.1.dev0", True),
        ("2.9.0", True),
        ("2.10.0", True),
        ("3.0.0", True),
        ("1.9.3", False),
        ("1.0.0", False),
    ],
)
def test_cookiecutter_version_validation(cookiecutter_version, is_valid):
    from hooks.pre_gen_project import validate_cookiecutter_version

    if is_valid:
        validate_cookiecutter_version(cookiecutter_version)
    else:
        with pytest.raises(ValueError):
            validate_cookiecutter_version(cookiecutter_version)
