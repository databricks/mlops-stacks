# This file is used for the main SQL query that checks the last {num_evaluation_windows} metric violations and whether at least {num_violation_windows} of those runs violate the condition.

import sys
import pathlib

sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.resolve()))

"""The SQL query is divided into three main parts. The first part selects the top {num_evaluation_windows}
values of the metric to be monitored, ordered by the time window, and saves as recent_metrics.
```sql
WITH recent_metrics AS (
  SELECT
    {metric_to_monitor},
    window
  FROM
    {table_name_under_monitor}_profile_metrics
  WHERE
    column_name = ":table"
    AND slice_key IS NULL
    AND model_id != "*"
    AND log_type = "INPUT"
  ORDER BY
    window DESC
  LIMIT
    {num_evaluation_windows}
)
```
The `column_name = ":table"` and `slice_key IS NULL` conditions ensure that the metric
is selected for the entire table within the given granularity. The `log_type = "INPUT"`
condition ensures that the primary table metrics are considered, but not the baseline
table metrics. The `model_id!= "*"` condition ensures that the metric aggregated across
all model IDs is not selected.

The second part of the query determines if the metric values have been violated with two cases. 
The first case checks if the metric value is greater than the threshold for at least {num_violation_windows} windows:
```sql
(SELECT COUNT(*) FROM recent_metrics WHERE {metric_to_monitor} > {metric_violation_threshold}) >= {num_violation_windows}
```
The second case checks if the most recent metric value is greater than the threshold. This is to make sure we only trigger retraining
if the most recent window was violated, avoiding unnecessary retraining if the violation was in the past and the metric is now within the threshold:
```sql
(SELECT {metric_to_monitor} FROM recent_metrics ORDER BY window DESC LIMIT 1) > {metric_violation_threshold}
```

The final part of the query sets the `query_result` to 1 if both of the above conditions are met, and 0 otherwise:
```sql
SELECT
  CASE
    WHEN
      # Check if the metric value is greater than the threshold for at least {num_violation_windows} windows
      AND
      # Check if the most recent metric value is greater than the threshold
    THEN 1
    ELSE 0
  END AS query_result
```
"""

sql_query = """WITH recent_metrics AS (
  SELECT
    {metric_to_monitor},
    window
  FROM
    {table_name_under_monitor}_profile_metrics
  WHERE
    column_name = ":table"
    AND slice_key IS NULL
    AND model_id != "*"
    AND log_type = "INPUT"
  ORDER BY
    window DESC
  LIMIT
    {num_evaluation_windows}
)
SELECT
  CASE
    WHEN
      (SELECT COUNT(*) FROM recent_metrics WHERE {metric_to_monitor} > {metric_violation_threshold}) >= {num_violation_windows}
      AND
      (SELECT {metric_to_monitor} FROM recent_metrics ORDER BY window DESC LIMIT 1) > {metric_violation_threshold}
    THEN 1
    ELSE 0
  END AS query_result
"""
