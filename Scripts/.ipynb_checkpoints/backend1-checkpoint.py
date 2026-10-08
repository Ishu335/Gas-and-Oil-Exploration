import pandas as pd
import joblib
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, StackingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

# Load dataset
df = pd.read_csv("dataset/Realistic_oil_gas_dataset_final.csv")

# Prepare features and target
X = df.drop(columns=["Extractable_Oil_Gas"])  
y = df["Extractable_Oil_Gas"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define base models (no scaling inside them because we'll apply it in outer pipeline)
base_models = [
    ('rf', RandomForestRegressor(n_estimators=200, max_depth=20, random_state=42)),
    ('lr', LinearRegression())
]

# Define stacking regressor
stacking_regressor = StackingRegressor(
    estimators=base_models,
    final_estimator=LinearRegression(),
    passthrough=True,  # original features + predictions go into meta-model
    n_jobs=-1
)

# Define pipeline with scaling
stacking_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('stack', stacking_regressor)
])

# Train the stacked model
stacking_pipeline.fit(X_train, y_train)

# Predict on test set
y_pred = stacking_pipeline.predict(X_test)

# Evaluation
r2 = r2_score(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mae = mean_absolute_error(y_test, y_pred)

# Results
print("\n Stacking Regressor Results:")
print("R² Score:", round(r2, 4))
print("RMSE:", round(rmse, 2))
print("MAE:", round(mae, 2))

# Save the model
joblib.dump(stacking_pipeline, "ensemble_model_stacking.joblib")
