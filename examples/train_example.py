"""Example MLflow experiment — a runnable smoke test for the tracking server.

Trains a small RandomForest on the built-in Iris dataset (no data download) and
logs parameters, metrics, a plot artifact, and the model to the MLflow server.

Usage:
    pip install -r requirements.txt

    export MLFLOW_TRACKING_URI=http://mlflow.local     # or http://<server-ip>
    # If the server requires a login, also:
    #   export MLFLOW_TRACKING_USERNAME=your-username
    #   export MLFLOW_TRACKING_PASSWORD=your-password

    python train_example.py

Then open the tracking URL in a browser and find the "example-iris" experiment.
"""

import os

import matplotlib

matplotlib.use("Agg")  # headless: render plots to file, no display needed
import matplotlib.pyplot as plt
import mlflow
import mlflow.sklearn
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import train_test_split

TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "http://mlflow.local")
mlflow.set_tracking_uri(TRACKING_URI)
print(f"Logging to: {TRACKING_URI}")

# Group runs under a named experiment (created automatically if new).
mlflow.set_experiment("example-iris")

# Data
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

params = {"n_estimators": 200, "max_depth": 4, "random_state": 42}

with mlflow.start_run(run_name="rf-iris") as run:
    # --- parameters + tags ---
    mlflow.log_params(params)
    mlflow.set_tag("example", "true")

    # --- train ---
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)

    # --- metrics ---
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    f1 = f1_score(y_test, preds, average="macro")
    mlflow.log_metric("accuracy", acc)
    mlflow.log_metric("f1_macro", f1)

    # --- artifact: a confusion-matrix plot ---
    ConfusionMatrixDisplay(confusion_matrix(y_test, preds)).plot()
    plt.title("Iris confusion matrix")
    plt.savefig("confusion_matrix.png", bbox_inches="tight")
    plt.close()
    mlflow.log_artifact("confusion_matrix.png")

    # --- model (with an input example so a signature is inferred) ---
    mlflow.sklearn.log_model(model, name="model", input_example=X_test[:5])

    print(f"accuracy = {acc:.3f}   f1_macro = {f1:.3f}")
    print(f"run_id   = {run.info.run_id}")
    print(
        f"view run : {TRACKING_URI}/#/experiments/"
        f"{run.info.experiment_id}/runs/{run.info.run_id}"
    )
