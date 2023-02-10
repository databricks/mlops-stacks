"""
This sample module contains features logic that can be used to generate and populate tables in Feature Store. 
You should plug in your own features computation logic in the compute_features_fn method below.
"""
from pyspark.sql.functions import *
from pyspark.sql.types import IntegerType, StringType, TimestampType
from pytz import timezone


@udf(returnType=IntegerType())
def _is_weekend(dt):
    tz = "America/New_York"
    return int(dt.astimezone(timezone(tz)).weekday() >= 5)  # 5 = Saturday, 6 = Sunday


@udf(returnType=StringType())
def _partition_id(dt):
    # datetime -> "YYYY-MM"
    return f"{dt.year:04d}-{dt.month:02d}"


def _filter_df_by_ts(df, ts_column, start_date, end_date):
    if ts_column and start_date:
        df = df.filter(col(ts_column) >= start_date)
    if ts_column and end_date:
        df = df.filter(col(ts_column) < end_date)
    return df


def compute_features_fn(input_df, timestamp_column, start_date, end_date):
    """
     Contains logic to compute features.
 
     Given an input dataframe and time ranges, this function should compute features, populate an output dataframe and
     return it. This method will be called from a  Feature Store pipeline job and the output dataframe will be written
     to a Feature Store table. You should update this method with your own feature computation logic.
 
     The timestamp_column, start_date, end_date args are optional but strongly recommended for time-series based
     features.

     :param input_df: Input dataframe.
     :param timestamp_column: Column containing the timestamp. This column is used to limit the range of feature
     computation. It is also used as the timestamp key column when populating the feature table, so it needs to be
     returned in the output.
     :param start_date: Start date of the feature computation interval.
     :param end_date:  End date of the feature computation interval.
     :return: Output dataframe containing computed features given the input arguments.
    """
    df = _filter_df_by_ts(
        input_df,  timestamp_column, start_date, end_date
    )
    dropoffzip_features = (
        df.groupBy("dropoff_zip", window(timestamp_column, "30 minute"))
            .agg(count("*").alias("count_trips_window_30m_dropoff_zip"))
            .select(
            col("dropoff_zip").alias("zip"),
            unix_timestamp(col("window.end")).alias(timestamp_column).cast(TimestampType()),
            _partition_id(to_timestamp(col("window.end"))).alias("yyyy_mm"),
            col("count_trips_window_30m_dropoff_zip").cast(IntegerType()),
            _is_weekend(col("window.end")).alias("dropoff_is_weekend"),
        )
    )
    return dropoffzip_features
