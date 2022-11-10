from cookiecutter.main import cookiecutter
import pathlib
import pytest
import json
from functools import wraps

COOKIECUTTER_ROOT_DIRECTORY = str(pathlib.Path(__file__).parent.parent)


def parametrize_by_cloud(fn):
    @wraps(fn)
    @pytest.mark.parametrize("cloud", ["aws", "azure"])
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    return wrapper


def parametrize_by_project_generation_params(fn):
    @pytest.mark.parametrize(
        "cloud,cicd_platform,include_feature_store",
        [
            ("aws", "GitHub Actions", "no"),
            ("azure", "GitHub Actions", "no"),
            ("azure", "Azure DevOps", "no"),
            ("aws", "GitHub Actions", "yes"),
            ("azure", "GitHub Actions", "yes"),
            #  ADO + Feature Store is not supported yet.
            # ("azure", "Azure DevOps", "yes""),
        ],
    )
    @wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    return wrapper


@pytest.fixture
def generated_project_dir(tmpdir, cloud, cicd_platform, include_feature_store):
    generate(
        tmpdir,
        {
            "project_name": "my-mlops-project",
            "cloud": cloud,
            "cicd_platform": cicd_platform,
            "include_feature_store": include_feature_store,
            "mlflow_experiment_parent_dir": "/tmp",
            "databricks_staging_workspace_host": "https://adb-3214.67.azuredatabricks.net",
            "databricks_prod_workspace_host": "https://adb-345.89.azuredatabricks.net",
            "default_branch": "main",
            "release_branch": "release",
            "read_user_group": "users",
        },
    )
    return tmpdir


def read_workflow(tmpdir):
    return (tmpdir / "my-mlops-project" / ".github/workflows/run-tests.yml").read_text(
        "utf-8"
    )


def markdown_checker_configs(tmpdir):
    markdown_checker_config_dict = {
        "ignorePatterns": [
            {"pattern": "http://127.0.0.1:5000"},
            {"pattern": "https://adb-3214.67.azuredatabricks.net*"},
            {"pattern": "https://adb-345.89.azuredatabricks.net*"},
        ],
        "httpHeaders": [
            {
                "urls": ["https://docs.github.com/"],
                "headers": {"Accept-Encoding": "zstd, br, gzip, deflate"},
            },
        ],
    }

    file_name = "checker-config.json"

    with open(tmpdir / "my-mlops-project" / file_name, "w") as outfile:
        json.dump(markdown_checker_config_dict, outfile)


def generate(directory, context):
    cookiecutter(
        template=COOKIECUTTER_ROOT_DIRECTORY,
        output_dir=str(directory),
        no_input=True,
        extra_context=context,
    )


def paths(directory):
    paths = list(pathlib.Path(directory).glob("**/*"))
    paths = [r.relative_to(directory) for r in paths]
    return {str(f) for f in paths if str(f) != "."}
