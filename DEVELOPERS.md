# MLflow Developers Guide

How to log experiments, models, and artifacts to the company's central MLflow
tracking server. This is for **users** of MLflow (data scientists / ML
engineers). For deploying or operating the server, see the
[Docker Compose guide](docker_compose_installation/README.md).

---

## 1. What you get

A shared tracking server that records, for every training run:
- **Parameters** (hyperparameters, config)
- **Metrics** (accuracy, loss, … — including per-step curves)
- **Artifacts** (models, plots, files) — stored centrally, downloadable by anyone
- **Model registry** (versioned, promotable models)

You interact with it only through the `mlflow` Python client (or REST). You do
**not** need any database access, S3 keys, or NFS mounts — the server handles
storage for you.

---

## 2. Access

| | |
|---|---|
| **Tracking URL** | `http://192.168.3.86:5000` |
| **Web UI** | open that URL in a browser |
| **Auth** | username + password (per developer) |

Ask an admin to create your account. Admins create one with:

```bash
curl -u admin:<admin-password> -X POST \
  http://192.168.3.86:5000/api/2.0/mlflow/users/create \
  -H "Content-Type: application/json" \
  -d '{"username": "yourname", "password": "your-password"}'
```

> If you can't reach the URL at all, you're likely off the network / VPN, or the
> firewall port isn't open — ping an admin.

---

## 3. Set up your machine

```bash
pip install mlflow          # match the server's major version (2.x)
```

Point the client at the server and provide your credentials via **environment
variables** — never hardcode credentials in code:

```bash
export MLFLOW_TRACKING_URI="http://192.168.3.86:5000"
export MLFLOW_TRACKING_USERNAME="yourname"
export MLFLOW_TRACKING_PASSWORD="your-password"
```

Put these in your shell profile (`~/.bashrc` / `~/.zshrc`) or a local `.env`
that you **do not commit**. Verify it works:

```bash
python -c "import mlflow; print(mlflow.search_experiments())"
```

An empty list (`[]`) or a list of experiments both mean success. An error
mentioning `401` means your username/password is wrong.

---

## 4. Log your first run

```python
import mlflow

# Groups runs under a named experiment (created automatically if new).
# Convention: "<project> - <your-name>" so experiments are easy to find.
mlflow.set_experiment("fraud-model - alice")

with mlflow.start_run(run_name="baseline-xgboost"):
    # --- parameters ---
    mlflow.log_param("max_depth", 6)
    mlflow.log_param("learning_rate", 0.1)

    # --- metrics ---
    mlflow.log_metric("accuracy", 0.93)
    mlflow.log_metric("auc", 0.97)

    # --- metric over time (e.g. per epoch) ---
    for epoch, loss in enumerate([0.9, 0.6, 0.4, 0.3]):
        mlflow.log_metric("loss", loss, step=epoch)

    # --- tags (searchable metadata) ---
    mlflow.set_tag("dataset_version", "2024-06")

    # --- artifacts (any file: plots, configs, data samples) ---
    mlflow.log_artifact("confusion_matrix.png")
```

Open the UI, pick your experiment, and you'll see the run with everything logged.
Artifacts are uploaded to the server's object store and viewable/downloadable
from the run page.

---

## 5. Autologging (easiest way to start)

For supported libraries, one line captures params, metrics, and the model
automatically:

```python
import mlflow

mlflow.autolog()          # or mlflow.sklearn.autolog(), mlflow.pytorch.autolog(), etc.

# ...your normal training code inside a run...
with mlflow.start_run():
    model.fit(X_train, y_train)
```

Supported: scikit-learn, XGBoost, LightGBM, PyTorch Lightning, Keras/TensorFlow,
and more. See the [MLflow autolog docs](https://mlflow.org/docs/latest/tracking/autolog.html).

---

## 6. Log and load models

Log a model as a first-class artifact:

```python
import mlflow.sklearn

with mlflow.start_run():
    model.fit(X_train, y_train)
    mlflow.sklearn.log_model(model, artifact_path="model")
```

Load it back anywhere (any teammate, with their own credentials set):

```python
import mlflow

run_id = "xxxxxxxxxxxxxxxx"
model = mlflow.sklearn.load_model(f"runs:/{run_id}/model")
model.predict(X_new)
```

### Model Registry (promote models across stages)

```python
# Register a run's model under a shared name
mlflow.register_model(f"runs:/{run_id}/model", "fraud-model")

# Later, load a specific version or alias
model = mlflow.sklearn.load_model("models:/fraud-model/3")          # version 3
model = mlflow.sklearn.load_model("models:/fraud-model@champion")   # by alias
```

Use the **Models** tab in the UI to view versions, add aliases (e.g.
`champion`, `staging`), and see lineage back to the source run.

---

## 7. Conventions & best practices

- **Experiment naming**: `"<project> - <your-name>"` so work is easy to filter.
- **Name your runs** (`run_name=`) — anonymous runs are hard to tell apart.
- **Tag** runs with things you'll want to search on (`git_commit`, `dataset_version`, `model_type`).
- **Log the environment**: call `mlflow.log_artifact("requirements.txt")` or use
  autolog, which captures dependencies with the model.
- **Never commit credentials** — keep them in env vars / an un-committed `.env`.
- **One run per training attempt** — don't reuse a run for unrelated work.
- **Large artifacts** are fine (they go to object storage), but avoid logging
  huge raw datasets on every run; log a reference or a sample instead.

---

## 8. Change your password

```python
import os, requests
base = os.environ["MLFLOW_TRACKING_URI"]
requests.patch(
    f"{base}/api/2.0/mlflow/users/update-password",
    auth=(os.environ["MLFLOW_TRACKING_USERNAME"], os.environ["MLFLOW_TRACKING_PASSWORD"]),
    json={"username": os.environ["MLFLOW_TRACKING_USERNAME"], "password": "new-password"},
)
```

---

## 9. Troubleshooting

| Symptom | Cause / fix |
|---------|-------------|
| `MlflowException: ... 401` | Wrong/missing username or password. Check `MLFLOW_TRACKING_USERNAME` / `MLFLOW_TRACKING_PASSWORD`. |
| `Connection refused` / timeout | Not on the network/VPN, wrong URL, or firewall port closed. |
| `PERMISSION_DENIED` on an experiment | New users default to READ. Ask an admin to grant you write access to that experiment. |
| Artifacts won't upload | Usually a transient server issue — retry; if it persists, ping an admin (server-side object store). |
| Version warnings | Keep your client on the same major version (2.x) as the server. |

---

## Reference

- [MLflow Tracking docs](https://mlflow.org/docs/latest/tracking.html)
- [MLflow Model Registry docs](https://mlflow.org/docs/latest/model-registry.html)
- [MLflow authentication docs](https://mlflow.org/docs/latest/auth/index.html)
