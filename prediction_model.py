import psycopg2
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVR
from dotenv import load_dotenv
from langchain.tools import tool
import os
import matplotlib.pyplot as plt
import seaborn as sns
from pydantic import BaseModel
from typing import Dict, List
import streamlit as st
from datetime import datetime

load_dotenv()

# Fetch data from the prediction table in RDS
def fetch_data():
    connection = psycopg2.connect(
        host='database-1-instance-1.cj26esgeg1lm.us-east-1.rds.amazonaws.com',
        user='globetrotter',
        password='globetrotters',
        dbname=os.getenv('RDS_DATABASE'),
        port=5432
    )
    
    query = "SELECT olympics_year, total_medals, tourism_growth FROM globetrotters.prediction"
    df = pd.read_sql(query, connection)
    connection.close()
    return df

# Fetch medal data from RDS
def fetch_medal_data(year):
    connection = psycopg2.connect(
        host='database-1-instance-1.cj26esgeg1lm.us-east-1.rds.amazonaws.com',
        user='globetrotter',
        password='globetrotters',
        dbname=os.getenv('RDS_DATABASE'),
        port=5432
    )
    
    query = f"SELECT country, total FROM globetrotters.medal_winners_total"
    df = pd.read_sql(query, connection)
    connection.close()
    return df

# Fetch and prepare data
df = fetch_data()
X = df[['olympics_year', 'total_medals']]
y = df['tourism_growth']

# Split data and train model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = SVR(kernel='linear')
model.fit(X_train, y_train)

# Fetch the current year
current_year = datetime.now().year
next_year = current_year + 1

# Fetch medal data for the next year
df_next_year = fetch_medal_data(next_year)
countries = df_next_year['country'].tolist()
total_medals = df_next_year['total'].tolist()
medals_next_year = np.array([[next_year, medals] for medals in total_medals])

# Predict tourism growth for the next year
predicted_growth_next_year = model.predict(medals_next_year)

print(f"Predicted Tourism Growth in {next_year}:")
for i, country in enumerate(countries):
    if i < len(predicted_growth_next_year):
        print(f"{country}: {predicted_growth_next_year[i]:.2f}%")
    else:
        print(f"{country}: Prediction not available")

# Plot total medals vs tourism growth and save the plot
plt.figure(figsize=(10, 6))
sns.scatterplot(x=df['total_medals'], y=df['tourism_growth'])
plt.title('Total Medals vs Tourism Growth')
plt.xlabel('Total Medals')
plt.ylabel('Tourism Growth (%)')
plt.savefig('total_medals_vs_tourism_growth.png')
plt.close()
print("\nScatter plot saved as 'total_medals_vs_tourism_growth.png'")

# Define Pydantic model for input validation
class CountryTourismIncreaseInput(BaseModel):
    year: int
    top_n: int = 5

@tool
def predict_tourism_growth(total_medals: int) -> float:
    """
    Predict tourism growth for the next year based on the total medals won.
    
    Args:
        total_medals (int): The total number of medals won.
    
    Returns:
        float: The predicted tourism growth percentage.
    """
    # Fetch historical data
    historical_data = fetch_data()
    
    # Determine the next year for prediction
    current_year = datetime.now().year
    next_year = current_year + 1
    
    # Predict tourism growth for the next year
    prediction = model.predict([[next_year, total_medals]])
    
    # Plot the historical data and the prediction
    plt.figure(figsize=(10, 6))
    
    # Scatter plot for historical data
    sns.scatterplot(x=historical_data['olympics_year'], y=historical_data['tourism_growth'], label='Historical Data')
    
    # Line plot for the trend
    sns.lineplot(x=historical_data['olympics_year'], y=historical_data['tourism_growth'], label='Trend')
    
    # Add the prediction to the plot
    plt.scatter([next_year], [prediction[0]], color='red', label='Prediction')
    plt.plot([historical_data['olympics_year'].max(), next_year], 
             [historical_data['tourism_growth'].iloc[-1], prediction[0]], 
             color='red', linestyle='--', label='Prediction Trend')
    
    # Adjust y-axis limits dynamically
    min_growth = min(historical_data['tourism_growth'].min(), prediction[0])
    max_growth = max(historical_data['tourism_growth'].max(), prediction[0])
    plt.ylim(min_growth - 5, max_growth + 5)
    
    plt.title(f'Predicted Tourism Growth for {next_year}')
    plt.xlabel('Olympic Year')
    plt.ylabel('Tourism Growth (%)')
    plt.legend()
    
    # Define the filename for saving the plot
    filename = f'predicted_tourism_growth_{next_year}.png'
    plt.savefig(filename)
    
    # Display the plot in Streamlit
    st.pyplot(plt)
    
    return prediction[0]



    
@tool
def country_with_biggest_tourist_increase(input_data: Dict) -> List[str]:
    """
    Determine which countries will have the biggest tourist increase based on the medals won in the future.
    
    Args:
        input_data (Dict): A dictionary containing:
            year (int): The year for which to predict the tourism increase.
            top_n (int, optional): The number of top countries to return and highlight. Defaults to 5.
    
    Returns:
        List[str]: The countries with the biggest predicted tourism increase.
    """
    # Validate input using Pydantic
    validated_input = CountryTourismIncreaseInput(**input_data)
    year = validated_input.year
    top_n = validated_input.top_n

    df_year = fetch_medal_data(year)
    countries = df_year['country'].tolist()
    total_medals = df_year['total'].tolist()
    
    medals_year = np.array([[year, medals] for medals in total_medals])
    predicted_growth = model.predict(medals_year)
    
    # Create a DataFrame with countries and their predicted growth
    results_df = pd.DataFrame({
        'country': countries,
        'predicted_growth': predicted_growth
    })
    
    # Sort the DataFrame by predicted growth in descending order
    results_df = results_df.sort_values('predicted_growth', ascending=False).reset_index(drop=True)
    
    # Get the top N countries
    top_countries = results_df.head(top_n)['country'].tolist()
    
    # Create color map: highlight top countries in red, others in blue
    colors = ['red' if country in top_countries else 'blue' for country in results_df['country']]
    
    # Plot the predicted tourism growth for the given year
    plt.figure(figsize=(15, 10))
    bars = plt.bar(results_df['country'], results_df['predicted_growth'], color=colors)
    plt.title(f'Predicted Tourism Growth in {year + 1}', fontsize=16)
    plt.xlabel('Country', fontsize=12)
    plt.ylabel('Predicted Tourism Growth (%)', fontsize=12)
    plt.xticks(rotation=90, fontsize=8)
    plt.yticks(fontsize=10)
    
    # Add value labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                 f'{height:.2f}%',
                 ha='center', va='bottom', fontsize=8, rotation=90)
    
    # Add a legend
    plt.legend([f'Top {top_n} Countries', 'Other Countries'], loc='upper right')
    
    plt.tight_layout()
    filename = f'predicted_tourism_growth_{year + 1}.png'
    plt.savefig(filename)
    plt.close()
    print(f"\nBar plot saved as '{filename}'")
    st.image(filename, caption=f'Countries with biggest tourist increase {input_data}')
    
    return top_countries