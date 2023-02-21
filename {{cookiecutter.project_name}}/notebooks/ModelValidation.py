# Databricks notebook source
##################################################################################
# Model Validation Notebook
##
# This notebook uses mlflow model validation API to run mode validation after training and registering a model 
# in model registry, before deploying it to Production stage.
#
# It runs as part of CD and by an automated model training job -> validation -> deployment job defined under ``databricks-config``
#
# Please finish the two cells with "TODO" comments before enabling the model validation.
#
# Parameters:
#
# * env (optional): Name of the environment the notebook is run in (staging, or prod). Defaults to "prod".
#                   You can add environment-specific logic to this notebook based on the value of this parameter,
#                   e.g. read validation data from different tables or data sources across environments.
# * run_mode (optional): The model validation run mode. Defaults to Disabled. Possible values are disabled, dry_run, enabled.
#                       disabled : Do not run the model validation notebook.
#                       dry_run  : Run the model validation notebook. Ignore failed model validation rules and proceed to move model to Production stage.
#                       enabled  : Run the model validation notebook. Move model to Production stage only if all model validation rules are passing.
#
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

# MAGIC %pip install -r ../requirements.txt

# COMMAND ----------

dbutils.widgets.dropdown("env", "prod", ["staging", "prod"], "Environment Name")
dbutils.widgets.dropdown("run_mode", "disabled", ["disabled", "dry_run", "enabled"], "Run Mode")

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
_run_mode = dbutils.widgets.get("run_mode")
if _run_mode.lower() == "disabled":
    dbutils.notebook.exit(0)
dry_run = _run_mode.lower() == "dry_run"

def get_model_type_from_recipe():
    recipe_config = get_recipe_config("../", f"databricks-{env}")
    problem_type = recipe_config.get("recipe").split("/")[0]
    if problem_type.lower() == "regression":
        return "regressor"
    elif problem_type.lower() == "classification":
        return "classifier"
    else:
        raise Exception(f"Unsupported recipe {recipe_config}")

def get_targets_from_recipe():
    recipe_config = get_recipe_config("../", f"databricks-{env}")
    return recipe_config.get("target_col")

# set model evaluation parameters that can be inferred from the job
model_uri = dbutils.jobs.taskValues.get("Train", "model_uri", debugValue="")
model_name = dbutils.jobs.taskValues.get("Train", "model_name", debugValue="")
model_version = dbutils.jobs.taskValues.get("Train", "model_version", debugValue="")

baseline_model_uri = "models:/" + model_name + "/Production"
evaluators = "default"
assert env != "None", "env notebook parameter must be specified"
assert model_uri != "", "model_uri notebook parameter must be specified"
assert model_name != "", "model_name notebook parameter must be specified"
assert model_version != "", "model_version notebook parameter must be specified"

# set experiment
mlflow.set_experiment(experiment_name)

# COMMAND ----------

##################################################################################
# TODO : Please fill in this cell with proper values for enable_baseline_comparison,
#        data, targets, model_type, custom_metrics, validation_thresholds
#        evaluator_config
##################################################################################

# Whether to load the current registered "Production" stage model as baseline. A version with "Production" stage must 
# exist for the model.
# Baseline model is a requirement for relative change and absolute change validation rules.
# TODO(optional) : enable_baseline_comparison
enable_baseline_comparison = False

# model validation data input for staging or prod workspace. A Pandas DataFrame or Spark DataFrame, containing evaluation features and labels.
# Please refer to data parameter in mlflow.evaluate documentation https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.evaluate
if env == "prod":
    # TODO(required) : set data for prod workspace
    data = None
elif env == "staging":
    # TODO(required) : set data for staging workspace
    data = None
else:
    raise Exception("Unknown environment. Please select 'prod' or 'staging' as environment name")

# The string name of a column from data that contains evaluation labels.
# Call get_targets_from_recipe() to get targets from recipe configs if mlflow recipe is used. 
# Please refer to targets parameter in mlflow.evaluate documentation https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.evaluate
# TODO(required) : targets
targets = get_targets_from_recipe()


# A string describing the model type. The model type can be either "regressor" and "classifier".
# Call get_model_type_from_recipe() to get model type from recipe configs if mlflow recipe is used. 
# Please refer to model_type parameter in mlflow.evaluate documentation https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.evaluate
# TODO(required) : model_type
model_type = get_model_type_from_recipe()

# Custom metrics to be included. Set it to None if custom metrics are not needed.
# Please refer to custom_metrics parameter in mlflow.evaluate documentation https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.evaluate
# TODO(optional) : define custom metric function as necessary
# TODO(optional) : custom_metrics
custom_metrics = []

# Define model validation rules. Set it to None if validation rules are not needed.
# Please refer to custom_metrics parameter in mlflow.evaluate documentation https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.evaluate
# TODO(optional) : validation_thresholds
validation_thresholds = {}

# A dictionary of additional configurations to supply to the evaluator.
# Please refer to evaluator_config parameter in mlflow.evaluate documentation https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.evaluate
# TODO(optional) : evaluator_config
evaluator_config = {}

# COMMAND ----------

client.get_model_version(model_name, model_version).description

# COMMAND ----------

eval_result = None
err = None

def log_to_model_description(run, success):
    run_info = run.info
    run_link = "[Run](#mlflow/experiments/{0}/runs/{1})".format(run_info.experiment_id, run_info.run_id)
    description = client.get_model_version(model_name, model_version).description
    status = "SUCCESS" if success else "FAILURE"
    if description != "":
        description += """
            ---
        """.replace(" ", "")
    description += "Model Validation Status: {0}\nValidation Details: {1}".format(status, run_link)
    client.update_model_version(
        name=model_name,
        version=model_version,
        description=description
    )

# run evaluate
with mlflow.start_run() as run, tempfile.TemporaryDirectory() as tmp_dir:

    validation_thresholds_file = os.path.join(tmp_dir, "validation_thresholds.txt")
    with open(validation_thresholds_file, "w") as f:
        if validation_thresholds:
            for metric_name in validation_thresholds:
                f.write("{0:30}  {1}\n".format(metric_name, str(validation_thresholds[metric_name])))
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
            baseline_model=None if not enable_baseline_comparison else baseline_model_uri,
            evaluator_config=evaluator_config,
        )
        metrics_file = os.path.join(tmp_dir, "metrics.txt")
        with open(metrics_file, "w") as f:
            f.write("{0:30}  {1:30}  {2}\n".format("metric_name", "candidate", "baseline"))
            for metric in eval_result.metrics:
                candidate_metric_value = str(eval_result.metrics[metric])
                baseline_metric_value = "N/A"
                if metric in eval_result.baseline_model_metrics:
                    mlflow.log_metric("baseline_"+metric, eval_result.baseline_model_metrics[metric])
                    baseline_metric_value = str(eval_result.baseline_model_metrics[metric])
                f.write("{0:30}  {1:30}  {2}\n".format(metric, candidate_metric_value, baseline_metric_value))
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
