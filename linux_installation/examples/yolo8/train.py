from ultralytics import YOLO
import mlflow
import os

# Set MLflow tracking URI
mlflow.set_tracking_uri("http://192.168.1.147:5000")

# Set the experiment name
experiment_name = "Yolo8"
mlflow.set_experiment(experiment_name)

# Define a writable artifact path
artifact_path = "/home/waqas/mlflow_artifacts"
os.makedirs(artifact_path, exist_ok=True)

# Start a new MLflow run
with mlflow.start_run(run_name="first_run"):
    mlflow.log_param("learning_rate", 0.01)
    mlflow.log_metric("accuracy", 0.95)
    mlflow.log_artifact("model.pkl")

# Initialize YOLO model
model = YOLO("yolo11n.yaml")

# Train the model and specify an output directory
results = model.train(
    data="/home/waqas/datasets/data.yaml",
    epochs=3,
    project="/home/waqas/runs"  # Set a writable output directory
)

