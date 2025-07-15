def get_reference_documentation(catalog, schema, table, spark):
    import pandas as pd 
    from pyspark.sql.functions import col, struct
    ref_docs = (spark.createDataFrame(pd.read_parquet('https://notebooks.databricks.com/demos/dbdemos-dataset/llm/databricks-documentation/databricks_doc_eval_set.parquet'))
                .withColumnRenamed('request', 'inputs')
                .withColumnRenamed('expected_response', 'expectations')
                .withColumn('inputs', struct(col('inputs').alias('question')))
                .withColumn('expectations', struct(col('expectations').alias('expected_response'))))

    return ref_docs