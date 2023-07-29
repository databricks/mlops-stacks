import numpy as np
from mlflow.models import make_metric, MetricThreshold

# Custom metrics to be included. Return empty list if custom metrics are not needed.
# Please refer to custom_metrics parameter in mlflow.evaluate documentation https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.evaluate
# TODO(optional) : custom_metrics
def custom_metrics():

    # TODO(optional) : define custom metric function to be included in custom_metrics.
    def squared_diff_plus_one(eval_df, _builtin_metrics):
        """
        This example custom metric function creates a metric based on the ``prediction`` and
        ``target`` columns in ``eval_df`.
        """
        return np.sum(np.abs(eval_df["prediction"] - eval_df["target"] + 1) ** 2)

    return [make_metric(eval_fn=squared_diff_plus_one, greater_is_better=False)]


# Define model validation rules. Return empty dict if validation rules are not needed.
# Please refer to validation_thresholds parameter in mlflow.evaluate documentation https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.evaluate
# TODO(optional) : validation_thresholds
def validation_thresholds():
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


# Define evaluator config. Return empty dict if validation rules are not needed.
# Please refer to evaluator_config parameter in mlflow.evaluate documentation https://mlflow.org/docs/latest/python_api/mlflow.html#mlflow.evaluate
# TODO(optional) : evaluator_config
def evaluator_config():
    return {}
