from langchain.tools import tool

import numpy as np
import pandas as pd
import boto3
from sklearn.model_selection import train_test_split
import os
from sklearn.svm import SVR
from dotenv import load_dotenv

load_dotenv()
# Fetch data from the prediction table in Athena
def fetch_data():
    client = boto3.client(
        'athena',
        region_name=os.getenv('AWS_DEFAULT_REGION'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    query = "SELECT olympics_year, total_medals, tourism_growth FROM prediction"
    
    response = client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': os.getenv('ATHENA_DATABASE')  # Replace with your Athena database name
        },
        ResultConfiguration={
            'OutputLocation': os.getenv('ATHENA_OUTPUT_LOCATION')  # Replace with your S3 bucket for query results
        }
    )
    
    query_execution_id = response['QueryExecutionId']
    
    # Wait for the query to complete
    while True:
        response = client.get_query_execution(QueryExecutionId=query_execution_id)
        status = response['QueryExecution']['Status']['State']
        if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            break
    
    if status == 'SUCCEEDED':
        result = client.get_query_results(QueryExecutionId=query_execution_id)
        rows = result['ResultSet']['Rows']
        columns = [col['VarCharValue'] for col in rows[0]['Data']]
        data = [[col.get('VarCharValue', None) for col in row['Data']] for row in rows[1:]]
        df = pd.DataFrame(data, columns=columns)
        return df
    else:
        raise Exception(f"Query failed with status: {status}")

# Simulated Data: Countries, Medals Won, and Tourist Growth
df = fetch_data()

# Features (Olympic Year and Medals) and Target (Tourism Growth)
X = df[['olympics_year', 'total_medals']]
y = df['tourism_growth']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create SVR model
model = SVR(kernel='linear')

# Train the model
model.fit(X_train, y_train)

# Path to excel file
xlsx_file = "Datasets/2024_medal_winners_total.xlsx"
df_2024 = pd.read_excel(xlsx_file)

# Extract Countries (NOC) and total medals for 2024
countries = df_2024['NOC'].tolist()
total_medals = df_2024['Total'].tolist()

# Create the medals_2024 array for prediction
medals_2024 = np.array([[2024, medals] for medals in total_medals])

# Predict tourism growth for 2025 based on 2024 medals
predicted_growth_2025 = model.predict(medals_2024)

print("Predicted Tourism Growth in 2025:")
for i, country in enumerate(countries):
    if i < len(predicted_growth_2025):
        print(f"{country}: {predicted_growth_2025[i]:.2f}%")
    else:
        print(f"{country}: Prediction not available")

# Define the tool function
@tool
def predict_tourism_growth(olympics_year, total_medals):
    """
    Predict tourism growth based on the Olympic year and total medals won.
    
    Args:
        olympics_year (int): The year of the Olympics.
        total_medals (int): The total number of medals won.
    
    Returns:
        float: The predicted tourism growth percentage.
    """
    prediction = model.predict([[olympics_year, total_medals]])
    return prediction[0]

@tool
def country_with_biggest_tourist_increase(year, top_n=1):
    """
    Determine which countries will have the biggest tourist increase based on the medals won in the future.
    
    Args:
        year (int): The year for which to predict the tourism increase.
        top_n (int, optional): The number of top countries to return. Defaults to 1.
    
    Returns:
        list: The countries with the biggest predicted tourism increase.
    """
    xlsx_file = "Datasets/2024_medal_winners_total.xlsx"
    df_2024 = pd.read_excel(xlsx_file)
    countries = df_2024['NOC'].tolist()
    total_medals = df_2024['Total'].tolist()
    
    medals_2024 = np.array([[year, medals] for medals in total_medals])
    predicted_growth = model.predict(medals_2024)
    
    top_indices = np.argsort(predicted_growth)[-top_n:][::-1]
    top_countries = [countries[i] for i in top_indices]
    
    return top_countries