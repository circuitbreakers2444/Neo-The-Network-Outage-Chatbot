import os
import dash
import dash_bootstrap_components as dbc
from DatabricksChatbot import DatabricksChatbot
from SecretsManager import SecretsManager

# Initialize the Dash app with a clean theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

os.environ['FLASK_RUN_TIMEOUT'] = '120'
os.environ["DATABRICKS_HOST"] =  "https://dbc-68b80ec3-78b4.cloud.databricks.com"   
USE_OPEN_AI = True

secrets_manager = SecretsManager()
# Create the chatbot component with a specified height
chatbot = DatabricksChatbot(app=app, use_open_ai=USE_OPEN_AI, height='600px')

# Define the app layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(chatbot.layout, width={'size': 8, 'offset': 2})
    ])
], fluid=True)

if __name__ == '__main__':
    app.run_server(debug=True)
