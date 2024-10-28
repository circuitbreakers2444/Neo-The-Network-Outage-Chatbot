import dash
from dash import html, Input, Output, State, dcc
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime, timedelta
import os
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole
from mistralai import Mistral
from langchain_mistralai import ChatMistralAI
from databricks.vector_search.client import VectorSearchClient
from langchain_community.vectorstores import DatabricksVectorSearch
from langchain_community.embeddings import DatabricksEmbeddings
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain.tools.retriever import create_retriever_tool
from langchain_core.tools import tool
from langchain_community.utilities import OpenWeatherMapAPIWrapper
from langchain_openai import ChatOpenAI
from ToolFunctions import *


class DatabricksChatbot:
    def __init__(self, app, use_open_ai, height='600px'):
        self.app = app
        self.use_open_ai = use_open_ai
        self.height = height    
        self.langgraph_agent_executor = None
        self.config = {"configurable": {"thread_id": "neo-thread"}}       

        try:
            print('Initializing Agent...')     
            self._initialize_agent()
            print('Agent initialized successfully')
        except Exception as e:
            print(f'Error initializing Agent: {str(e)}')
            self.model = None
            self.langgraph_agent_executor = None

        self.layout = self._create_layout()
        self._create_callbacks()
        self._add_custom_css()
        
    def _initialize_agent(self):
        model = ChatOpenAI(model="gpt-4o", temperature = 0.0) if self.use_open_ai else ChatMistralAI(model="mistral-large-latest", temperature = 0.0)
        memory = MemorySaver()
        with open("system_prompt.txt", "r") as file:
            system_prompt = file.read()
            print(system_prompt)
        self.langgraph_agent_executor = create_react_agent(model, setup_tools(), state_modifier=system_prompt, checkpointer=memory)

    def _create_layout(self):
        return html.Div([
            dbc.Row([
            dbc.Col(
                html.Img(src='/assets/keycore.jpg', className='logo', style={'height': '50px'}),
                width=2  # Adjust the width as needed
            ),
            dbc.Col(
                html.H2('Network Outage Assistant', className='chat-title mb-3'),
                width=10  # Adjust the width as needed
            )
        ], className='mb-3'),
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
            dcc.Store(id='welcome-trigger', data={'welcome_shown': False}),
            html.Div(id='dummy-output', style={'display': 'none'}),
        ], className='d-flex flex-column chat-container p-3')

    def _create_callbacks(self):
         # Callback to show the welcome message on page load
        @self.app.callback(
            Output('chat-history-store', 'data'),
            Output('chat-history', 'children'),
            Input('welcome-trigger', 'data'),
            State('chat-history-store', 'data'),           
            prevent_initial_call=False  # We want this callback to fire on page load
        )
        def display_welcome_message(welcome_trigger, chat_history):
            if chat_history is None:
                chat_history = []

            # Add welcome message if not already shown
            if not welcome_trigger['welcome_shown']:
                chat_history.append({
                    'role': 'assistant',
                    'content': 'Hi, I am Neo, I can help you with network outage in your postcode.'
                })

            chat_display = self._format_chat_display(chat_history)

            return chat_history, chat_display
        
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
        if self.langgraph_agent_executor is None:
            raise Exception('Agent is not initialized')
       
        print(messages)
        try:
            print('Calling Agent...')           
            print(messages[-1]['content'])
            response = self.langgraph_agent_executor.invoke(
                {"messages":  [("user", messages[-1]['content'])]}, self.config
            )
            message = response["messages"][-1].content
            print(message)
            print('Agent called successfully')
            return message
        except Exception as e:
            print(f'Error calling Agent: {str(e)}')
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
            background-color: #002263; /* Databricks Green 600 */
            border-color: #002263;
        }
        #clear-button {
            background-color: #00A972; /* Databricks Maroon 600 */
            border-color: #00A972;
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
