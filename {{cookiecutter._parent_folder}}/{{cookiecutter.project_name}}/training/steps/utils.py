"""
This module contains utils shared between different notebooks
"""
import json
import mlflow
import os


def get_deployed_model_stage_for_env(env):
    """
    Get the model version stage under which the latest deployed model version can be found
    for the current environment
    :param env: Current environment
    :return: Model version stage
    """
    # For a registered model version to be served, it needs to be in either the Staging or Production
    # model registry stage
    # ({{ "applications/machine-learning/manage-model-lifecycle/index.html#transition-a-model-stage" | generate_doc_link(cookiecutter.cloud) }}).
    # For models in dev and staging, we deploy the model to the "Staging" stage, and in prod we deploy to the
    # "Production" stage
    _MODEL_STAGE_FOR_ENV = {
        "dev": "Staging",
        "staging": "Staging",
        "prod": "Production",
    }
    return _MODEL_STAGE_FOR_ENV[env]


def _get_ml_config_value(env, key):
    # Reading ml config from terraform output file for the respective key and env(staging/prod).
    conf_file_path = os.path.join(
        os.pardir, "databricks-config", "output", f"{env}.json"
    )
    try:
        with open(conf_file_path, "r") as handle:
            data = json.loads(handle.read())
    except FileNotFoundError as e:
        raise RuntimeError(
            f"Unable to find file '{conf_file_path}'. Make sure ML config-as-code resources defined "
            f"under databricks-config have been deployed to {env} (see databricks-config/README in the "
            f"current git repo for details)"
        ) from e
    try:
        return data[key]["value"]
    except KeyError as e:
        raise RuntimeError(
            f"Unable to load key '{key}' for env '{env}'. Ensure that key '{key}' is defined "
            f"in f{conf_file_path}"
        ) from e


def _get_resource_name_suffix(test_mode):
    if test_mode:
        return "-test"
    else:
        return ""


def get_model_name(env, test_mode=False):
    """
    Get the registered model name for the current environment.

    In dev or when running integration tests, we rely on a hardcoded model name.
    Otherwise, e.g. in production jobs, we read the model name from Terraform config-as-code output

    :param env: Current environment
    :param test_mode: Whether the notebook is running in test mode.

    :return: Registered Model name.
    """
    if env == "dev" or test_mode:
        resource_name_suffix = _get_resource_name_suffix(test_mode)
        return f"{{cookiecutter.model_name}}{resource_name_suffix}"
    else:
        # Read ml model name from databricks-config
        return _get_ml_config_value(env, "{{cookiecutter.project_name}}_model_name")
