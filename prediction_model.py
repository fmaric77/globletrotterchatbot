import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.linear_model import Ridge
from sklearn.svm import SVR
from sklearn.linear_model import Lasso
from sklearn.linear_model import ElasticNet
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# Simulated Data: Countries, Medals Won, and Tourist Growth
df = pd.read_csv("C:\Users\Academy2024\Desktop\abuvac\Project\prediction_dataset.csv")

# Features (Olympic Year and Medals) and Target (Tourism Growth)
X = df[['Olympics_Year', 'Total_Medals']]
y = df['Tourism_Growth']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create RandomForest model
# model = RandomForestRegressor(n_estimators=100, random_state=42)

# Create Linear Regression model
# model = LinearRegression()

# Create Decision Tree Regressor model
# model = DecisionTreeRegressor(random_state=42)

# Create Gradient Boosting Regressor model
# model = GradientBoostingRegressor(random_state=42)

# Create KNN Regressor model
# model = KNeighborsRegressor(n_neighbors=5)

# Create SVR model
model = SVR(kernel='linear')

# Create Ridge Regression model
# model = Ridge(alpha=1.0)

# Create Lasso Regression model
# model = Lasso(alpha=0.1)

# Create ElasticNet model
# model = ElasticNet(alpha=0.1, l1_ratio=0.5)

# Create XGBoost Regressor
# model = XGBRegressor(random_state=42)

# Train the model
model.fit(X_train, y_train)

# Make predictions on test set
y_pred = model.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

# print(f"Mean Squared Error: {mse}")
# print(f"R^2 Score: {r2}")

# Path to excel file
xlsx_file = "C:/Users/Academy2024/Desktop/abuvac/Project/2024_medal_winners_total.xlsx"
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