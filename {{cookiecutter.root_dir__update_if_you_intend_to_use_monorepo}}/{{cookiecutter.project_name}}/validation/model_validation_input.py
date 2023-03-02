##################################################################################
# TODO : Please fill in parameters with proper values for your project
##################################################################################
import numpy as np
from enum import Enum
from mlflow.models import MetricThreshold, make_metric


class RunMode(Enum):
    ENABLED = 1
    DRY_RUN = 2
    DISABLED = 3


# The `run_mode` defines whether model validation is enabled or not. It can be one of the three values:
# - `DISABLED` : Do not run the model validation notebook.
# - `DRY_RUN`  : Run the model validation notebook. Ignore failed model validation rules and proceed to move model to Production stage.
# - `ENABLED`  : Run the model validation notebook. Move model to Production stage only if all model validation rules are passing.
# TODO(required)
def get_run_mode():
    return RunMode.DISABLED


# Whether to load the current registered "Production" stage model as baseline. A version with "Production" stage must
# exist for the model.
# Baseline model is a requirement for relative change and absolute change validation rules.
# TODO(required)
def enable_baseline_comparison():
    return False


# model validation data input for prod workspace. A Pandas DataFrame or Spark DataFrame, containing evaluation features and labels.
# Please refer to data parameter in mlflow.evaluate documentation https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.evaluate
# TODO(required)
def get_prod_workspace_validation_input(spark):
    return spark.sql(
        "SELECT * FROM delta.`dbfs:/databricks-datasets/nyctaxi-with-zipcodes/subsampled`"
    )


# model validation data input for staging workspace. A Pandas DataFrame or Spark DataFrame, containing evaluation features and labels.
# Please refer to data parameter in mlflow.evaluate documentation https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.evaluate
# TODO(required)
def get_staging_workspace_validation_input(spark):
    return spark.sql(
        "SELECT * FROM delta.`dbfs:/databricks-datasets/nyctaxi-with-zipcodes/subsampled`"
    )


# A string describing the model type. The model type can be either "regressor" and "classifier".
# Please refer to model_type parameter in mlflow.evaluate documentation https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.evaluate
# TODO(required) : model_type
def get_model_type():
    return "regressor"


# The string name of a column from data that contains evaluation labels.
# Please refer to targets parameter in mlflow.evaluate documentation https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.evaluate
# TODO(required) : targets
def get_targets():
    return "mean_squared_error"


# Custom metrics to be included. Set it to None if custom metrics are not needed.
# Please refer to custom_metrics parameter in mlflow.evaluate documentation https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.evaluate
# TODO(optional) : define custom metric function to be included in custom_metrics.
def squared_diff_plus_one(eval_df, _builtin_metrics):
    """
    This example custom metric function creates a metric based on the ``prediction`` and
    ``target`` columns in ``eval_df`.
    """
    return np.sum(np.abs(eval_df["prediction"] - eval_df["target"] + 1) ** 2)


# Custom metrics to be included. Set it to None if custom metrics are not needed.
# Please refer to custom_metrics parameter in mlflow.evaluate documentation https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.evaluate
# TODO(optional) : custom_metrics
def get_custom_metrics():
    return [
        make_metric(
            eval_fn=squared_diff_plus_one,
            greater_is_better=False,
        ),
    ]


# Define model validation rules. Set it to None if validation rules are not needed.
# Please refer to custom_metrics parameter in mlflow.evaluate documentation https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.evaluate
# TODO(optional) : validation_thresholds
def get_validation_thresholds():
    return {
        "max_error": MetricThreshold(
            threshold=500, higher_is_better=False  # max_error should be <= 500
        ),
        "mean_squared_error": MetricThreshold(
            threshold=20,  # mean_squared_error should be <= 20
            # min_absolute_change=0.01,  # mean_squared_error should be at least 0.01 greater than baseline model accuracy
            # min_relative_change=0.01,  # mean_squared_error should be at least 1 percent greater than baseline model accuracy
            higher_is_better=False,
        ),
    }


# A dictionary of additional configurations to supply to the evaluator.
# Please refer to evaluator_config parameter in mlflow.evaluate documentation https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.evaluate
# TODO(optional) : evaluator_config
def get_evaluator_config():
    return {}
