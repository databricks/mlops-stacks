# Databricks notebook source
# MAGIC %load_ext autoreload
# MAGIC %autoreload 2
# MAGIC # Enables autoreload; learn more at https://docs.databricks.com/en/files/workspace-modules.html#autoreload-for-python-modules
# MAGIC # To disable autoreload; run %autoreload 0

# COMMAND ----------

# DBTITLE 1,Agent Evaluation Pipeline - Overview
##################################################################################
# Agent Evaluation
#
# Notebook that downloads an evaluation dataset and evaluates the model using
# llm-as-a-judge with the Databricks agent framework.
#
# Parameters:
# * uc_catalog (required)           - Name of the Unity Catalog
# * schema (required)               - Name of the schema inside Unity Catalog
# * eval_table (required)           - Name of the table containing the evaluation dataset
# * experiment (required)           - Name of the experiment to register the run under
# * registered_model (required)     - Name of the model registered in mlflow
# * model_alias (required)          - Model alias to deploy
#
# Widgets:
# * Unity Catalog: Text widget to input the name of the Unity Catalog
# * Schema: Text widget to input the name of the database inside the Unity Catalog
# * Evaluation Table: Text widget to input the name of the table containing the evaluation dataset
# * Experiment: Text widget to input the name of the experiment to register the run under
# * Registered model name: Text widget to input the name of the model to register in mlflow
# * Model Alias: Text widget to input the model alias to deploy
#
# Usage:
# 1. Set the appropriate values for the widgets.
# 2. Run to evaluate your agent.
#
##################################################################################

# COMMAND ----------

# DBTITLE 1,Install Prerequisites and Restart Python
# Install prerequisite packages
%pip install -r ../../agent_requirements.txt
dbutils.library.restartPython()

# COMMAND ----------

# DBTITLE 1,Widget Creation
# List of input args needed to run the notebook as a job.
# Provide them via DB widgets or notebook arguments.

