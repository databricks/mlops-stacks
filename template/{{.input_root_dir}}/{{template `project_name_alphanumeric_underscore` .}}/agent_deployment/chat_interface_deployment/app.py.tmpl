import os
import dash
import dash_bootstrap_components as dbc
from DatabricksChatbot import DatabricksChatbot
from dotenv import load_dotenv

load_dotenv()

# Ensure environment variable is set correctly
serving_endpoint = os.getenv('SERVING_ENDPOINT')
assert serving_endpoint, 'SERVING_ENDPOINT must be set in app.yaml.'

# Initialize the Dash app with a clean theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# Create the chatbot component with a specified height
chatbot = DatabricksChatbot(app=app, endpoint_name=serving_endpoint, height='600px')

# Define the app layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(chatbot.layout, width={'size': 8, 'offset': 2})
    ])
], fluid=True)

if __name__ == '__main__':
    app.run_server(debug=True)