# Databricks notebook source
# MAGIC %pip install -qqqq pyyaml databricks-agents databricks-sdk==0.49.0

# COMMAND ----------

# List of input args needed to run the notebook as a job.
# Provide them via DB widgets or notebook arguments.

# A Unity Catalog containing the model
dbutils.widgets.text(
    "uc_catalog",
    "ai_agent_stacks",
    label="Unity Catalog",
)
# Name of schema
dbutils.widgets.text(
    "schema",
    "ai_agent_ops",
    label="Schema",
)
# Name of model registered in mlflow
dbutils.widgets.text(
    "registered_model",
    "agent_function_chatbot",
    label="Registered model name",
)
# Name of the Databricks App
dbutils.widgets.text(
    "app_name",
    "dash-chatbot-app",
    label="App Name",
)
# Name of the Agent Model Endpoint
dbutils.widgets.text(
    "agent_model_endpoint",
    "databricks-meta-llama-3-3-70b-instruct",
    label="Agent Model Endpoint",
)

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

app_name = dbutils.widgets.get("app_name")
uc_catalog = dbutils.widgets.get("uc_catalog")
schema = dbutils.widgets.get("schema")
registered_model = dbutils.widgets.get("registered_model")
agent_model_endpoint = dbutils.widgets.get("agent_model_endpoint")

assert app_name != "", "app_name notebook parameter must be specified"
assert uc_catalog != "", "uc_catalog notebook parameter must be specified"
assert schema != "", "schema notebook parameter must be specified"
assert registered_model != "", "registered_model notebook parameter must be specified"
assert agent_model_endpoint != "", "agent_model_endpoint notebook parameter must be specified"

# COMMAND ----------

import yaml 
import os

endpoint_name = agent_model_endpoint

yaml_app_config = {"command": ["python", "app.py"],
                    "env": [{"name": "SERVING_ENDPOINT", "value": endpoint_name}]
                  }
try:
    with open('app.yaml', 'w') as f:
        yaml.dump(yaml_app_config, f)
except:
    print('pass to work on build job')

# COMMAND ----------

# MAGIC %%writefile app.py
# MAGIC import os
# MAGIC import dash
# MAGIC import dash_bootstrap_components as dbc
# MAGIC from DatabricksChatbot import DatabricksChatbot
# MAGIC from dotenv import load_dotenv
# MAGIC
# MAGIC load_dotenv()
# MAGIC
# MAGIC # Ensure environment variable is set correctly
# MAGIC serving_endpoint = os.getenv('SERVING_ENDPOINT')
# MAGIC assert serving_endpoint, 'SERVING_ENDPOINT must be set in app.yaml.'
# MAGIC
# MAGIC # Initialize the Dash app with a clean theme
# MAGIC app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
# MAGIC
# MAGIC # Create the chatbot component with a specified height
# MAGIC chatbot = DatabricksChatbot(app=app, endpoint_name=serving_endpoint, height='600px')
# MAGIC
# MAGIC # Define the app layout
# MAGIC app.layout = dbc.Container([
# MAGIC     dbc.Row([
# MAGIC         dbc.Col(chatbot.layout, width={'size': 8, 'offset': 2})
# MAGIC     ])
# MAGIC ], fluid=True)
# MAGIC
# MAGIC if __name__ == '__main__':
# MAGIC     app.run_server(debug=True)

# COMMAND ----------

