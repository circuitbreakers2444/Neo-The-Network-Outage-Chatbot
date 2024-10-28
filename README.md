# Network Outage Assistant (Neo)

The **Network Outage Assistant (Neo)** is a web-based chatbot application powered by Databricks. The application is designed to provide real-time information about planned and unplanned power outages by postcode and includes rich data processing for a detailed and user-friendly experience. Neo helps users quickly retrieve outage information while also estimating outage durations based on weather conditions and other factors.

To maintain modularity, separate files were created for various functionalities, including data handling, chatbot interface, and tools. We used the open-source **Mistral** language model as the primary model for this project, and to benchmark its performance, we used **OpenAI**'s models.

## Project Architecture

![image (2)](https://github.com/user-attachments/assets/ccb85772-d594-4028-8433-7d6fe79d817f)

## Architecture Diagram Description

This architecture diagram illustrates a chatbot system designed for outage-related inquiries, integrated with Databricks. Here's a description of each component:

1. **User**: Interacts with the chatbot interface to obtain outage information.

2. **Chatbot UI**: The user interface where users enter queries and receive responses from the chatbot.

3. **Databricks App**: Acts as an intermediary, connecting the Chatbot UI with the agent layer in Databricks, facilitating data retrieval and response generation.

4. **Agent**: Contains the main components responsible for processing and responding to user queries. This includes:
   - **Mistral AI**: The primary AI model used for generating responses and managing interactions with various tools.
   - **LangChain**: A framework that supports the chaining of different AI tools, allowing Mistral AI to access the required resources.

5. **Tools**: A set of APIs and data sources that the agent can access for generating accurate responses. This includes:
   - **RAG - Databricks Vector Search Index**: A Retrieval-Augmented Generation (RAG) tool integrated with a vector search index on Databricks for efficiently retrieving relevant outage data.
   - **OpenWeatherMap API**: Provides weather data to help correlate outage information with weather conditions.
   - **Planned Outages**: A database or API specifically for retrieving data on scheduled outages.
   - **Unplanned Outages**: A database or API for obtaining data on unexpected or unscheduled outages.

This setup allows the chatbot to handle outage-related queries by pulling information from relevant sources and APIs, using LangChain to route requests and data through Mistral AI for generating user-specific responses.

## Project Structure

The project is organized into three main directories:

- **Dash-Chatbot-App**: Contains the main application code for the chatbot interface.
- **Data_Prep**: Includes data files and scripts for generating sample outage data.
- **RAG**: Handles retrieval-augmented generation (RAG) setup, including document processing and testing scripts.

## Features

- **Conversational AI Assistant**: Powered by Databricks and either Mistral or OpenAI GPT models for interactive responses.
- **Data Preparation and Weather Integration**: Processes planned and unplanned outages data, enriched with weather data for better estimation of unplanned outage durations.
- **Retrieval-Augmented Generation (RAG)**: Uses Databricks vector search for efficient retrieval of frequently asked questions (FAQ) and outage details.
- **Customizable Layout and Theming**: Built with Dash and Bootstrap components for a responsive and clean UI.

## Directory Structure

```plaintext
.
├── Dash-Chatbot-App
│   ├── Assets/
│   │   └── keycore.jpg
│   ├── Data/
│   │   ├── planned_outages.csv
│   │   ├── postcodes_suburb.csv
│   │   └── past_electricity_outages_unplanned.csv
│   │   └── system_prompt.txt
│   ├── app.py                      # Main application file
│   ├── app.yaml                  
│   ├── DatabricksChatbot.py         # Chatbot implementation
│   ├── DataLoader.py                # Data loading and processing
│   ├── requirements.txt                
│   ├── SecretsManager.py            # Manages secret keys for APIs
│   ├── system_prompt.txt            # System prompt for chatbot behavior
│   └── ToolFunctions.py             # Utility functions for chatbot
├── Data_Prep
│   └── electricity_outages_final.csv       
│   ├── past_electricity_outages_unplanned.csv
│   ├── planned_outages.csv          # Generated planned outages
│   ├── postcodes_suburb.csv         # Suburb-postcode mappings
│   └── Sample_data_generation       # Scripts for sample data generation
└── RAG
    ├── 1 Create needed tables       # RAG table setup scripts
    ├── 2A Incremental PDF to docs_text
    ├── 2B Text files to docs_text
    └── 3 RAG Test Script            # Testing script for RAG integration

```

## Setup Instructions

### Prerequisites
- Python 3.8 or later
- Necessary Python packages (see `requirements.txt`)

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/network-outage-assistant.git
   cd network-outage-assistant
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:

- Set `DATABRICKS_HOST`, and API keys in `SecretsManager.py` for Databricks, Mistral, OpenAI, and OpenWeatherMap.
- `app.yaml` should include `SERVING_ENDPOINT` configuration.

4. **Run Data Preparation Scripts** (optional if using sample data):

- Run the data generation script in `Data_Prep` to create `planned_outages.csv`.

5. **Run the Application**:

   ```bash
   python app.py
   ```

## File Descriptions

### Dash-Chatbot-App

- **app.py**: Initializes the Dash application and chatbot layout.
- **app.yaml**: Configuration file for environment variables and deployment.
- **DatabricksChatbot.py**: Core chatbot implementation with response processing and callback functions.
- **DataLoader.py**: Loads and processes CSV files for planned and unplanned outages, along with suburb-postcode mappings.
- **requirements.txt**: Lists necessary Python packages for the project.
- **SecretsManager.py**: Manages retrieval of sensitive information, such as API keys from Databricks.
- **system_prompt.txt**: Defines chatbot behavior and guidelines for handling outage-related queries.
- **ToolFunctions.py**: Implements functions for retrieving outage information, getting weather data, and estimating outage durations.

#### Assets
- **keycore.jpg**: Contains images and assets required by the chatbot.

#### Data
- **planned_outages.csv**: Contains planned outages data.
- **postcodes_suburb.csv**: Maps postcodes to suburbs.
- **past_electricity_outages_unplanned.csv**: Historical data for unplanned outages, used in duration estimation.
- **system_prompt.txt**: Defines the initial system prompts for chatbot behavior.

### Data_Prep

- **electricity_outages_final.csv**: Processed data combining planned and unplanned outages.
- **planned_outages.csv**: Contains planned outages data.
- **postcodes_suburb.csv**: Maps postcodes to suburbs.
- **past_electricity_outages_unplanned.csv**: Historical data for unplanned outages, used in duration estimation.
- **Sample_data_generation**: Script for generating sample outage data.

### RAG (Retrieval-Augmented Generation)

- **1 Create needed tables**: Scripts to create and manage necessary tables for RAG.
- **2A Incremental PDF to docs_text**: Converts PDFs to searchable text documents for integration into RAG.
- **2B Text files to docs_text**: Converts text files to searchable text format for RAG integration.
- **3 RAG Test Script**: Testing script for RAG functionality within the application.


## Key Components

### Chatbot Features

- **Modular Structure**: Each component is separated for clarity and maintainability, including DatabricksChatbot, ToolFunctions, and DataLoader.
- **FAQ and Outage Information Handling**: The chatbot uses the `answer_FAQ` tool for frequently asked questions and retrieves planned or unplanned outage information based on the user query.
- **Weather Integration**: For unplanned outages, the chatbot fetches current weather data from OpenWeatherMap API to estimate outage duration accurately.

### Data Preparation

- **Planned Outage Generation**: Randomly generates planned outages with specific start and end times and outage reasons, merged with postcode-suburb data for location-based queries.
- **Weather-based Estimation for Unplanned Outages**: Uses weather data to estimate unplanned outage durations, allowing for contextual and dynamic responses.

### RAG Integration

- **FAQ Retrieval**: Uses Databricks vector search to efficiently retrieve responses to FAQs.
- **Document Storage and Search**: Processes PDFs and text files for integration into the RAG, making information retrieval faster and more accurate.

## System Prompt and Tools

The `System_prompt.txt` file provides a detailed guide for the chatbot’s behavior, including:

- Differentiation between planned and unplanned outages.
- Requirements for valid postcodes.
- Handling FAQ responses and summarizing long answers.

Key tools in `ToolFunctions.py`:

- **get_suburb_by_postcode**: Validates and retrieves suburb based on postcode.
- **get_current_datetime**: Provides the current date and time.
- **get_planned_outage_info**: Retrieves planned outage information based on the user's input.
- **get_weather_for_postcode**: Fetches weather data for a specified postcode.
- **estimate_unplanned_outage_duration**: Estimates the duration of unplanned outages based on weather conditions.

## Requirements

The required packages are listed in `requirements.txt`:

```plaintext
dash==2.17.1
dash-bootstrap-components
databricks-sdk
python-dotenv
mistralai
openai
together
langgraph 
langchain 
langchain_openai 
langchain_mistralai 
langchain_community
databricks-vectorsearch 
databricks-sdk==0.18.0 
mlflow[databricks]
pyowm
```

## Usage

- **Starting the Chatbot**: Run `app.py` and open the application in a web browser.
- **User Interaction**: Enter a postcode and query about an outage. Neo will determine whether the outage is planned or unplanned, provide relevant details, and estimate duration if needed.
- **Clear Chat**: Use the "Clear" button to reset the conversation.


5. **Open a Pull Request**.


   
 
