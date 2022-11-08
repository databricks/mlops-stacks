"""
This module defines the following routines used by the 'transform' step of the regression recipe:

- ``transformer_fn``: Defines customizable logic for transforming input data before it is passed
  to the estimator during model inference.
"""

from pandas import DataFrame
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, FunctionTransformer


def calculate_features(df: DataFrame):
    """
    Extend the input dataframe with pickup day of week and hour, and trip duration.
    Drop the now-unneeded pickup datetime and dropoff datetime columns.
    """
    df["pickup_dow"] = df["tpep_pickup_datetime"].dt.dayofweek
    df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour
    trip_duration = df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]
    df["trip_duration"] = trip_duration.map(lambda x: x.total_seconds() / 60)
    df.drop(columns=["tpep_pickup_datetime", "tpep_dropoff_datetime"], inplace=True)
    return df


def transformer_fn():
    """
    Returns an *unfitted* transformer that defines ``fit()`` and ``transform()`` methods.
    The transformer's input and output signatures should be compatible with scikit-learn
    transformers.
    """
    return Pipeline(
        steps=[
            (
                "calculate_time_and_duration_features",
                FunctionTransformer(calculate_features, feature_names_out="one-to-one"),
            ),
            (
                "encoder",
                ColumnTransformer(
                    transformers=[
                        (
                            "hour_encoder",
                            OneHotEncoder(categories="auto", sparse=False),
                            ["pickup_hour"],
                        ),
                        (
                            "day_encoder",
                            OneHotEncoder(categories="auto", sparse=False),
                            ["pickup_dow"],
                        ),
                        (
                            "std_scaler",
                            StandardScaler(),
                            ["trip_distance", "trip_duration"],
                        ),
                    ]
                ),
            ),
        ]
    )
