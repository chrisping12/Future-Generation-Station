import pandas as pd
import numpy as np
import joblib
import os 
os.system('chcp 65001')
from pysr import PySRRegressor
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# Load the data
df = pd.read_csv('nba_player_features_rolling5G.csv')
# Fill NaN values with column means
df = df.fillna(df.mean(numeric_only=True))

non_numeric_cols = ['PLAYER_NAME', 'GAME_DATE', ]# 'rolling_usg_pct_5G', 'delta_min_vs_rolling']
df = df.drop(columns=non_numeric_cols)

# Check data types of all columns
print("\nData types of all columns:")
print(df.dtypes)

#scaler = StandardScaler()
#X_scaled = scaler.fit_transform(X)
#X = pd.DataFrame(X_scaled, columns=X.columns)

# Verify if there are still any NaN values
print("\nNaN counts for each column immediately after conversion:")
print(df.isna().sum())

# Check for remaining NaN values
if df.isna().sum().sum() > 0:
    print("\nNaNs are still present in the DataFrame.")
else:
    print("\nNo NaNs detected. Proceeding to PySR.")

# Save the cleaned DataFrame
df.to_csv('cleaned_nba_data.csv', index=False)

# Define your target variable
target_column = 'PTS'

# Ensure 'PTS' exists before dropping from X
if target_column not in df.columns:
    raise ValueError(f"'{target_column}' column not found in the DataFrame.")

# Define your input features (everything except the target column)
X = df.drop(columns=[target_column])
y = df[target_column]

# Create a PySR model with Feature Selection
model = PySRRegressor(
    niterations=100,
    populations=20,
    population_size=1000,
    maxsize=20,
    unary_operators=["log", "sqrt"],
    binary_operators=["+", "-", "*", "/", "^"],
    elementwise_loss="L2DistLoss()",
    progress=True,
    verbosity=1,
    output_torch_format=True,
    select_k_features=8
)

# Fit the model to your data
model.fit(X, y)

# View the best discovered equation
print(model)

# View the top discovered equations (sorted by score)
print(model.equations_)

# Save the trained model
joblib.dump(model, 'pysr_nba_model.pkl')

predictions = model.predict(X)
