# Databricks notebook source
##################################################################################
# Batch Inference Notebook
#
# This notebook is an example of applying a model for batch inference against an input delta table,
# writing output to a delta table. It's scheduled as a batch inference job defined under ``databricks-config``
#
# Parameters:
#
#  * env (optional)  - String name of the current environment (dev, staging, or prod). Defaults to "dev"
#  * input_table_name (required)  - Delta table name containing your input data.
#  * output_table_name (required) - Delta table name where the predictions will be written to.
#                                   Note that this will create a new version of the Delta table if
#                                   the table already exists
##################################################################################


# List of input args needed to run the notebook as a job.
# Provide them via DB widgets or notebook arguments.
#
# Name of the current environment
dbutils.widgets.dropdown("env", "dev", ["dev", "staging", "prod"], "Environment Name")
# A Hive-registered Delta table containing the input features.
dbutils.widgets.text("input_table_name", "", label="Input Table Name")
# Delta table to store the output predictions.
dbutils.widgets.text("output_table_name", "", label="Output Table Name")

# COMMAND ----------

# MAGIC %pip install -r ../requirements.txt

# COMMAND ----------

import sys

sys.path.append("../steps")

# COMMAND ----------

# DBTITLE 1,Define input and output variables
from utils import get_deployed_model_stage_for_env, get_model_name

env = dbutils.widgets.get("env")
input_table_name = dbutils.widgets.get("input_table_name")
output_table_name = dbutils.widgets.get("output_table_name")
assert input_table_name != "", "input_table_name notebook parameter must be specified"
assert output_table_name != "", "output_table_name notebook parameter must be specified"

model_name = get_model_name(env)
model_uri = f"models:/{model_name}/{get_deployed_model_stage_for_env(env)}"

# COMMAND ----------

# DBTITLE 1,Load model and run inference
from predict import predict_batch

predict_batch(spark, model_uri, input_table_name, output_table_name)
dbutils.notebook.exit(output_table_name)
