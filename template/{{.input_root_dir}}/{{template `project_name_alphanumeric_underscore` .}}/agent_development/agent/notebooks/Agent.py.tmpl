# Databricks notebook source
# MAGIC %load_ext autoreload
# MAGIC %autoreload 2
# MAGIC # Enables autoreload; learn more at https://docs.databricks.com/en/files/workspace-modules.html#autoreload-for-python-modules
# MAGIC # To disable autoreload; run %autoreload 0

# COMMAND ----------

# DBTITLE 1,Agent Creation Pipeline - Overview
###################################################################################
# Agent Chain Creation
#
# This notebook shows an example of a RAG-based Agent with multiple retrievers.
#
# Parameters:
# * uc_catalog (required)                     - Name of the Unity Catalog
# * schema (required)                         - Name of the schema inside Unity Catalog
# * vector_search_endpoint (required)         - Name of the vector search endpoint
# * vector_search_index (required)            - Name of the vector search index
# * model_serving_endpopint (required)        - Name of the model endpoint to serve
# * foundation_model_endpoint (required)      - Name and Identifier of the foundation model endpoint
# * experiment (required)                     - Name of the experiment to register the run under
# * registered_model (required)               - Name of the model to register in mlflow
# * max_words (required)                      - Maximum number of words to return in the response
# * model_alias (required)                    - Alias to give to newly registered model
#
# Widgets:
# * Unity Catalog: Text widget to input the name of the Unity Catalog
# * Schema: Text widget to input the name of the database inside the Unity Catalog
# * Vector Search endpoint: Text widget to input the name of the vector search endpoint
# * Vector search index: Text widget to input the name of the vector search index
# * Agent model endppoint: Text widget to input the name of the agent model endpoint
# * Experiment: Text widget to input the name of the experiment to register the run under
# * Registered model name: Text widget to input the name of the model to register in mlflow
# * Max words: Text widget to input the maximum integer number of words to return in the response
# * Model Alias: Text widget to input the alias of the model to register in mlflow
#
# Usage:
# 1. Set the appropriate values for the widgets.
# 2. Run the pipeline to create and register an agent with tool calling.
#
##################################################################################

# COMMAND ----------

# DBTITLE 1,Install Prerequisites
# Install prerequisite packages
%pip install -r ../../agent_requirements.txt

# COMMAND ----------

# DBTITLE 1,Widget Creation
# List of input args needed to run this notebook as a job
# Provide them via DB widgets or notebook arguments

# A Unity Catalog containing the preprocessed data
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
# Name of vector search endpoint containing the preprocessed index
dbutils.widgets.text(
    "vector_search_endpoint",
    "ai_agent_endpoint",
    label="Vector Search endpoint",
)
# Name of vector search index containing the preprocessed index
dbutils.widgets.text(
    "vector_search_index",
    "databricks_documentation_vs_index",
    label="Vector Search index",
)
# Foundation model to use
dbutils.widgets.text(
    "foundation_model_endpoint",
    "databricks-meta-llama-3-3-70b-instruct",
    label="Foundation model endpoint",
)
# Name of experiment to register under in mlflow
dbutils.widgets.text(
    "experiment",
    "/agent_function_chatbot",
    label="Experiment name",
)
# Name of model to register in mlflow
dbutils.widgets.text(
    "registered_model",
    "agent_function_chatbot",
    label="Registered model name",
)
# Max words for summarization
dbutils.widgets.text(
    "max_words",
    "20",
    label="Max Words",
)
# Model alias
dbutils.widgets.text(
    "model_alias",
    "agent_latest",
    label="Model Alias",
)

# COMMAND ----------

# DBTITLE 1,Define Input Variables
uc_catalog = dbutils.widgets.get("uc_catalog")
schema = dbutils.widgets.get("schema")
vector_search_endpoint = dbutils.widgets.get("vector_search_endpoint")
vector_search_index = dbutils.widgets.get("vector_search_index")
foundation_model_endpoint = dbutils.widgets.get("foundation_model_endpoint")
experiment = dbutils.widgets.get("experiment")
registered_model = dbutils.widgets.get("registered_model")
max_words = dbutils.widgets.get("max_words")
model_alias = dbutils.widgets.get("model_alias")

assert uc_catalog != "", "uc_catalog notebook parameter must be specified"
assert schema != "", "schema notebook parameter must be specified"
assert vector_search_endpoint != "", "vector_search_endpoint notebook parameter must be specified"
assert vector_search_index != "", "vector_search_index notebook parameter must be specified"
assert foundation_model_endpoint != "", "foundation_model_endpoint notebook parameter must be specified"
assert experiment != "", "experiment notebook parameter must be specified"
assert registered_model != "", "registered_model notebook parameter must be specified"
assert max_words != "", "max_words notebook parameter must be specified"
assert model_alias != "", "model_alias notebook parameter must be specified"

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

