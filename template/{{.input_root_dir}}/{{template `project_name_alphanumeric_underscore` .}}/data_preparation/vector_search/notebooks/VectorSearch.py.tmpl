# Databricks notebook source
# MAGIC %load_ext autoreload
# MAGIC %autoreload 2
# MAGIC # Enables autoreload; learn more at https://docs.databricks.com/en/files/workspace-modules.html#autoreload-for-python-modules
# MAGIC # To disable autoreload; run %autoreload 0

# COMMAND ----------

# DBTITLE 1,Vector Search Pipeline - Overview
###################################################################################
# Vector Search
#
# This notebook creates a Vector Search index from a table containing chunked documents.
#
# Parameters:
# * uc_catalog (required)                     - Name of the Unity Catalog
# * schema (required)                         - Name of the schema inside Unity Catalog
# * preprocessed_data_table (required)        - Name of the preprocessed data table inside database of Unity Catalog
# * vector_search_endpoint (required)         - Name of the Vector Search endpoint
#
# Widgets:
# * Vector Search endpoint: Text widget to input the name of the Vector Search endpoint
# * Unity Catalog: Text widget to input the name of the Unity Catalog
# * Schema: Text widget to input the name of the database inside the Unity Catalog
# * Preprocessed data table: Text widget to input the name of the preprocessed data table inside the database of Unity Catalog
#
# Usage:
# 1. Set the appropriate values for the widgets.
# 2. Run the pipeline to set up the vector search endpoint.
# 3. Create index.
#
##################################################################################

# COMMAND ----------

# DBTITLE 1,Install Prerequisites
# Install prerequisite packages
%pip install -r ../../requirements.txt

# COMMAND ----------

# DBTITLE 1,Widget Creation
# List of input args needed to run this notebook as a job.
# Provide them via DB widgets or notebook arguments in your DAB resources.

# A Unity Catalog location containing the input data
dbutils.widgets.text(
    "uc_catalog",
    "",
    label="Unity Catalog",
)
# Name of schema
dbutils.widgets.text(
    "schema",
    "",
    label="Schema",
)
# Name of preprocessed data table
dbutils.widgets.text(
    "preprocessed_data_table",
    "databricks_documentation",
    label="Preprocessed data table",
)
# A Vector Search Endpoint for retrieving processed data
dbutils.widgets.text(
    "vector_search_endpoint",
    "ai_agent_endpoint",
    label="Vector Search endpoint",
)


# COMMAND ----------

# DBTITLE 1,Define variables
vector_search_endpoint = dbutils.widgets.get("vector_search_endpoint")
uc_catalog = dbutils.widgets.get("uc_catalog")
schema = dbutils.widgets.get("schema")
preprocessed_data_table = dbutils.widgets.get("preprocessed_data_table")

assert vector_search_endpoint != "", "vector_search_endpoint notebook parameter must be specified"
assert uc_catalog != "", "uc_catalog notebook parameter must be specified"
assert schema != "", "schema notebook parameter must be specified"
assert preprocessed_data_table != "", "preprocessed_data_table notebook parameter must be specified"

# COMMAND ----------

# DBTITLE 1,Set up path to import utility functions
import sys
import os

# Get notebook's directory using dbutils
notebook_path = '/Workspace/' + os.path.dirname(
    dbutils.notebook.entry_point.getDbutils().notebook()
    .getContext().notebookPath().get()
)
# Navigate up from notebooks/ to component level
utils_dir = os.path.dirname(notebook_path)
sys.path.insert(0, utils_dir)

# COMMAND ----------

# DBTITLE 1,Initialize endpoint
from databricks.vector_search.client import VectorSearchClient
from utils.vector_search_utils import vs_endpoint_exists, wait_for_vs_endpoint_to_be_ready

vsc = VectorSearchClient(disable_notice=True)

if not vs_endpoint_exists(vsc, vector_search_endpoint):
    vsc.create_endpoint(name=vector_search_endpoint, endpoint_type="STANDARD")

# this may throw an error on the first pass, once the endpoint is created we'd see correct messages
wait_for_vs_endpoint_to_be_ready(vsc, vector_search_endpoint)
print(f"Endpoint named {vector_search_endpoint} is ready.")

# COMMAND ----------

# DBTITLE 1,Create Index
from utils.vector_search_utils import index_exists, wait_for_index_to_be_ready
from databricks.sdk import WorkspaceClient
import databricks.sdk.service.catalog as c

# The table we'd like to index
source_table_fullname = f"{uc_catalog}.{schema}.{preprocessed_data_table}"

# Where we want to store our index
vs_index_fullname = f"{uc_catalog}.{schema}.{preprocessed_data_table}_vs_index"

if not index_exists(vsc, vector_search_endpoint, vs_index_fullname):
  print(f"Creating index {vs_index_fullname} on endpoint {vector_search_endpoint}...")
  vsc.create_delta_sync_index(
    endpoint_name=vector_search_endpoint,
    index_name=vs_index_fullname,
    source_table_name=source_table_fullname,
    pipeline_type="TRIGGERED",
    primary_key="id",
    embedding_source_column="content", # The column containing our text
    embedding_model_endpoint_name="databricks-gte-large-en" # The embedding endpoint used to create the embeddings
  )
  #Let's wait for the index to be ready and all our embeddings to be created and indexed
  vsc.get_index(vector_search_endpoint, vs_index_fullname).wait_until_ready()
else:
  #Trigger a sync to update our vs content with the new data saved in the table
  vsc.get_index(vector_search_endpoint, vs_index_fullname).sync()

print(f"Index {vs_index_fullname} on table {source_table_fullname} is ready")

# COMMAND ----------

# DBTITLE 1,Test if Index Online
import databricks
import time
from utils.vector_search_utils import check_index_online

vector_index=vsc.get_index(endpoint_name=vector_search_endpoint, index_name=vs_index_fullname)

check_index_online(vs_index_fullname, vector_index)