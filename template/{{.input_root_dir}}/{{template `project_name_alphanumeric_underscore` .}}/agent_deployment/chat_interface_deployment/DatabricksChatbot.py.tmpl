import dash
from dash import html, Input, Output, State, dcc
import dash_bootstrap_components as dbc
from mlflow.deployments import get_deploy_client
from utils import list_endpoints

class DatabricksChatbot:
    def __init__(self, app, endpoint_name, height='600px'):
        self.app = app
        self.endpoint_name = endpoint_name
        self.height = height

        try:
            print('Initializing MLflow deploy client...')
            self.deploy_client = get_deploy_client()
            print('MLflow deploy client initialized')
        except Exception as e:
            print(f'Error initializing deploy client: {str(e)}')
            self.deploy_client = None

        self.layout = self._create_layout()
        self._create_callbacks()
        self._add_custom_css()

    def _create_layout(self):
        return html.Div([
            html.H2('Chat with Databricks AI', className='chat-title mb-3'),
            dbc.Card([
                dbc.CardBody([
                    html.Div(id='chat-history', className='chat-history'),
                ], className='d-flex flex-column chat-body')
            ], className='chat-card mb-3'),
            dbc.InputGroup([
                dbc.Input(id='user-input', placeholder='Type your message here...', type='text'),
                dbc.Button('Send', id='send-button', color='success', n_clicks=0, className='ms-2'),
                dbc.Button('Clear', id='clear-button', color='danger', n_clicks=0, className='ms-2'),
            ], className='mb-3'),
            dcc.Store(id='assistant-trigger'),
            dcc.Store(id='chat-history-store'),
            html.Div(id='dummy-output', style={'display': 'none'}),
        ], className='d-flex flex-column chat-container p-3')

    def _create_callbacks(self):
        @self.app.callback(
            Output('chat-history-store', 'data', allow_duplicate=True),
            Output('chat-history', 'children', allow_duplicate=True),
            Output('user-input', 'value'),
            Output('assistant-trigger', 'data'),
            Input('send-button', 'n_clicks'),
            Input('user-input', 'n_submit'),
            State('user-input', 'value'),
            State('chat-history-store', 'data'),
            prevent_initial_call=True
        )
        def update_chat(send_clicks, user_submit, user_input, chat_history):
            if not user_input:
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update

            chat_history = chat_history or []
            chat_history.append({'role': 'user', 'content': user_input})
            chat_display = self._format_chat_display(chat_history)
            chat_display.append(self._create_typing_indicator())

            return chat_history, chat_display, '', {'trigger': True}

        @self.app.callback(
            Output('chat-history-store', 'data', allow_duplicate=True),
            Output('chat-history', 'children', allow_duplicate=True),
            Input('assistant-trigger', 'data'),
            State('chat-history-store', 'data'),
            prevent_initial_call=True
        )
        def process_assistant_response(trigger, chat_history):
            if not trigger or not trigger.get('trigger'):
                return dash.no_update, dash.no_update

            chat_history = chat_history or []
            if (not chat_history or not isinstance(chat_history[-1], dict)
                    or 'role' not in chat_history[-1]
                    or chat_history[-1]['role'] != 'user'):
                return dash.no_update, dash.no_update

            try:
                assistant_response = self._call_model_endpoint(chat_history)
                chat_history.append({
                    'role': 'assistant',
                    'content': assistant_response
                })
            except Exception as e:
                error_message = f'Error: {str(e)}'
                print(error_message)  # Log the error for debugging
                chat_history.append({
                    'role': 'assistant',
                    'content': error_message
                })

            chat_display = self._format_chat_display(chat_history)
            return chat_history, chat_display

        @self.app.callback(
            Output('chat-history-store', 'data', allow_duplicate=True),
            Output('chat-history', 'children', allow_duplicate=True),
            Input('clear-button', 'n_clicks'),
            prevent_initial_call=True
        )
        def clear_chat(n_clicks):
            print('Clearing chat')
            if n_clicks:
                return [], []
            return dash.no_update, dash.no_update

    def _call_model_endpoint(self, messages, max_tokens=128):
        if self.deploy_client is None:
            raise Exception('Deploy client is not initialized')

        # Format messages for Agent Framework
        # Agent Framework expects input as a list of message dictionaries
        input_messages = [
            {
                'role': message['role'],
                'content': message['content']
            } for message in messages
        ]

        try:
            print(f'Calling agent endpoint...{self.endpoint_name}')

            # Use MLflow deployments client to query the agent endpoint
            # This matches the format used in ModelServing.py notebook
            input_example = {
                "input": input_messages,
                "databricks_options": {"return_trace": True}
            }

            response = self.deploy_client.predict(
                endpoint=f'/serving-endpoints/{self.endpoint_name}',
                inputs=input_example
            )

            # Extract the response content from Agent Framework response
            # The response is a dict with 'output' key
            if isinstance(response, dict) and 'output' in response:
                message = response['output']
            else:
                raise Exception(f'Unexpected response format: {response}')

            print('Agent endpoint called successfully')
            return message
        except Exception as e:
            print(f'Error calling agent endpoint: {str(e)}')
            raise

    def _format_chat_display(self, chat_history):
        return [
            html.Div([
                html.Div(msg['content'],
                         className=f"chat-message {msg['role']}-message")
            ], className=f"message-container {msg['role']}-container")
            for msg in chat_history if isinstance(msg, dict) and 'role' in msg
        ]

    def _create_typing_indicator(self):
        return html.Div([
            html.Div(className='chat-message assistant-message typing-message',
                     children=[
                         html.Div(className='typing-dot'),
                         html.Div(className='typing-dot'),
                         html.Div(className='typing-dot')
                     ])
        ], className='message-container assistant-container')

    def _add_custom_css(self):
        custom_css = '''
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
        body {
            font-family: 'DM Sans', sans-serif;
            background-color: #F9F7F4; /* Oat Light */
        }
        .chat-container {
            max-width: 800px;
            margin: 0 auto;
            background-color: #FFFFFF;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .chat-title {
            font-size: 24px;
            font-weight: 700;
            color: #1B3139; /* Navy 800 */
            text-align: center;
        }
        .chat-card {
            border: none;
            background-color: #EEEDE9; /* Oat Medium */
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .chat-body {
            flex-grow: 1;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        .chat-history {
            flex-grow: 1;
            overflow-y: auto;
            padding: 15px;
        }
        .message-container {
            display: flex;
            margin-bottom: 15px;
        }
        .user-container {
            justify-content: flex-end;
        }
        .chat-message {
            max-width: 80%;
            padding: 10px 15px;
            border-radius: 20px;
            font-size: 16px;
            line-height: 1.4;
        }
        .user-message {
            background-color: #FF3621; /* Databricks Orange 600 */
            color: white;
        }
        .assistant-message {
            background-color: #1B3139; /* Databricks Navy 800 */
            color: white;
        }
        .typing-message {
            background-color: #2D4550; /* Lighter shade of Navy 800 */
            color: #EEEDE9; /* Oat Medium */
            display: flex;
            justify-content: center;
            align-items: center;
            min-width: 60px;
        }
        .typing-dot {
            width: 8px;
            height: 8px;
            background-color: #EEEDE9; /* Oat Medium */
            border-radius: 50%;
            margin: 0 3px;
            animation: typing-animation 1.4s infinite ease-in-out;
        }
        .typing-dot:nth-child(1) { animation-delay: 0s; }
        .typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .typing-dot:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typing-animation {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-5px); }
            100% { transform: translateY(0px); }
        }
        #user-input {
            border-radius: 20px;
            border: 1px solid #DCE0E2; /* Databricks Gray - Lines */
        }
        #send-button, #clear-button {
            border-radius: 20px;
            width: 100px;
        }
        #send-button {
            background-color: #00A972; /* Databricks Green 600 */
            border-color: #00A972;
        }
        #clear-button {
            background-color: #98102A; /* Databricks Maroon 600 */
            border-color: #98102A;
        }
        .input-group {
            flex-wrap: nowrap;
        }
        '''
        self.app.index_string = self.app.index_string.replace(
            '</head>',
            f'<style>{custom_css}</style></head>'
        )

        self.app.clientside_callback(
            """
            function(children) {
                var chatHistory = document.getElementById('chat-history');
                if(chatHistory) {
                    chatHistory.scrollTop = chatHistory.scrollHeight;
                }
                return '';
            }
            """,
            Output('dummy-output', 'children'),
            Input('chat-history', 'children'),
            prevent_initial_call=True
        )