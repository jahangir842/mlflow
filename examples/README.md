# Example experiments

Small, self-contained MLflow runs you can use to **smoke-test the server** or as
templates for your own logging. Neither downloads any data.

| Script | Task | Experiment | Highlights |
|--------|------|------------|------------|
| `train_example.py` | Classification (Iris, RandomForest) | `example-iris` | params, metrics, confusion-matrix plot, model |
| `train_regression_example.py` | Regression (Diabetes, GradientBoosting) | `example-diabetes-regression` | different params, a **metric curve** over iterations, 3 plots, a CSV, model |

## Run them

```bash
cd examples
pip install -r requirements.txt

export MLFLOW_TRACKING_URI=http://mlflow.local     # or http://<server-ip>
# If the server requires a login, also set:
#   export MLFLOW_TRACKING_USERNAME=your-username
#   export MLFLOW_TRACKING_PASSWORD=your-password

python train_example.py                 # classification
python train_regression_example.py      # regression
```

Each script prints its run URL. Open the tracking UI and find the experiment to
see the params, metrics, plots/CSV artifacts, and the logged model.

## What they demonstrate

| MLflow feature | How |
|----------------|-----|
| Experiment grouping | `mlflow.set_experiment(...)` |
| Parameters | `mlflow.log_params(...)` |
| Metrics | `mlflow.log_metric("rmse", ...)` |
| Metric curve (per step) | `mlflow.log_metric("val_rmse", v, step=i)` |
| Tags | `mlflow.set_tag("task", "regression")` |
| File artifacts (plots, CSV) | `mlflow.log_artifact(f, artifact_path="outputs")` |
| Model logging | `mlflow.sklearn.log_model(...)` (streamed to MinIO via the server) |

## Clean up (optional)

Delete an example experiment from the UI, or via the API:

```python
import mlflow
c = mlflow.MlflowClient()
for name in ("example-iris", "example-diabetes-regression"):
    e = c.get_experiment_by_name(name)
    if e:
        c.delete_experiment(e.experiment_id)
```

See the [Developers Guide](../developers-guide.md) for the full walkthrough.
