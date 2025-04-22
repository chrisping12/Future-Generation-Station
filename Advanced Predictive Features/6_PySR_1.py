import pandas as pd
import numpy as np
import joblib
import os 
os.system('chcp 65001')
from pysr import PySRRegressor
from sklearn.preprocessing import StandardScaler

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

# Cast to float32
X = X.astype(np.float32)
y = y.astype(np.float32)

# Create a PySR model with Feature Selection
model = PySRRegressor(
    niterations=1000,
    populations=20,
    population_size=500,
    maxsize=20,
    unary_operators=[ "log", "sqrt"],
    binary_operators=["+", "-", "*", "/", "^", "cond"],
    elementwise_loss="HuberLoss()",
    #weight_complexity=0.0001,
    progress=True,
    denoise=True,
    verbosity=3,
    ncycles_per_iteration=1,
    output_torch_format=False,
    select_k_features=10,
    batching=True,
    batch_size=2048,     # start here; bump up to 4096 or even 5799 once you confirm it runs
    precision=32,      # optional but recommended on low‑RAM machines
)

print("🚀 Launching PySR…")
import os, time
print("⏳ Starting PySR at", time.strftime("%X"), "PID=", os.getpid())
model.fit(X, y)
print("✅ Done.")

# View the best discovered equation
print(model)

# View the top discovered equations (sorted by score)
print(model.equations_)

# Save the trained model
joblib.dump(model, 'pysr_nba_model.pkl')

predictions = model.predict(X)
