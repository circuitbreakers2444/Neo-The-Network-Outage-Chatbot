from datetime import datetime
import pandas as pd
from langchain_community.utilities import OpenWeatherMapAPIWrapper
from langchain_community.vectorstores import DatabricksVectorSearch
from langchain_community.embeddings import DatabricksEmbeddings
from databricks.vector_search.client import VectorSearchClient
from langchain_core.tools import tool
from langchain.tools.retriever import create_retriever_tool
import os
from DataLoader import DataLoader


data_loader = DataLoader()

df_outages = data_loader.df_outages
df_postcodes = data_loader.df_postcodes
unplanned_outage_data = data_loader.unplanned_outage_data
overall_avg_outage = data_loader.overall_avg_outage

def get_retriever(persist_dir: str = None):
    """Create a vector search retriever instance."""
    print("retrieving RAG")
    VECTOR_SEARCH_ENDPOINT_NAME = "vector-search-ep"
    index_name = "llm.rag.docs_indx"
    embedding_model = DatabricksEmbeddings(endpoint="ee-embedding-bge")
    vsc = VectorSearchClient(
        workspace_url=os.environ["DATABRICKS_HOST"],
        personal_access_token=os.environ["DATABRICKS_TOKEN_WS"]
    )
    vs_index = vsc.get_index(endpoint_name=VECTOR_SEARCH_ENDPOINT_NAME, index_name=index_name)
    return DatabricksVectorSearch(vs_index, text_column="text", embedding=embedding_model).as_retriever()

def setup_tools():
    """Set up tools including the FAQ retriever tool."""
    retriever_FAQ_tool = create_retriever_tool(
        get_retriever(),
        "answer_FAQ",
        "Answer FAQ's on power outage"
    )
    return [
        retriever_FAQ_tool,
        get_suburb_by_postcode,
        get_current_datetime,
        get_planned_outage_info,
        get_weather_for_postcode,
        estimate_unplanned_outage_duration
    ]


@tool
def get_suburb_by_postcode(postcode: str) -> str:
    """Retrieve suburb name by postcode. If the postcode is not found, return 'Postcode not supported'."""
    try:
        print("retrieving get_suburb_by_postcode")
        # Convert the postcode column to string to ensure comparison works properly
        df_postcodes['Postcode'] = df_postcodes['Postcode'].astype(str)
        
        # Check if the postcode exists in the dataframe
        result = df_postcodes[df_postcodes['Postcode'] == postcode]['Suburb']
        
        if result.empty:
            return "Postcode not supported"
        else:
            return result.values[0]
    
    except Exception as e:
        return f"Error occurred: {str(e)}"


@tool
def get_current_datetime() -> str:
    """Retrieve the current date and time."""
    try:
        print("retrieving get_current_datetime")
        # Get the current date and time
        current_datetime = datetime.now()
        # Format the date and time as a string
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        return f"The current date and time is: {formatted_datetime}"
    except Exception as e:
        return f"Error retrieving current date and time: {str(e)}"


@tool
def get_planned_outage_info(postcode: str, start_time: str, end_time: str) -> str:
    """Retrieve planned outage information for a given postcode and date range (date part only)."""
    try:
        print("retrieving get_planned_outage_info")
        
        # Convert strings to datetime objects
        start_time = pd.to_datetime(start_time).date()  # Convert to date
        end_time = pd.to_datetime(end_time).date()      # Convert to date
        
        print(start_time, ":", end_time, ":", type(postcode))
        
        # Ensure that the outage start/end are converted to the date part only
        df_outages['outage_start_date'] = pd.to_datetime(df_outages['outage_start_date_time']).dt.date
        df_outages['outage_end_date'] = pd.to_datetime(df_outages['outage_end_date_time']).dt.date
        
        # Filter outages based on postcode and date range (ignoring time)
        outages = df_outages[
                                ((df_outages['Postcode'] == postcode) &
                                (df_outages['outage_start_date'] >= start_time) &
                                (df_outages['outage_end_date'] >= end_time)) |
                                ((df_outages['Postcode'] == postcode) &
                                (df_outages['outage_start_date'] >= start_time) &
                                (df_outages['outage_end_date'] <= end_time))
                            ]
        
        print(start_time, ":", end_time, ":", outages, ":", postcode)
        
        if outages.empty:
            return f"No outages found for postcode {postcode} during the provided date range. {start_time} to {end_time}"
        sorted_outages = outages.sort_values(by='outage_start_date_time', ascending=True)
        # Create a response string for the outages
        response = f"Outages in postcode {postcode} from {start_time} to {end_time}:\n"
        for _, row in sorted_outages.iterrows():
            response += (f"Planned Outage from {row['outage_start_date_time']} to {row['outage_end_date_time']} "
                        f"due to {row['reason_for_outage']}.\n")
        
        return response
    
    except Exception as e:
        print(f"Error calling tool:  {str(e)}")
        return f"Error retrieving planned outage information: {str(e)}"

@tool
def get_weather_for_postcode(postcode: str) -> dict:
    """Fetch the current weather data for a given postcode."""
    try:
        print("retrieving get_weather_for_postcode")
        # Initialize the OpenWeatherMap API wrapper
        weather = OpenWeatherMapAPIWrapper()
        print(postcode)
        # Fetch weather data for the given postcode
        weather_data = weather.run(f"{postcode}")

        print(weather_data)
        # Return the result as a dictionary
        return {
            "postcode": postcode,          
            "weather_data": weather_data
        }
    except Exception as e:
        print(f"Error fetching weather data: {str(e)}")
        return {"error": f"Error fetching weather data: {str(e)}"}


@tool
def estimate_unplanned_outage_duration(postcode: int, weather_condition: str) -> float:
    """
    Estimate unplanned outage duration based on the average outage duration for a given postcode and weather condition.
    
    Args:
    - postcode (int): The postcode for which to estimate the outage.
    - weather_condition (str): The weather condition (e.g., "Rain", "Storms", "High Temperature").

    Returns:
    - float: Estimated unplanned outage duration in hours.
    """
    try:
        print("retrieving estimate_unplanned_outage_duration")
        # Filter data by postcode and weather condition
        filtered_data = unplanned_outage_data[
            (unplanned_outage_data['Postcode'] == postcode) &
            (unplanned_outage_data['Weather_Conditions'] == weather_condition)
        ]

        if not filtered_data.empty:
            # Calculate the average outage duration for matching records
            avg_outage = filtered_data['Outage_Hours'].mean()
            return round(avg_outage, 2)
        else:
            # If no matching data, return the overall average
            print("No matching data found. Returning overall average.")
            return round(overall_avg_outage, 2)

    except Exception as e:
        print(f"Error calculating outage duration: {str(e)}")
        return round(overall_avg_outage, 2)

