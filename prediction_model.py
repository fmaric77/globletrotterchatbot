import psycopg2
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVR
from dotenv import load_dotenv
from langchain.tools import tool
import os

load_dotenv()

# Fetch data from the prediction table in RDS
def fetch_data():
    connection = psycopg2.connect(
        host='database-1-instance-1.cj26esgeg1lm.us-east-1.rds.amazonaws.com',
        user='globetrotter',
        password='globetrotters',
        dbname=os.getenv('RDS_DATABASE'),  # Replace with your RDS database name
        port=5432  # PostgreSQL default port
    )
    
    query = "SELECT olympics_year, total_medals, tourism_growth FROM globetrotters.prediction"
    df = pd.read_sql(query, connection)
    connection.close()
    return df

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

# Fetch 2024 medal data from RDS
def fetch_medal_data(year):
    connection = psycopg2.connect(
        host='database-1-instance-1.cj26esgeg1lm.us-east-1.rds.amazonaws.com',
        user='globetrotter',
        password='globetrotters',
        dbname=os.getenv('RDS_DATABASE'),  # Replace with your RDS database name
        port=5432  # PostgreSQL default port
    )
    
    query = f"SELECT country, total FROM globetrotters.medal_winners_total"
    df = pd.read_sql(query, connection)
    connection.close()
    return df

df_2024 = fetch_medal_data(2024)

# Extract Countries (NOC) and total medals for 2024
countries = df_2024['country'].tolist()
total_medals = df_2024['total'].tolist()

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
    df_year = fetch_medal_data(year)
    countries = df_year['country'].tolist()
    total_medals = df_year['total'].tolist()
    
    medals_year = np.array([[year, medals] for medals in total_medals])
    predicted_growth = model.predict(medals_year)
    
    top_indices = np.argsort(predicted_growth)[-top_n:][::-1]
    top_countries = [countries[i] for i in top_indices]
    
    return top_countries