# A Unity Catalog containing the model
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
# Name of evaluation table
dbutils.widgets.text(
    "eval_table",
    "databricks_documentation_eval",
    label="Evaluation dataset",
)
# Name of experiment to register under in mlflow
dbutils.widgets.text(
    "experiment",
    "/agent_function_chatbot",
    label="Experiment name",
)
# Name of model registered in mlflow
dbutils.widgets.text(
    "registered_model",
    "agent_function_chatbot",
    label="Registered model name",
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
eval_table = dbutils.widgets.get("eval_table")
experiment = dbutils.widgets.get("experiment")
registered_model = dbutils.widgets.get("registered_model")
model_alias = dbutils.widgets.get("model_alias")

assert uc_catalog != "", "uc_catalog notebook parameter must be specified"
assert schema != "", "schema notebook parameter must be specified"
assert eval_table != "", "eval_table notebook parameter must be specified"
assert experiment != "", "experiment notebook parameter must be specified"
assert registered_model != "", "registered_model notebook parameter must be specified"
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

# COMMAND ----------

# DBTITLE 1,Get Reference Documentation and Prepare for Dataset
import pandas as pd
from pyspark.sql import SparkSession

# Initialize Spark session if not already available
try:
    spark
except NameError:
    spark = SparkSession.builder.getOrCreate()

# Download the reference documentation from Databricks demos
print("Loading reference documentation from Databricks demos...")
ref_docs_df = pd.read_parquet(
    'https://notebooks.databricks.com/demos/dbdemos-dataset/llm/databricks-documentation/databricks_doc_eval_set.parquet'
)

print(f"Loaded {len(ref_docs_df)} reference documents")
display(ref_docs_df.head())

# COMMAND ----------

# DBTITLE 1,Transform Data to MLflow 3.x Evaluation Dataset Format
# Transform the reference docs into the correct format for MLflow 3.x
# According to the docs, each record needs 'inputs' and 'expected' (or 'expectations') fields

evaluation_records = []
for idx, row in ref_docs_df.head(100).iterrows():
    record = {
        "inputs": {
            "question": row.get('request', '')
        },
        "expected": {
            "expected_response": row.get('expected_response', '')
        }
    }
    evaluation_records.append(record)

print(f"Transformed {len(evaluation_records)} records for evaluation dataset")
print("\nSample record structure:")
print(evaluation_records[0])

# COMMAND ----------

# DBTITLE 1,Create Evaluation Dataset
import mlflow.genai.datasets

# Construct the fully qualified table name
dataset_name = f"{uc_catalog}.{schema}.{eval_table}"

try:
  eval_dataset = mlflow.genai.datasets.get_dataset(dataset_name)
except Exception as e:
  if 'does not exist' in str(e):
    eval_dataset = mlflow.genai.datasets.create_dataset(dataset_name)
    # Add your examples to the evaluation dataset
    eval_dataset.merge_records(evaluation_records)
    print("Added records to the evaluation dataset.")


# COMMAND ----------

# DBTITLE 1,Display Eval Dataset
# Preview the dataset
print("\nDataset preview:")
dataset_df = eval_dataset.to_df()
display(dataset_df)

# COMMAND ----------

# DBTITLE 1,Load Model and Create Prediction Wrapper
import mlflow
import pandas as pd

# Set experiment
mlflow.set_experiment(experiment)

# Load the model
model_uri = f"models:/{uc_catalog}.{schema}.{registered_model}@{model_alias}"
loaded_model = mlflow.pyfunc.load_model(model_uri)

# Create a simple prediction wrapper that extracts the final answer
def predict_wrapper(question):
    """
    Simple prediction wrapper for evaluation.
    Takes a question string, returns the answer string.
    """
    # Format input for the model
    model_input = pd.DataFrame({
        "input": [[{"role": "user", "content": question}]]
    })
    response = loaded_model.predict(model_input)

    # Extract the final text response from the output
    # The output is a list of items (function calls, tool outputs, messages)
    # We need to find the last message with type='message' and role='assistant'
    for item in reversed(response['output']):
        if item.get('type') == 'message' and item.get('role') == 'assistant':
            # Content can be a list or a string
            content = item['content']
            if isinstance(content, list):
                # Get the last text content item
                for c in reversed(content):
                    if c.get('type') == 'text':
                        return c['text']
            elif isinstance(content, str):
                return content

    # Fallback to the original extraction method if the above doesn't work
    return response['output'][-1]['content'][-1]['text']

# COMMAND ----------

# DBTITLE 1,Test predict_wrapper with a sample question
# Test the wrapper with a sample question to inspect the response
test_question = "What is Databricks?"
print(f"Testing with question: {test_question}")
print("\n" + "="*80)

test_input = pd.DataFrame({
    "input": [[{"role": "user", "content": test_question}]]
})
test_response = loaded_model.predict(test_input)

print("Raw response structure:")
print(f"Response keys: {test_response.keys()}")
print(f"\nNumber of output items: {len(test_response['output'])}")
print("\nOutput items:")
for i, item in enumerate(test_response['output']):
    print(f"\n[{i}] Type: {item.get('type')}, Role: {item.get('role', 'N/A')}")
    if 'content' in item:
        content = item['content']
        if isinstance(content, list):
            print(f"    Content: list with {len(content)} items")
            for j, c in enumerate(content):
                if isinstance(c, dict):
                    print(f"      [{j}] {c.get('type', 'unknown')}: {str(c.get('text', c))[:100]}...")
                else:
                    print(f"      [{j}] {str(c)[:100]}...")
        else:
            print(f"    Content: {str(content)[:100]}...")

print("\n" + "="*80)
print(f"Extracted answer: {predict_wrapper(test_question)}")
print("="*80)

# COMMAND ----------

# DBTITLE 1,Define Evaluation Scorers
import mlflow

# For MLflow 3.5.1, scorers are typically defined using mlflow.metrics or custom functions
# We'll use built-in metrics and custom judges

def get_scorers():
    """
    Define evaluation scorers for agent evaluation.
    In MLflow 3.5.1, we use make_genai_metric for custom LLM-as-judge metrics.
    """
    scorers = []

    try:
        # Try importing the genai scorers (may vary by MLflow version)
        from mlflow.metrics.genai import answer_relevance, faithfulness, answer_correctness

        scorers.extend([
            answer_relevance,  # Checks if response addresses the user's query
            faithfulness,  # Checks if response is grounded in retrieved context
            answer_correctness,  # Compares response against expected answer
        ])
    except ImportError:
        print("Note: Some genai metrics may not be available in this MLflow version")
        print("Evaluation will proceed with available metrics")

    # Add any custom metrics if needed
    try:
        from mlflow.metrics.genai import make_genai_metric, EvaluationExample

        response_quality = make_genai_metric(
            name="response_quality",
            definition="""
            Evaluate if the response is clear, professional, and actionable.
            The response should not mention internal tools or show intermediate reasoning.
            """,
            grading_prompt="""
            Score the response on the following criteria:
            - Clarity and professionalism (1-5)
            - Avoids mentioning internal tools or functions (Yes/No)
            - Provides direct, actionable answers (1-5)

            Provide a score from 1-5 where:
            1 = Poor quality, unprofessional, or mentions internal details
            5 = Excellent quality, professional, clear and actionable
            """,
            examples=[
                EvaluationExample(
                    input="How do I create a table?",
                    output="To create a table, use the CREATE TABLE SQL command with your desired columns and data types.",
                    score=5,
                    justification="Clear, professional, and actionable without internal details"
                ),
                EvaluationExample(
                    input="How do I create a table?",
                    output="I used the get_table_info() function and then processed the schema...",
                    score=2,
                    justification="Mentions internal functions instead of providing direct answer"
                )
            ],
            version="v1",
            greater_is_better=True
        )
        scorers.append(response_quality)
    except Exception as e:
        print(f"Could not create custom response_quality metric: {e}")

    return scorers

scorers = get_scorers()
print(f"Loaded {len(scorers)} evaluation scorers")

# COMMAND ----------

# DBTITLE 1,Run Evaluation
import os
import warnings

# Suppress VectorSearch authentication notices during evaluation
os.environ["DATABRICKS_VECTOR_SEARCH_DISABLE_NOTICE"] = "1"
warnings.filterwarnings('ignore', message='.*notebook authentication token.*')

# Set the MLflow experiment
mlflow.set_experiment(experiment)

print("Starting evaluation run...")
print(f"Dataset: {dataset_name}")
print(f"Model: {model_uri}")
print(f"Number of scorers: {len(scorers)}")

with mlflow.start_run(run_name="agent_evaluation") as run:
    print(f"\nMLflow Run ID: {run.info.run_id}")

    try:
        # In MLflow 3.5.1, mlflow.evaluate is the standard API
        # If using genai-specific features, use mlflow.genai.evaluate

        # Prepare evaluation data - convert dataset to pandas DataFrame
        eval_df = eval_dataset.to_df().toPandas() if hasattr(eval_dataset.to_df(), 'toPandas') else eval_dataset.to_df()

        # Create a wrapper function that works with the evaluate API
        def model_predict(inputs):
            """Wrapper that accepts inputs dict/series and returns predictions"""
            if isinstance(inputs, dict):
                question = inputs.get('question', '')
            else:
                # Handle pandas Series
                question = inputs['question'] if 'question' in inputs else str(inputs)
            return predict_wrapper(question)

        print("\nRunning evaluation...")
        results = mlflow.evaluate(
            data=eval_df,
            model_type="question-answering",
            predictions="output",  # Column name for predictions
            targets="expected_response",  # Column name for ground truth (if available)
            extra_metrics=scorers if scorers else None,
            evaluators="default" if not scorers else None,
        )

        print("\nEvaluation complete!")
        print(f"Metrics: {results.metrics}")

        # Log the evaluation results
        mlflow.log_metrics(results.metrics)

    except Exception as e:
        print(f"Error during evaluation: {e}")
        print("\nAttempting alternative evaluation approach...")

        # Fallback: manual evaluation loop
        from tqdm import tqdm
        predictions = []

        for idx, row in tqdm(eval_df.iterrows(), total=len(eval_df), desc="Evaluating"):
            try:
                question = row['inputs']['question'] if isinstance(row['inputs'], dict) else row['inputs']
                pred = predict_wrapper(question)
                predictions.append(pred)
            except Exception as pred_error:
                print(f"Error predicting row {idx}: {pred_error}")
                predictions.append("")

        eval_df['predictions'] = predictions

        # Log the predictions
        mlflow.log_table(eval_df, artifact_file="evaluation_results.json")
        print(f"\nEvaluated {len(predictions)} examples")
        print("Results logged to MLflow")

# COMMAND ----------

# DBTITLE 1,Display Evaluation Results
print("\n" + "="*80)
print("EVALUATION SUMMARY")
print("="*80)

if 'results' in locals():
    print(f"\nMetrics:")
    for metric_name, metric_value in results.metrics.items():
        print(f"  {metric_name}: {metric_value}")

    print(f"\nRun ID: {run.info.run_id}")
    print(f"Experiment: {experiment}")

    # Display detailed results if available
    if hasattr(results, 'tables'):
        print("\nDetailed results:")
        display(results.tables['eval_results_table'])
else:
    print("\nEvaluation completed with manual approach")
    print("Check MLflow UI for detailed results")

print("="*80)