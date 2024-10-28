# Databricks notebook source
# DBTITLE 1,Past Unplanned Outages
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Read postcodes and suburb names from CSV
df_postcodes = pd.read_csv('postcodes_suburb.csv')
postcodes = df_postcodes['Postcode'].tolist()  # List of postcodes
suburb_names = df_postcodes['Suburb'].tolist()  # List of suburb names

# Parameters for data generation
num_records = 10000  # Number of outage records
weather_conditions = ["Fine_Conditions", "Rain", "Storms", "High Temperature"]
staff_range = {postcode: random.randint(3, 15) for postcode in postcodes}  # Random staff count per postcode

# Helper function to generate random datetime
def random_date():
    return datetime(2024, random.randint(1, 12), random.randint(1, 28), random.randint(0, 23), random.randint(0, 59))

# Function to calculate outage duration based on logic
def generate_outage_duration(weather, staff):
    if weather in ["Rain", "Storms", "High Temperature"]:
        base_duration = random.uniform(3, 12)  # Higher outage times
    else:
        base_duration = random.uniform(0, 6)  # Lower outage times

    # Adjusting for staff availability
    adjustment_factor = (15 - staff) / 15  # Fewer staff increases outage
    return min(max(base_duration * (1 + adjustment_factor), 0), 24)  # Bound outage within 0-24 hours

# Data generation loop
data = []
for _ in range(num_records):
    postcode = random.choice(postcodes)
    weather = random.choice(weather_conditions)
    staff = staff_range[postcode]
    suburb = suburb_names[postcodes.index(postcode)]  # Get suburb name based on postcode
    start_time = random_date()
    duration = generate_outage_duration(weather, staff)
    end_time = start_time + timedelta(hours=duration)

    # Extract time-based features
    day = start_time.day
    dow = start_time.strftime("%A")  # Full weekday name
    month = start_time.strftime("%B")  # Full month name

    data.append([
        postcode, suburb, weather, staff, start_time, end_time, duration, day, dow, month
    ])

# Create DataFrame
df = pd.DataFrame(data, columns=[
    "Postcode", "Suburb", "Weather_Conditions", "Field_Staff", "Outage_StartTime", 
    "Outage_EndTime", "Outage_Hours", "Day", "DOW", "Month"
])

# Save to CSV
output_path = "electricity_outages_final.csv"
df.to_csv(output_path, index=False)


# COMMAND ----------

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Read postcodes and suburb names from CSV
df_postcodes = pd.read_csv('postcodes_suburb.csv')
postcodes = df_postcodes['Postcode'].tolist()  # List of postcodes
suburb_names = df_postcodes['Suburb'].tolist()  # List of suburb names

# Parameters for data generation
num_records = 10000  # Number of outage records
weather_conditions = ["Fine_Conditions", "Rain", "Storms", "High Temperature"]
staff_range = {postcode: random.randint(3, 15) for postcode in postcodes}  # Random staff count per postcode
end_date = datetime(2024, 9, 30)  # Upper limit for outage start dates

# Helper function to generate random datetime within the past year up to September 30, 2024
def random_date():
    start_date = end_date - timedelta(days=365)
    random_days = random.randint(0, (end_date - start_date).days)
    random_time = timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
    return start_date + timedelta(days=random_days) + random_time

# Function to calculate outage duration based on logic
def generate_outage_duration(weather, staff):
    if weather in ["Rain", "Storms", "High Temperature"]:
        base_duration = random.uniform(2.5, 5.5)  # Moderate outage times
    else:
        base_duration = random.uniform(1, 4)  # Lower outage times

    # Adjusting for staff availability
    adjustment_factor = (15 - staff) / 15  # Fewer staff increases outage
    return min(max(base_duration * (1 + adjustment_factor), 0), 24)  # Bound outage within 0-24 hours

# Data generation loop
data = []
for _ in range(num_records):
    postcode = random.choice(postcodes)
    weather = random.choice(weather_conditions)
    staff = staff_range[postcode]
    suburb = suburb_names[postcodes.index(postcode)]  # Get suburb name based on postcode
    start_time = random_date()
    duration = generate_outage_duration(weather, staff)
    end_time = start_time + timedelta(hours=duration)

    # Extract time-based features
    day = start_time.day
    dow = start_time.strftime("%A")  # Full weekday name
    month = start_time.strftime("%B")  # Full month name

    data.append([
        postcode, suburb, weather, staff, start_time, end_time, duration, day, dow, month
    ])

# Create DataFrame
df = pd.DataFrame(data, columns=[
    "Postcode", "Suburb", "Weather_Conditions", "Field_Staff", "Outage_StartTime", 
    "Outage_EndTime", "Outage_Hours", "Day", "DOW", "Month"
])

# Save to CSV
output_path = "electricity_outages_final.csv"
df.to_csv(output_path, index=False)


# COMMAND ----------

# DBTITLE 1,Planned outages
import pandas as pd
import random
from datetime import datetime, timedelta

# Load the CSV file containing postcodes and suburbs
df_postcodes = pd.read_csv('postcodes_suburb.csv')
postcodes = df_postcodes['Postcode'].astype(str).tolist()
reasons = ["Planned maintenance", "Road and commercial work", "Routine inspection", "Equipment failure", "Power grid upgrade"]

# Define the date range from today to the end of December 2024
start_date = datetime.now()
end_date = datetime(2024, 12, 31)

data = []
for i in range(100):
    # Generate a random outage start date within the specified range
    outage_start = start_date + timedelta(days=random.randint(0, (end_date - start_date).days), hours=random.randint(0, 23))
    outage_end = outage_start + timedelta(hours=random.randint(1, 12))
    reason = random.choice(reasons)
    postcode = random.choice(postcodes)  # Use postcodes from the CSV file
    data.append({
        'Postcode': postcode,
        'outage_start_date_time': outage_start,
        'outage_end_date_time': outage_end,
        'reason_for_outage': reason
    })

# Create a pandas DataFrame for the outages
df_outages = pd.DataFrame(data)

# Merge outages data with postcodes to include suburbs
df_postcodes['Postcode'] = df_postcodes['Postcode'].astype(str)
df_outages_with_suburb = pd.merge(df_outages, df_postcodes, on='Postcode', how='left')

# Write the DataFrame with suburbs to a CSV file
csv_file_path = "planned_outages.csv"
df_outages_with_suburb.to_csv(csv_file_path, index=False)