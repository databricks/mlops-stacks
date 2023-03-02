# Databricks notebook source
##################################################################################
# Model Validation Notebook
##
# This notebook uses mlflow model validation API to run mode validation after training and registering a model
# in model registry, before deploying it to Production stage.
#
# It runs as part of CD and by an automated model training job -> validation -> deployment job defined under ``{{cookiecutter.project_name}}/terraform``
#
# Please finish the two cells with "TODO" comments before enabling the model validation.
#
# Parameters:
#
# * env : Name of the environment the notebook is run in (staging, or prod). Defaults to "prod".
#         You can add environment-specific logic to this notebook based on the value of this parameter,
#         e.g. read validation data from different tables or data sources across environments.
#
#
# For details on mlflow evaluate API, see doc https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.evaluate
# For details and examples about performing model validation, see the Model Validation documentation https://mlflow.org/docs/latest/models.html#model-validation
#
##################################################################################

# COMMAND ----------

# MAGIC %load_ext autoreload
# MAGIC %autoreload 2

# COMMAND ----------

# MAGIC %pip install -r ../../../requirements.txt

# COMMAND ----------

dbutils.widgets.dropdown(
    "env", "prod", ["staging", "prod"], "Environment(for input data)"
)
dbutils.widgets.text(
    "experiment_name",
    "{{cookiecutter.mlflow_experiment_parent_dir}}/{{cookiecutter.experiment_base_name}}-test",
    "Experiment Name",
)
dbutils.widgets.text("model_name", "", "Model Name")
dbutils.widgets.text("model_version", "", "Candidate Model Version")

# COMMAND ----------

import sys

sys.path.append("..")
sys.path.append("../..")

from model_validation_input import get_run_mode, RunMode

run_mode = get_run_mode()

if run_mode == RunMode.DISABLED:
    print(
        "Model validation is in DISABLED mode. Exit model validation without blocking model deployment."
    )
    dbutils.notebook.exit(0)
dry_run = run_mode == RunMode.DRY_RUN

if dry_run:
    print(
        "Model validation is in DRY_RUN mode. Validation threshold validation failures will not block model deployment."
    )
else:
    print(
        "Model validation is in ENABLED mode. Validation threshold validation failures will block model deployment."
    )

# COMMAND ----------

import mlflow
from mlflow.models import MetricThreshold, make_metric
import pandas as pd
import os
import numpy as np
import tempfile
import json
import traceback
from mlflow.recipes.utils import (
    get_recipe_config,
    get_recipe_name,
    get_recipe_root_path,
)
from mlflow.tracking.client import MlflowClient

client = MlflowClient()

env = dbutils.widgets.get("env")
experiment_name = dbutils.widgets.get("experiment_name")


def get_model_type_from_recipe():
    recipe_config = get_recipe_config("../../training", f"databricks-{env}")
    problem_type = recipe_config.get("recipe").split("/")[0]
    if problem_type.lower() == "regression":
        return "regressor"
    elif problem_type.lower() == "classification":
        return "classifier"
    else:
        raise Exception(f"Unsupported recipe {recipe_config}")


def get_targets_from_recipe():
    recipe_config = get_recipe_config("../../training", f"databricks-{env}")
    return recipe_config.get("target_col")


# set model evaluation parameters that can be inferred from the job
model_uri = dbutils.jobs.taskValues.get("Train", "model_uri", debugValue="")
model_name = dbutils.jobs.taskValues.get("Train", "model_name", debugValue="")
model_version = dbutils.jobs.taskValues.get("Train", "model_version", debugValue="")

if model_uri == "":
    model_name = dbutils.widgets.get("model_name")
    model_version = dbutils.widgets.get("model_version")
    model_uri = "models:/" + model_name + "/" + model_version

baseline_model_uri = "models:/" + model_name + "/Production"
evaluators = "default"
assert env != "None", "env notebook parameter must be specified"
assert model_uri != "", "model_uri notebook parameter must be specified"
assert model_name != "", "model_name notebook parameter must be specified"
assert model_version != "", "model_version notebook parameter must be specified"

# set experiment
mlflow.set_experiment(experiment_name)

# COMMAND ----------

