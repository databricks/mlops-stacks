# Databricks notebook source
# MAGIC %load_ext autoreload
# MAGIC %autoreload 2
# MAGIC # Enables autoreload; learn more at https://docs.databricks.com/en/files/workspace-modules.html#autoreload-for-python-modules
# MAGIC # To disable autoreload; run %autoreload 0

# COMMAND ----------

# DBTITLE 1,Data Ingestion Pipeline - Overview
###################################################################################
# Data Ingestion Pipeline
#
# This pipeline is designed to process raw documentation data from a specified data source URL.
# The data is stored in a Unity Catalog within a specified database for later processing.
#
# Parameters:
# * uc_catalog (required)                     - Name of the Unity Catalog containing the input data
# * schema (required)                         - Name of the schema inside the Unity Catalog
# * raw_data_table (required)                 - Name of the raw data table inside the database of the Unity Catalog
# * data_source_url (required)                - URL of the data source. Default is "https://docs.databricks.com/en/doc-sitemap.xml"
#
# Widgets:
# * Unity Catalog: Text widget to input the name of the Unity Catalog
# * Schema: Text widget to input the name of the database inside the Unity Catalog
# * Raw data table: Text widget to input the name of the raw data table inside the database of the Unity Catalog
# * Data Source URL: Text widget to input the URL of the data source
#
# Usage:
# 1. Set the appropriate values for the widgets.
# 2. Run the pipeline to collect and store the raw documentation data.
#
##################################################################################

# COMMAND ----------

# DBTITLE 1,Install Prerequisites
# Install prerequisite packages
%pip install -r ../../requirements.txt

# COMMAND ----------

# DBTITLE 1,Widget creation
# List of input args needed to run this notebook as a job
# Provide them via DB widgets or notebook arguments in your DAB resources

# A Unity Catalog containing the input data
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
# Name of raw data table
dbutils.widgets.text(
    "raw_data_table",
    "raw_documentation",
    label="Raw data table",
)

# Data source url
dbutils.widgets.text(
    "data_source_url",
    "https://docs.databricks.com/en/doc-sitemap.xml",
    label="Data Source URL",
)

# COMMAND ----------

# DBTITLE 1,Define input and output variables
uc_catalog = dbutils.widgets.get("uc_catalog")
schema = dbutils.widgets.get("schema")
raw_data_table = dbutils.widgets.get("raw_data_table")
data_source_url = dbutils.widgets.get("data_source_url")

assert uc_catalog != "", "uc_catalog notebook parameter must be specified"
assert schema != "", "schema notebook parameter must be specified"
assert raw_data_table != "", "raw_data_table notebook parameter must be specified"
assert data_source_url != "", "data_source_url notebook parameter must be specified"

# COMMAND ----------

# DBTITLE 1,Set up path to import utilities
# Set up path to import utility and other helper functions
import sys
import os

# Get notebook's directory using dbutils
notebook_path = '/Workspace/' + os.path.dirname(
    dbutils.notebook.entry_point.getDbutils().notebook()
    .getContext().notebookPath().get()
)
# Navigate up from notebooks/ to component level (data_ingestion/)
utils_dir = os.path.dirname(notebook_path)
sys.path.insert(0, utils_dir)

# COMMAND ----------

# DBTITLE 1,Use the catalog and database specified in the notebook parameters
spark.sql(f"""CREATE SCHEMA IF NOT EXISTS `{uc_catalog}`.`{schema}`""")

spark.sql(f"""USE `{uc_catalog}`.`{schema}`""")

# COMMAND ----------

# DBTITLE 1,Download and store data to UC
from utils.fetch_data import fetch_data_from_url

if not spark.catalog.tableExists(f"{raw_data_table}") or spark.table(f"{raw_data_table}").isEmpty():
    # Download the data to a DataFrame 
    doc_articles = fetch_data_from_url(spark, data_source_url)

    #Save them as to unity catalog
    doc_articles.write.mode('overwrite').saveAsTable(f"{raw_data_table}")

    doc_articles.display()


# COMMAND ----------

dbutils.notebook.exit(0)