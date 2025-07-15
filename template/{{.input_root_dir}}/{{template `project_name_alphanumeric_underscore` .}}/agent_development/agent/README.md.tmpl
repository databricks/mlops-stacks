# Agent Development

To better handle package conflicts and make the agent development code more portable, we have created a seperate agent_requirements.txt.
Use this requirements file for the agent itself.

## Logging the Agent

To appropriately log the Agent in MLflow you will need to write the entire agent pipeline using `%%writefile app.py`.
This will create an app.py file that will be logged alongside the Agent artifacts.

## Tool Calling

The following tools are governed through [Unity Catalog functions](https://docs.databricks.com/aws/en/generative-ai/agent-framework/create-custom-tool):
* execute_python_code
* ask_ai_function
* summarization_function
* translate_function

The retriever is defined in ./tool/ai_tools.py as retrieve_function. 
Due to using packages that aren't in the standard Databricks ML Runtime we are not able to register it as a UC Function.

In the [UCFunctionToolkit](https://python.langchain.com/api_reference/community/tools/langchain_community.tools.databricks.tool.UCFunctionToolkit.html) tool list you can comment out any functions you do not want the Agent to consider in it's tool calling loop.
