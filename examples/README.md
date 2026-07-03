# Example experiment

A small, self-contained MLflow run you can use to **smoke-test the server** or as
a template for your own logging. It trains a RandomForest on the built-in Iris
dataset (no data to download) and logs parameters, metrics, a plot, and the model.

## Run it

```bash
cd examples
pip install -r requirements.txt

export MLFLOW_TRACKING_URI=http://mlflow.local     # or http://<server-ip>
# If the server requires a login, also set:
#   export MLFLOW_TRACKING_USERNAME=your-username
#   export MLFLOW_TRACKING_PASSWORD=your-password

python train_example.py
```

The script prints the run URL. Open the tracking UI and find the **`example-iris`**
experiment to see the params, metrics, the `confusion_matrix.png` artifact, and
the logged model.

## What it demonstrates

| MLflow feature | In the script |
|----------------|---------------|
| Experiment grouping | `mlflow.set_experiment("example-iris")` |
| Parameters | `mlflow.log_params(...)` |
| Metrics | `mlflow.log_metric("accuracy", ...)` |
| Tags | `mlflow.set_tag("example", "true")` |
| File artifacts | `mlflow.log_artifact("confusion_matrix.png")` |
| Model logging | `mlflow.sklearn.log_model(...)` (streamed to MinIO via the server) |

## Clean up (optional)

Delete the example experiment from the UI, or via the API:

```python
import mlflow
c = mlflow.MlflowClient()
c.delete_experiment(c.get_experiment_by_name("example-iris").experiment_id)
```

See the [Developers Guide](../developers-guide.md) for the full walkthrough.
