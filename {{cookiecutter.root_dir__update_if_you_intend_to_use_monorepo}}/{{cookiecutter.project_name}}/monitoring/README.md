# Setup Data Monitoring for Inference Table

**Databricks Data Monitoring is currently in Private Preview. Please `sign up` for the preview and get approved
before proceeding.**

This directory contains the notebook that can run in a Databricks workspace
to set up Data Monitoring for a production inference table.

## Prerequisites

### Unity Catalog
The table to be monitored must exist in Unity Catalog.
If Unity Catalog is enabled for your workspace but the table exists in the Hive metastore, please copy the table to Unity Catalog.

For example, the following code shows how to import your data to a Unity Catalog managed table
```
df = spark.table("hive_metastore.default.example_project_predictions")
df.write.saveAsTable(
    name = "my_unity_catalog.my_schema.my_inference_table"
)
```

### Inference Table

The inference table is required to contain the following columns
- A column that contains the predictions. For regression problems, the column must be a subclass of `NumericType`.
- A column that contains the time of inference. This column must be of type `TimestampType`.
- A column that contains the model version used for inference.


## Usage

### 1. Fill in data monitoring wheel URL
The `SetUpDataMonitoringForInferenceTable.py` notebook can be found in the monitoring directory. Please complete TODO 
and fill in the wheel_URL. The URL can be found from the Data Monitoring Private Preview user guide.


### 2. Review and update required fields 
Review and update the required fields: `timestamp_col`, `model_version_col`, `prediction_col`, 
`problem_type`, `inference_table_name`, `granularities`.

For details of the fields and the API, please refer to `Data Monitoring User Guide` and
`Data Monitoring API Reference`.

### 3. Update optional fields as necessary
Review and update optional fields as necessary: `linked_entities`, `output_schema_name`, `label_col`, `example_id_col`, 
`baseline_table_name`, `data_monitoring_dir`, `slicing_exprs`, `custom_metrics`.

For details of the fields and the API, please refer to `Data Monitoring User Guide` and 
`Data Monitoring API Reference`.

### 4. Set up a monitor

After completing all the TODOs in the notebook `SetUpDataMonitoringForInferenceTable.py`, upload it
to mlops prod workspace and run it to create and set up a monitor. 

**The user running the setup notebook must be owner of the inference table.**

### 5. Set up alerts

Please refer to `Data Monitoring User Guide`.