# MAGIC %%writefile DatabricksChatbot.py
# MAGIC import dash
# MAGIC from dash import html, Input, Output, State, dcc
# MAGIC import dash_bootstrap_components as dbc
# MAGIC from databricks.sdk import WorkspaceClient
# MAGIC from databricks.sdk.service.serving import ChatMessage, ChatMessageRole
# MAGIC from utils import list_endpoints
# MAGIC
# MAGIC class DatabricksChatbot:
# MAGIC     def __init__(self, app, endpoint_name, height='600px'):
# MAGIC         self.app = app
# MAGIC         self.endpoint_name = endpoint_name
# MAGIC         self.height = height
# MAGIC
# MAGIC         try:
# MAGIC             print('Initializing WorkspaceClient...')
# MAGIC             self.w = WorkspaceClient()
# MAGIC             print('WorkspaceClient initialized successfully')
# MAGIC         except Exception as e:
# MAGIC             print(f'Error initializing WorkspaceClient: {str(e)}')
# MAGIC             self.w = None
# MAGIC
# MAGIC         self.layout = self._create_layout()
# MAGIC         self._create_callbacks()
# MAGIC         self._add_custom_css()
# MAGIC
# MAGIC     def _create_layout(self):
# MAGIC         return html.Div([
# MAGIC             html.H2('Chat with Databricks AI', className='chat-title mb-3'),
# MAGIC             dbc.Card([
# MAGIC                 dbc.CardBody([
# MAGIC                     html.Div(id='chat-history', className='chat-history'),
# MAGIC                 ], className='d-flex flex-column chat-body')
# MAGIC             ], className='chat-card mb-3'),
# MAGIC             dbc.InputGroup([
# MAGIC                 dbc.Input(id='user-input', placeholder='Type your message here...', type='text'),
# MAGIC                 dbc.Button('Send', id='send-button', color='success', n_clicks=0, className='ms-2'),
# MAGIC                 dbc.Button('Clear', id='clear-button', color='danger', n_clicks=0, className='ms-2'),
# MAGIC             ], className='mb-3'),
# MAGIC             dcc.Store(id='assistant-trigger'),
# MAGIC             dcc.Store(id='chat-history-store'),
# MAGIC             html.Div(id='dummy-output', style={'display': 'none'}),
# MAGIC         ], className='d-flex flex-column chat-container p-3')
# MAGIC
# MAGIC     def _create_callbacks(self):
# MAGIC         @self.app.callback(
# MAGIC             Output('chat-history-store', 'data', allow_duplicate=True),
# MAGIC             Output('chat-history', 'children', allow_duplicate=True),
# MAGIC             Output('user-input', 'value'),
# MAGIC             Output('assistant-trigger', 'data'),
# MAGIC             Input('send-button', 'n_clicks'),
# MAGIC             Input('user-input', 'n_submit'),
# MAGIC             State('user-input', 'value'),
# MAGIC             State('chat-history-store', 'data'),
# MAGIC             prevent_initial_call=True
# MAGIC         )
# MAGIC         def update_chat(send_clicks, user_submit, user_input, chat_history):
# MAGIC             if not user_input:
# MAGIC                 return dash.no_update, dash.no_update, dash.no_update, dash.no_update
# MAGIC
# MAGIC             chat_history = chat_history or []
# MAGIC             chat_history.append({'role': 'user', 'content': user_input})
# MAGIC             chat_display = self._format_chat_display(chat_history)
# MAGIC             chat_display.append(self._create_typing_indicator())
# MAGIC
# MAGIC             return chat_history, chat_display, '', {'trigger': True}
# MAGIC
# MAGIC         @self.app.callback(
# MAGIC             Output('chat-history-store', 'data', allow_duplicate=True),
# MAGIC             Output('chat-history', 'children', allow_duplicate=True),
# MAGIC             Input('assistant-trigger', 'data'),
# MAGIC             State('chat-history-store', 'data'),
# MAGIC             prevent_initial_call=True
# MAGIC         )
# MAGIC         def process_assistant_response(trigger, chat_history):
# MAGIC             if not trigger or not trigger.get('trigger'):
# MAGIC                 return dash.no_update, dash.no_update
# MAGIC
# MAGIC             chat_history = chat_history or []
# MAGIC             if (not chat_history or not isinstance(chat_history[-1], dict)
# MAGIC                     or 'role' not in chat_history[-1]
# MAGIC                     or chat_history[-1]['role'] != 'user'):
# MAGIC                 return dash.no_update, dash.no_update
# MAGIC
# MAGIC             try:
# MAGIC                 assistant_response = self._call_model_endpoint(chat_history)
# MAGIC                 chat_history.append({
# MAGIC                     'role': 'assistant',
# MAGIC                     'content': assistant_response
# MAGIC                 })
# MAGIC             except Exception as e:
# MAGIC                 error_message = f'Error: {str(e)}'
# MAGIC                 print(error_message)  # Log the error for debugging
# MAGIC                 chat_history.append({
# MAGIC                     'role': 'assistant',
# MAGIC                     'content': error_message
# MAGIC                 })
# MAGIC
# MAGIC             chat_display = self._format_chat_display(chat_history)
# MAGIC             return chat_history, chat_display
# MAGIC
# MAGIC         @self.app.callback(
# MAGIC             Output('chat-history-store', 'data', allow_duplicate=True),
# MAGIC             Output('chat-history', 'children', allow_duplicate=True),
# MAGIC             Input('clear-button', 'n_clicks'),
# MAGIC             prevent_initial_call=True
# MAGIC         )
# MAGIC         def clear_chat(n_clicks):
# MAGIC             print('Clearing chat')
# MAGIC             if n_clicks:
# MAGIC                 return [], []
# MAGIC             return dash.no_update, dash.no_update
# MAGIC
# MAGIC     def _call_model_endpoint(self, messages, max_tokens=128):
# MAGIC         if self.w is None:
# MAGIC             raise Exception('WorkspaceClient is not initialized')
# MAGIC
# MAGIC         chat_messages = [
# MAGIC             ChatMessage(
# MAGIC                 content=message['content'],
# MAGIC                 role=ChatMessageRole[message['role'].upper()]
# MAGIC             ) for message in messages
# MAGIC         ]
# MAGIC         try:
# MAGIC             print(f'Calling model endpoint...{self.endpoint_name}')
# MAGIC             response = self.w.serving_endpoints.query(
# MAGIC                 name=self.endpoint_name,
# MAGIC                 messages=chat_messages,
# MAGIC                 max_tokens=max_tokens
# MAGIC             )
# MAGIC             message = response.choices[0].message.content
# MAGIC             print('Model endpoint called successfully')
# MAGIC             return message
# MAGIC         except Exception as e:
# MAGIC             print(f'Error calling model endpoint: {str(e)}')
# MAGIC             raise
# MAGIC
# MAGIC     def _format_chat_display(self, chat_history):
# MAGIC         return [
# MAGIC             html.Div([
# MAGIC                 html.Div(msg['content'],
# MAGIC                          className=f"chat-message {msg['role']}-message")
# MAGIC             ], className=f"message-container {msg['role']}-container")
# MAGIC             for msg in chat_history if isinstance(msg, dict) and 'role' in msg
# MAGIC         ]
# MAGIC
# MAGIC     def _create_typing_indicator(self):
# MAGIC         return html.Div([
# MAGIC             html.Div(className='chat-message assistant-message typing-message',
# MAGIC                      children=[
# MAGIC                          html.Div(className='typing-dot'),
# MAGIC                          html.Div(className='typing-dot'),
# MAGIC                          html.Div(className='typing-dot')
# MAGIC                      ])
# MAGIC         ], className='message-container assistant-container')
# MAGIC
# MAGIC     def _add_custom_css(self):
# MAGIC         custom_css = '''
# MAGIC         @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
# MAGIC         body {
# MAGIC             font-family: 'DM Sans', sans-serif;
# MAGIC             background-color: #F9F7F4; /* Oat Light */
# MAGIC         }
# MAGIC         .chat-container {
# MAGIC             max-width: 800px;
# MAGIC             margin: 0 auto;
# MAGIC             background-color: #FFFFFF;
# MAGIC             border-radius: 10px;
# MAGIC             box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
# MAGIC             height: 100vh;
# MAGIC             display: flex;
# MAGIC             flex-direction: column;
# MAGIC         }
# MAGIC         .chat-title {
# MAGIC             font-size: 24px;
# MAGIC             font-weight: 700;
# MAGIC             color: #1B3139; /* Navy 800 */
# MAGIC             text-align: center;
# MAGIC         }
# MAGIC         .chat-card {
# MAGIC             border: none;
# MAGIC             background-color: #EEEDE9; /* Oat Medium */
# MAGIC             flex-grow: 1;
# MAGIC             display: flex;
# MAGIC             flex-direction: column;
# MAGIC             overflow: hidden;
# MAGIC         }
# MAGIC         .chat-body {
# MAGIC             flex-grow: 1;
# MAGIC             overflow: hidden;
# MAGIC             display: flex;
# MAGIC             flex-direction: column;
# MAGIC         }
# MAGIC         .chat-history {
# MAGIC             flex-grow: 1;
# MAGIC             overflow-y: auto;
# MAGIC             padding: 15px;
# MAGIC         }
# MAGIC         .message-container {
# MAGIC             display: flex;
# MAGIC             margin-bottom: 15px;
# MAGIC         }
# MAGIC         .user-container {
# MAGIC             justify-content: flex-end;
# MAGIC         }
# MAGIC         .chat-message {
# MAGIC             max-width: 80%;
# MAGIC             padding: 10px 15px;
# MAGIC             border-radius: 20px;
# MAGIC             font-size: 16px;
# MAGIC             line-height: 1.4;
# MAGIC         }
# MAGIC         .user-message {
# MAGIC             background-color: #FF3621; /* Databricks Orange 600 */
# MAGIC             color: white;
# MAGIC         }
# MAGIC         .assistant-message {
# MAGIC             background-color: #1B3139; /* Databricks Navy 800 */
# MAGIC             color: white;
# MAGIC         }
# MAGIC         .typing-message {
# MAGIC             background-color: #2D4550; /* Lighter shade of Navy 800 */
# MAGIC             color: #EEEDE9; /* Oat Medium */
# MAGIC             display: flex;
# MAGIC             justify-content: center;
# MAGIC             align-items: center;
# MAGIC             min-width: 60px;
# MAGIC         }
# MAGIC         .typing-dot {
# MAGIC             width: 8px;
# MAGIC             height: 8px;
# MAGIC             background-color: #EEEDE9; /* Oat Medium */
# MAGIC             border-radius: 50%;
# MAGIC             margin: 0 3px;
# MAGIC             animation: typing-animation 1.4s infinite ease-in-out;
# MAGIC         }
# MAGIC         .typing-dot:nth-child(1) { animation-delay: 0s; }
# MAGIC         .typing-dot:nth-child(2) { animation-delay: 0.2s; }
# MAGIC         .typing-dot:nth-child(3) { animation-delay: 0.4s; }
# MAGIC         @keyframes typing-animation {
# MAGIC             0% { transform: translateY(0px); }
# MAGIC             50% { transform: translateY(-5px); }
# MAGIC             100% { transform: translateY(0px); }
# MAGIC         }
# MAGIC         #user-input {
# MAGIC             border-radius: 20px;
# MAGIC             border: 1px solid #DCE0E2; /* Databricks Gray - Lines */
# MAGIC         }
# MAGIC         #send-button, #clear-button {
# MAGIC             border-radius: 20px;
# MAGIC             width: 100px;
# MAGIC         }
# MAGIC         #send-button {
# MAGIC             background-color: #00A972; /* Databricks Green 600 */
# MAGIC             border-color: #00A972;
# MAGIC         }
# MAGIC         #clear-button {
# MAGIC             background-color: #98102A; /* Databricks Maroon 600 */
# MAGIC             border-color: #98102A;
# MAGIC         }
# MAGIC         .input-group {
# MAGIC             flex-wrap: nowrap;
# MAGIC         }
# MAGIC         '''
# MAGIC         self.app.index_string = self.app.index_string.replace(
# MAGIC             '</head>',
# MAGIC             f'<style>{custom_css}</style></head>'
# MAGIC         )
# MAGIC
# MAGIC         self.app.clientside_callback(
# MAGIC             """
# MAGIC             function(children) {
# MAGIC                 var chatHistory = document.getElementById('chat-history');
# MAGIC                 if(chatHistory) {
# MAGIC                     chatHistory.scrollTop = chatHistory.scrollHeight;
# MAGIC                 }
# MAGIC                 return '';
# MAGIC             }
# MAGIC             """,
# MAGIC             Output('dummy-output', 'children'),
# MAGIC             Input('chat-history', 'children'),
# MAGIC             prevent_initial_call=True
# MAGIC         )