from model_validation_input import (
    enable_baseline_comparison,
    get_prod_workspace_validation_input,
    get_staging_workspace_validation_input,
    get_model_type,
    get_validation_thresholds,
    get_custom_metrics,
    get_evaluator_config,
)

# take input
enable_baseline_comparison = enable_baseline_comparison()

if env == "prod":
    data = get_prod_workspace_validation_input(spark)
elif env == "staging":
    data = get_staging_workspace_validation_input(spark)
else:
    raise Exception(
        "Unknown environment. Please select 'prod' or 'staging' as environment name"
    )

targets = get_targets_from_recipe()

model_type = get_model_type_from_recipe()

custom_metrics = get_custom_metrics()

validation_thresholds = get_validation_thresholds()

evaluator_config = get_evaluator_config()

assert data, "Please provide correct data input for " + env
assert model_type, "Please provide correct model type"

# COMMAND ----------

# helper methods
def get_run_link(run_info):
    return "[Run](#mlflow/experiments/{0}/runs/{1})".format(
        run_info.experiment_id, run_info.run_id
    )


def get_training_run(model_name, model_version):
    version = client.get_model_version(model_name, model_version)
    return mlflow.get_run(run_id=version.run_id)


def generate_run_name(training_run):
    return None if not training_run else training_run.info.run_name + "-validation"


def generate_description(training_run):
    return (
        None
        if not training_run
        else "Model Training Details: {0}\n".format(get_run_link(training_run.info))
    )


def log_to_model_description(run, success):
    run_link = get_run_link(run.info)
    description = client.get_model_version(model_name, model_version).description
    status = "SUCCESS" if success else "FAILURE"
    if description != "":
        description += "\n\n---\n\n"
    description += "Model Validation Status: {0}\nValidation Details: {1}".format(
        status, run_link
    )
    client.update_model_version(
        name=model_name, version=model_version, description=description
    )


# COMMAND ----------

training_run = get_training_run(model_name, model_version)
# run evaluate
with mlflow.start_run(
    run_name=generate_run_name(training_run),
    description=generate_description(training_run),
) as run, tempfile.TemporaryDirectory() as tmp_dir:
    validation_thresholds_file = os.path.join(tmp_dir, "validation_thresholds.txt")
    with open(validation_thresholds_file, "w") as f:
        if validation_thresholds:
            for metric_name in validation_thresholds:
                f.write(
                    "{0:30}  {1}\n".format(
                        metric_name, str(validation_thresholds[metric_name])
                    )
                )
    mlflow.log_artifact(validation_thresholds_file)

    try:
        eval_result = mlflow.evaluate(
            model=model_uri,
            data=data,
            targets=targets,
            model_type=model_type,
            evaluators=evaluators,
            validation_thresholds=validation_thresholds,
            custom_metrics=custom_metrics,
            baseline_model=None
            if not enable_baseline_comparison
            else baseline_model_uri,
            evaluator_config=evaluator_config,
        )
        metrics_file = os.path.join(tmp_dir, "metrics.txt")
        with open(metrics_file, "w") as f:
            f.write(
                "{0:30}  {1:30}  {2}\n".format("metric_name", "candidate", "baseline")
            )
            for metric in eval_result.metrics:
                candidate_metric_value = str(eval_result.metrics[metric])
                baseline_metric_value = "N/A"
                if metric in eval_result.baseline_model_metrics:
                    mlflow.log_metric(
                        "baseline_" + metric, eval_result.baseline_model_metrics[metric]
                    )
                    baseline_metric_value = str(
                        eval_result.baseline_model_metrics[metric]
                    )
                f.write(
                    "{0:30}  {1:30}  {2}\n".format(
                        metric, candidate_metric_value, baseline_metric_value
                    )
                )
        mlflow.log_artifact(metrics_file)
        log_to_model_description(run, True)
    except Exception as err:
        log_to_model_description(run, False)
        error_file = os.path.join(tmp_dir, "error.txt")
        with open(error_file, "w") as f:
            f.write("Validation failed : " + str(err) + "\n")
            f.write(traceback.format_exc())
        mlflow.log_artifact(error_file)
        if not dry_run:
            raise err
        else:
            print(
                "Model validation failed in DRY_RUN. It will not block model deployment."
            )

# COMMAND ----------
