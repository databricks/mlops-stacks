"""
This sample module contains  features logic that can be used to generate and populate tables in Feature Store.
You should plug in your own features computation logic in the compute_features_fn method below.
"""
import pyspark.sql.functions as F
from pyspark.sql.types import FloatType, IntegerType, StringType, TimestampType
from pytz import timezone


@F.udf(returnType=StringType())
def _partition_id(dt):
    # datetime -> "YYYY-MM"
    return f"{dt.year:04d}-{dt.month:02d}"


def _filter_df_by_ts(df, ts_column, start_date, end_date):
    if ts_column and start_date:
        df = df.filter(F.col(ts_column) >= start_date)
    if ts_column and end_date:
        df = df.filter(F.col(ts_column) < end_date)
    return df


def compute_features_fn(input_df, timestamp_column, start_date, end_date):
    """Contains logic to compute features.

    Given an input dataframe and time ranges, this function should compute features, populate an output dataframe and
    return it. This method will be called from a  Feature Store pipeline job and the output dataframe will be written
    to a Feature Store table. You should update this method with your own feature computation logic.

    The timestamp_column, start_date, end_date args are optional but strongly recommended for time-series based
    features.

    TODO: Update and adapt the sample code for your use case

    :param input_df: Input dataframe.
    :param timestamp_column: Column containing a timestamp. This column is used to limit the range of feature
    computation. It is also used as the timestamp key column when populating the feature table, so it needs to be
    returned in the output.
    :param start_date: Start date of the feature computation interval.
    :param end_date:  End date of the feature computation interval.
    :return: Output dataframe containing computed features given the input arguments.
    """
    df = _filter_df_by_ts(input_df, timestamp_column, start_date, end_date)
    pickupzip_features = (
        df.groupBy(
            "pickup_zip", F.window(timestamp_column, "1 hour", "15 minutes")
        )  # 1 hour window, sliding every 15 minutes
        .agg(
            F.mean("fare_amount").alias("mean_fare_window_1h_pickup_zip"),
            F.count("*").alias("count_trips_window_1h_pickup_zip"),
        )
        .select(
            F.col("pickup_zip").alias("zip"),
            F.unix_timestamp(F.col("window.end"))
            .alias(timestamp_column)
            .cast(TimestampType()),
            _partition_id(F.to_timestamp(F.col("window.end"))).alias("yyyy_mm"),
            F.col("mean_fare_window_1h_pickup_zip").cast(FloatType()),
            F.col("count_trips_window_1h_pickup_zip").cast(IntegerType()),
        )
    )
    return pickupzip_features
