"""Example MLflow experiment #2 — regression with richer plots & artifacts.

Trains a GradientBoostingRegressor on the built-in Diabetes dataset (no data
download) and logs:
  - different hyperparameters (learning rate, subsample, ...)
  - regression metrics (RMSE, MAE, R2)
  - a validation-RMSE *curve* over boosting iterations (a stepped metric)
  - three plot artifacts: predicted-vs-actual, residuals histogram, feature importances
  - a predictions.csv artifact
  - the trained model

Usage:
    pip install -r requirements.txt

    export MLFLOW_TRACKING_URI=http://mlflow.local     # or http://<server-ip>
    # If the server requires a login, also set MLFLOW_TRACKING_USERNAME / _PASSWORD

    python train_regression_example.py
"""

import os

import matplotlib

matplotlib.use("Agg")  # headless: render plots to file
import matplotlib.pyplot as plt
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.datasets import load_diabetes
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "http://mlflow.local")
mlflow.set_tracking_uri(TRACKING_URI)
print(f"Logging to: {TRACKING_URI}")

mlflow.set_experiment("example-diabetes-regression")

# Data
data = load_diabetes()
X, y = data.data, data.target
feature_names = list(data.feature_names)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=7
)

params = {
    "n_estimators": 400,
    "learning_rate": 0.05,
    "max_depth": 3,
    "subsample": 0.8,
    "random_state": 7,
}


def rmse(a, b):
    return float(np.sqrt(mean_squared_error(a, b)))


with mlflow.start_run(run_name="gbr-diabetes") as run:
    # --- parameters + tags ---
    mlflow.log_params(params)
    mlflow.set_tag("example", "true")
    mlflow.set_tag("task", "regression")

    # --- train ---
    model = GradientBoostingRegressor(**params)
    model.fit(X_train, y_train)

    # --- validation-RMSE curve over boosting iterations (a stepped metric) ---
    for i, y_stage in enumerate(model.staged_predict(X_test)):
        mlflow.log_metric("val_rmse", rmse(y_test, y_stage), step=i)

    # --- final metrics ---
    preds = model.predict(X_test)
    mlflow.log_metric("rmse", rmse(y_test, preds))
    mlflow.log_metric("mae", float(mean_absolute_error(y_test, preds)))
    mlflow.log_metric("r2", float(r2_score(y_test, preds)))

    # --- plot 1: predicted vs actual ---
    plt.figure()
    plt.scatter(y_test, preds, alpha=0.6)
    lims = [min(y_test.min(), preds.min()), max(y_test.max(), preds.max())]
    plt.plot(lims, lims, "r--", linewidth=1)
    plt.xlabel("Actual")
    plt.ylabel("Predicted")
    plt.title("Predicted vs Actual")
    plt.savefig("pred_vs_actual.png", bbox_inches="tight")
    plt.close()

    # --- plot 2: residuals histogram ---
    residuals = y_test - preds
    plt.figure()
    plt.hist(residuals, bins=25, edgecolor="black")
    plt.axvline(0, color="r", linestyle="--", linewidth=1)
    plt.xlabel("Residual (actual - predicted)")
    plt.ylabel("Count")
    plt.title("Residuals")
    plt.savefig("residuals.png", bbox_inches="tight")
    plt.close()

    # --- plot 3: feature importances ---
    order = np.argsort(model.feature_importances_)
    plt.figure()
    plt.barh(np.array(feature_names)[order], model.feature_importances_[order])
    plt.xlabel("Importance")
    plt.title("Feature importances")
    plt.savefig("feature_importance.png", bbox_inches="tight")
    plt.close()

    # --- CSV artifact: per-row predictions ---
    pd.DataFrame(
        {"actual": y_test, "predicted": preds, "residual": residuals}
    ).to_csv("predictions.csv", index=False)

    # --- log all artifacts under an "outputs" folder + the model ---
    for f in ("pred_vs_actual.png", "residuals.png", "feature_importance.png", "predictions.csv"):
        mlflow.log_artifact(f, artifact_path="outputs")
    mlflow.sklearn.log_model(model, name="model", input_example=X_test[:5])

    print(
        f"rmse = {rmse(y_test, preds):.2f}   "
        f"mae = {mean_absolute_error(y_test, preds):.2f}   "
        f"r2 = {r2_score(y_test, preds):.3f}"
    )
    print(f"run_id   = {run.info.run_id}")
    print(
        f"view run : {TRACKING_URI}/#/experiments/"
        f"{run.info.experiment_id}/runs/{run.info.run_id}"
    )
