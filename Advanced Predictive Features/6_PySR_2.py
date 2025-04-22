import pandas as pd
import numpy as np
import joblib
import os 
os.system('chcp 65001')
from pysr import PySRRegressor
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
#from sklearn.model_selection import train_test_split
#from sklearn.metrics import mean_squared_error

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

# 1) Split your data
#X_train, X_test, y_train, y_test = train_test_split(
 #   X, y, test_size=0.2, random_state=42
#)

# Create a PySR model with Feature Selection
model = PySRRegressor(
    
    # 1) Search budget
    niterations=100,
    populations=20,              # more parallel sub‑populations
    population_size=50,         # moderately small for diversity
    
    # 2) Complexity controls
    maxsize=20,                  # allow up to ~40 nodes
    maxdepth=5,                  # at most 6 nested ops
    # remove weight_complexity!
    #weight_simplify=0.002,       # roughly default
    #weight_optimize=0.0,         # off by default
    #weight_randomize=0.0005,     # roughly default

    # adaptive parsimony (optional)
    #use_frequency=True,
    #use_frequency_in_tournament=True,
    #adaptive_parsimony_scaling=1040.0,      # lighter penalty for complex eqns
    
    
    # 3) Operators
    unary_operators=["exp", "log", "sqrt"],
    binary_operators=["+", "-", "*", "/"],
    
    # 4) Loss & validation
    elementwise_loss="L2DistLoss()",  # classic MSE for regression
    select_k_features=6,  # keep your top 10 in play
    
    
    # 6) Diagnostics
    progress=True,
    verbosity=3,
    denoise=True,
    output_torch_format=False,
    model_selection='accuracy',  # go all‑in for lowest error
    
           
)

# Fit the model to your data
model.fit(X, y)

# 3) Evaluate on the held‑out test set
#y_pred = model.predict(X)
#print("Test MSE:", mean_squared_error(y, y))

# 1. Get the Pareto front DataFrame
pareto_df = model.pareto_front()
print(pareto_df)
# ► This will show you one row per equation on the Pareto front,
#    with columns like “loss” (your objective), “complexity” (node count),
#    and the actual “equation” text.

# 2. Examine all discovered equations (the full set, not just the front)
equations_df = model.equations_
print(equations_df)
# ► This DataFrame usually has columns:
#    - `equation`     : the symbolic form
#    - `loss`         : the training (or validation) loss
#    - `complexity`   : how big/complex the tree is
#    - maybe other stats (e.g. “size”, “score” depending on version)


# View the best discovered equation
#print(model)


# Save the trained model
joblib.dump(model, 'pysr_nba_model.pkl')

predictions = model.predict(X)

# -- Optional: plot Loss vs Complexity to visualize the front --
import matplotlib.pyplot as plt

plt.scatter(pareto_df["complexity"], pareto_df["loss"])
plt.xlabel("Complexity")
plt.ylabel("Loss (train)")
plt.title("PySR Pareto Front: Accuracy vs. Complexity")
plt.show()