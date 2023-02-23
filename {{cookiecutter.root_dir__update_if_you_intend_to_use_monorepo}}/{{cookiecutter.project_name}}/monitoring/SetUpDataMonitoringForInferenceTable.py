# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC # Data Monitoring for Inference Table
# MAGIC see monitoring/README.md for details

# COMMAND ----------

# Install the Data Monitoring client library
# TODO: Fill in wheel URL
%pip install "{wheel_URL}"

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC ### Required Fields
# MAGIC TODO: Fill in and review required fields

# COMMAND ----------

# The name of the column that represents the inference timestamp (i.e. time of prediction) for this row. This column should be of TimestampType.
# By default, BatchInference notebook generates the column with name `inference_timestamp`.
timestamp_col = "inference_timestamp"

# The name of the column that represents the model version used to predict on this row. 
# This should correspond to the MLflow registered model version (or any identifier unique to a specific trained model).
# By default, BatchInference notebook generates the column with name `model_version`.
model_version_col = "model_version"

# The name of the column that holds the prediction (from inference) for this row.
# By default, BatchInference notebook generates the column with name `prediction`.
prediction_col = "prediction"

# The type of ML problem that the model is solving. This should be either “classification” or “regression”.
# Other problem types are not supported at this time. 
problem_type = "regression"

# The inference table holding data to be monitored. Table name format {catalog}.{schema}.{table}
inference_table_name = "{catalog}.{schema}.{table}"

# Name of the schema in which to create output tables. format {catalog}.{schema}
output_schema_name = "{catalog}.{schema}"

# List of granularities to use when aggregating data
# into time windows based on their timestamp. Currently the following static granularities are supported:
# {"5 minutes", "30 minutes", "1 hour", "1 day", "n week(s)", "1 month", "1 year"}.
granularities = ["1 hour"]

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC ### Optional Fields
# MAGIC TODO: Fill in optional fields as needed

# COMMAND ----------

# List of Databricks entity names that are associated
# with this table. Only following entities are supported:
#    ["models:/registry_model_name"] links a model registry model to the monitored table.
# Update the parameter if model name has been updated after generating the project.
linked_entities = ["models:/prod-{{cookiecutter.model_name}}"]

# The name of the column that holds the label for this row. This field is optional if you do not have labels to provide with your data.
# This column will be used to compute model quality metrics
label_col = None

# The name of the column that holds the example ID for this row. This might be a unique identifier attached to each inference 
# or some other identifier you don’t want analyzed as a feature. The provided column will be ignored during analysis. 
example_id_col = None

# A table containing baseline data for comparison. The baseline table is expected to match the schema of the monitored table
# If columns are missing on either side then monitoring will use best-effort heuristics to compute the output metrics.
baseline_table_name = None

# data_monitoring_dir = "/Users/first.last@company.com" The absolute path to user-configurable directory for storing data monitoring assets.
# The path must be pointing to an existing directory. If provided, the assets will be created under:
#         "{data_monitoring_dir}/{table_name}"
# Otherwise, the assets will be stored under the default directory:
#         "/Users/{user_name}/databricks_data_monitoring/{table_name}"
# Note that this directory can exist anywhere, including "/Shared/" or other locations outside of the /Users/ 
# directory; this can be useful when configuring a production monitor intended to be shared within an organization.
data_monitoring_dir = None

# List of column expressions to slice data with for targeted analysis. The data is grouped by each expression independently,
# resulting in a separate slice for each predicate and its complements. For example `slicing_exprs=["col_1", "col_2 > 10"]` will generate the
# following slices: two slices for `col_2 > 10` (True and False), and one slice per unique value in `col1`. For high-cardinality columns, only the
# top 100 unique values by frequency will generate slices.
slicing_exprs = None

# A list of custom metrics to compute alongside existing aggregate, derived, and drift metrics.
custom_metrics = []

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC ### Create (or update) a monitor

# COMMAND ----------

import databricks.data_monitoring as dm

inference_analysis = dm.analysis.InferenceLog(
    timestamp_col=timestamp_col,
    model_version_col=model_version_col,
    prediction_col=prediction_col,
    problem_type=problem_type,
    label_col=label_col,
    example_id_col=example_id_col
)
dm.create_or_update_monitor(
    table_name=inference_table_name,
    analysis_type=inference_analysis,
    granularities=granularities,
    output_schema_name=output_schema_name,
    baseline_table_name=baseline_table_name,
    custom_metrics=custom_metrics,
    linked_entities=linked_entities,
    skip_analysis=True,
    data_monitoring_dir=data_monitoring_dir
)

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ### Refresh metrics

# COMMAND ----------

dm.refresh_metrics(
    table_name = inference_table_name
)
