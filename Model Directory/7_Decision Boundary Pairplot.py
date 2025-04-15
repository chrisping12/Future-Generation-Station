import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# Load dataset
df = pd.read_csv('predictions_with_pysr.csv')

# Define features and classification target
feat_x = 'rolling_pts_avg_5G'
feat_y = 'rolling_opp_def_rating_5G'
target_col = 'PTS_15_plus'

# Define binary classification target (25+ points)
df[target_col] = (df['PTS'] >= 15).astype(int)

# Drop rows where inputs are missing
df_subset = df[[feat_x, feat_y, target_col]].dropna()

# Extract features and labels
X = df_subset[[feat_x, feat_y]].values
y = df_subset[target_col].values

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train logistic regression model
clf = LogisticRegression()
clf.fit(X_scaled, y)

# Create mesh grid for contour plot
x_min, x_max = X_scaled[:, 0].min() - 1, X_scaled[:, 0].max() + 1
y_min, y_max = X_scaled[:, 1].min() - 1, X_scaled[:, 1].max() + 1
xx, yy = np.meshgrid(np.linspace(x_min, x_max, 300),
                     np.linspace(y_min, y_max, 300))
grid = np.c_[xx.ravel(), yy.ravel()]
Z = clf.predict(grid).reshape(xx.shape)

# Plot
plt.figure(figsize=(10, 6))
plt.contourf(xx, yy, Z, alpha=0.3, cmap='coolwarm')
plt.scatter(X_scaled[:, 0], X_scaled[:, 1], c=y, edgecolors='k', cmap='coolwarm', s=60)
plt.xlabel(f'{feat_x} (scaled)')
plt.ylabel(f'{feat_y} (scaled)')
plt.title('Logistic Regression Decision Boundary')
plt.grid(True)

# Save output
output_dir = 'decision_boundaries'
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, f'decision_boundary_{feat_x}_vs_{feat_y}.png')
plt.savefig(output_file)
plt.close()

print(f" Decision boundary plot saved to: {output_file}")