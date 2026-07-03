# MLflow — Developer Quickstart

Log your experiments, metrics, and models to the shared MLflow server. You don't
need to install or run anything server-side — just point the `mlflow` client at
it.

**Server:** `http://mlflow.local`  (or `http://192.168.3.86` if the name doesn't resolve)

> Want a ready-to-run example first? See [`examples/`](examples/README.md) — a
> one-command script that logs a full run (params, metrics, plot, model).

---

## 1. Make `mlflow.local` resolve (one-time)

The server is reached by the name `mlflow.local`. Add one line to your machine's
**hosts file** so the name points to the server (`192.168.3.86`):

**Linux / macOS** (safe to re-run — only adds the line if it's not already there):
```bash
grep -q "mlflow.local" /etc/hosts || echo "192.168.3.86  mlflow.local" | sudo tee -a /etc/hosts
```

**Windows** (open PowerShell/Notepad **as Administrator**):
```
Add the line to  C:\Windows\System32\drivers\etc\hosts :
192.168.3.86  mlflow.local
```

Verify: `ping mlflow.local` should reply from `192.168.3.86`.

> Prefer not to edit hosts? You can always use the IP directly:
> `http://192.168.3.86` (no port).

## 2. Set up the client (once)

```bash
pip install 'mlflow>=3'          # match the server (currently 3.14.x)

# Tell MLflow where the server is
export MLFLOW_TRACKING_URI="http://mlflow.local"
```

Put that `export` in your `~/.bashrc` / `~/.zshrc` so it's always set.

> Use a **MLflow 3.x** client to match the server. A 2.x client mostly works but
> can hit API mismatches.

> **If the server requires a login**, also set:
> ```bash
> export MLFLOW_TRACKING_USERNAME="your-username"
> export MLFLOW_TRACKING_PASSWORD="your-password"
> ```
> (Ask an admin whether login is required and for your account.)

Check it works:
```bash
python -c "import mlflow; print(mlflow.search_experiments())"
```

---

## 3. Log a run

```python
import mlflow

mlflow.set_experiment("my-project")          # groups your runs

with mlflow.start_run(run_name="first-try"):
    mlflow.log_param("learning_rate", 0.01)  # settings
    mlflow.log_metric("accuracy", 0.93)      # results
    mlflow.log_artifact("plot.png")          # any file (saved centrally)
```

Open **`http://mlflow.local`** in your browser to see it.

---

## 4. Easiest: autolog

One line captures params, metrics, and the model automatically for common
libraries (scikit-learn, XGBoost, PyTorch, Keras, …):

```python
import mlflow
mlflow.autolog()

with mlflow.start_run():
    model.fit(X_train, y_train)              # everything logged for you
```

---

## 5. Save and load a model

```python
import mlflow.sklearn

with mlflow.start_run():
    model.fit(X_train, y_train)
    mlflow.sklearn.log_model(model, name="model")
```

Load it back later (anywhere, once your `MLFLOW_TRACKING_URI` is set):

```python
import mlflow
model = mlflow.sklearn.load_model("runs:/<run_id>/model")
model.predict(X_new)
```

(You can find the `run_id` on the run's page in the UI.)

---

## 6. Tips

- **Name your experiments and runs** so they're easy to find.
- **Tag** runs with useful metadata: `mlflow.set_tag("dataset", "v2")`.
- **Artifacts can be large** (models, images, files) — they're stored on the
  server, not in git.
- **Don't hardcode credentials** in code; use the environment variables above.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Connection refused` / timeout | Check you're on the network/VPN. Try the IP: `http://192.168.3.86`. |
| Name `mlflow.local` won't resolve | Use the IP, or add `192.168.3.86  mlflow.local` to your hosts file (ask an admin). |
| `401` error | The server needs a login — set `MLFLOW_TRACKING_USERNAME` / `MLFLOW_TRACKING_PASSWORD`. |

More: [MLflow Tracking docs](https://mlflow.org/docs/latest/tracking.html)
