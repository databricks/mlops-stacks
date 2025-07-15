# You can find additional AI built-in functions starting at https://docs.databricks.com/aws/en/sql/language-manual/functions/ai_classify

# execute_python_code
def execute_python_code(code: str) -> str:
    """
    Executes the given python code and returns its stdout.
    Remember the code should print the final result to stdout.

    Args:
      code: Python code to execute. Remember to print the final result to stdout.
    """
    import sys
    from io import StringIO

    stdout = StringIO()
    sys.stdout = stdout
    try: 
        exec(code)
        return stdout.getvalue()
    except Exception as e:
        if "Spark" in str(e): 
            return f"Python code execution failed: {e}. Databricks specific code is not allowed." 
        if "pyspark" in str(e):
            return f"Python code execution failed: {e}. Databricks specific code is not allowed." 
        if "dbutils" in str(e): 
            return f"Python code execution failed: {e}. Databricks specific code is not allowed." 
        else:
            return f"Python code execution failed: {e}. Use simple code + try again."

# AI function name
ask_ai_function = """CREATE OR REPLACE FUNCTION {ask_ai_function_name}(question STRING COMMENT 'question to ask')
RETURNS STRING
COMMENT 'answer the question using chosen model'
RETURN SELECT ai_gen(question)
"""

# Summarization function
summarization_function = """CREATE OR REPLACE FUNCTION {summarization_function_name}(text STRING COMMENT 'content to parse', max_words INT COMMENT 'max number of words in the response, must be non-negative integer, if set to 0 then no limit')
RETURNS STRING
COMMENT 'summarize the content and limit response to max_words'
RETURN SELECT ai_summarize(text, max_words)
"""

# Translate function
translate_function = """CREATE OR REPLACE FUNCTION {translate_function_name}(content STRING COMMENT 'content to translate', language STRING COMMENT 'target language')
RETURNS STRING
COMMENT 'translate the content to target language, currently only english <-> spanish translation is supported'
RETURN SELECT ai_translate(content, language)
"""

# Retrieve function
from databricks_langchain import VectorSearchRetrieverTool
from langchain_core.tools import tool
import os

@tool
def retrieve_function(query: str) -> str:
    """Retrieve from Databricks Vector Search using the query."""

    index = f"{os.getenv('UC_CATALOG')}.{os.getenv('SCHEMA')}.{os.getenv('VECTOR_SEARCH_INDEX')}"

    # Define the Vector Search Retriever Tool
    vs_tool = VectorSearchRetrieverTool(
        index_name=index,  # Replace with your index name
        tool_name="vector_search_retriever",
        tool_description="Retrieves information from Databricks Vector Search.",
        embedding_model_name="databricks-bge-large-en",  # Embedding model
        num_results=1,  # Number of results to return
        columns=["url", "content"],  # Columns to include in search results
        query_type="ANN"  # Query type (ANN or HYBRID)
    )

    response = vs_tool.invoke(query)
    return f"{response[0].metadata['url']}  \n{response[0].page_content}"