# COMMAND ----------

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.apps import App, AppResource, AppResourceServingEndpoint, AppResourceServingEndpointServingEndpointPermission, AppDeployment
from databricks import agents

model_name = f"{uc_catalog}.{schema}.{registered_model}"
deployment_info = agents.get_deployments(model_name)[0]

print(f"Found agent deployment: {deployment_info.endpoint_name}")

# COMMAND ----------

w = WorkspaceClient()

serving_endpoint = AppResourceServingEndpoint(name=deployment_info.endpoint_name,
                                              permission=AppResourceServingEndpointServingEndpointPermission.CAN_QUERY
                                              )

agent_endpoint = AppResource(name="agent-endpoint", serving_endpoint=serving_endpoint) 

agent_app = App(name=app_name, 
              description="Your Databricks assistant", 
              default_source_code_path=os.getcwd(),
              resources=[agent_endpoint])
try:
  app_details = w.apps.create_and_wait(app=agent_app)
  print(app_details)
except Exception as e:
  if "already exists" in str(e):
    app_details = w.apps.get(app_name)
    print(app_details)
  else:
    raise e

# COMMAND ----------

deployment = AppDeployment(
  source_code_path=os.getcwd()
)

app_details = w.apps.deploy_and_wait(app_name=app_name, app_deployment=deployment)
print(app_details)