# Import agent configuration constants
from utils.config import MAX_WORDS
max_words = MAX_WORDS

# COMMAND ----------

# DBTITLE 1,Create a DatabricksFunctionClient and set as default
from unitycatalog.ai.core.base import set_uc_function_client
from unitycatalog.ai.core.databricks import DatabricksFunctionClient

client = DatabricksFunctionClient()

# sets the default uc function client
set_uc_function_client(client)


# COMMAND ----------

# DBTITLE 1, Create UC functions
from utils.ai_tools import (ask_ai_function, summarization_function, translate_function)

ask_ai_function_name = f"{uc_catalog}.{schema}.ask_ai"
function_info = client.create_function(sql_function_body = ask_ai_function.format(ask_ai_function_name = ask_ai_function_name))

summarization_function_name = f"{uc_catalog}.{schema}.summarize"
function_info = client.create_function(sql_function_body = summarization_function.format(summarization_function_name = summarization_function_name))

translate_function_name = f"{uc_catalog}.{schema}.translate"
function_info = client.create_function(sql_function_body = translate_function.format(translate_function_name = translate_function_name))

# COMMAND ----------
# DBTITLE 1, Create a model config

import yaml

config = {
    'llm_config': {
        'endpoint': foundation_model_endpoint,
        'max_tokens': 500,
        'temperature': 0.01,
    },
    'catalog': uc_catalog,
    'schema': schema,
    'system_prompt': "You are a Databricks expert.",
    'vector_search_config': {
        'vector_search_index': vector_search_index,
        'embedding_model': 'databricks-gte-large-en',
        'num_results': 1,
        'columns': ['url', 'content'],
        'query_type': 'ANN'
    }
}

with open('ModelConfig.yml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

# COMMAND ----------
# DBTITLE 1,Test Agent Before Logging

from app import AGENT

# Test the agent directly with a sample query
test_question = "What is Databricks?"
print(f"Testing agent with question: {test_question}")
print("="*80)

test_answer = AGENT.predict({"input": [{"role": "user", "content": test_question}]})
print(f"Answer: {test_answer}")
print("="*80)
print("Agent test completed. Check MLflow trace in the experiment UI to verify tool execution.")

# COMMAND ----------
# DBTITLE 1, Log agent with resources

import mlflow
from importlib.metadata import version

mlflow.set_experiment(experiment)

with mlflow.start_run():
    model_info = mlflow.pyfunc.log_model(
        python_model="app.py",
        name="model",
        model_config="ModelConfig.yml",
        input_example={"input": [{"role": "user", "content": "What is Databricks?"}]},
        resources=AGENT.get_resources(),
        extra_pip_requirements=["databricks-connect"]
    )

# COMMAND ----------

# DBTITLE 1,Test Loaded Model

import pandas as pd

# Load the model from MLflow
loaded_model = mlflow.pyfunc.load_model(f"runs:/{model_info.run_id}/model")

# Test with a sample question
test_question = "What is Databricks?"
print(f"Testing loaded model with question: {test_question}")
print("="*80)

model_input = pd.DataFrame({
    "input": [[{"role": "user", "content": test_question}]]
})
response = loaded_model.predict(model_input)

print(f"Answer: {response}")
print("="*80)
print("Loaded model test completed. Check MLflow trace in the experiment UI to verify tool execution.")

# COMMAND ----------

# DBTITLE 1,Register model and set alias
from mlflow import MlflowClient

# Initialize MLflow client
client_mlflow = MlflowClient()

registered_model_name = f"{uc_catalog}.{schema}.{registered_model}"
uc_registered_model_info = mlflow.register_model(model_info.model_uri,
                                                 name=registered_model_name,
                                                 env_pack="databricks_model_serving") # Optimized deployment: only for Serverless Env 3

# Set an alias for new version of the registered model to retrieve it for model serving
client_mlflow.set_registered_model_alias(f"{uc_catalog}.{schema}.{registered_model}", model_alias, uc_registered_model_info.version)

# COMMAND ----------

# DBTITLE 1,Final Summary
print("="*80)
print("Agent Development Complete")
print("="*80)
print(f"Model registered: {registered_model_name}")
print(f"Model version: {uc_registered_model_info.version}")
print(f"Model alias: {model_alias}")
print(f"MLflow run ID: {model_info.run_id}")
print("="*80)

# COMMAND ----------

# DBTITLE 1,Exit Notebook
dbutils.notebook.exit("Agent created")