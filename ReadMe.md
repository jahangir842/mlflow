### Guide for Team Members to Log Experiments to MLflow Tracking Server

#### Prerequisites:

1. **MLflow Installed**: Ensure that each team member has MLflow installed on their machine. They can install it using `pip`:
   ```bash
   pip install mlflow
   ```

2. **Access to the Tracking Server**: Ensure that your MLflow server is running and accessible to your team members. They should be able to access the server’s URL (e.g., `http://192.168.1.147:5000`) from their machines.

### Steps for Team Members to Log Experiments

#### 1. **Set the Tracking URI**

Each team member must configure their local MLflow environment to point to your centralized MLflow tracking server.

You can set the `MLFLOW_TRACKING_URI` environment variable on their machine to point to your server’s address. They can either set it in their terminal session or in the Python script.

##### Option 1: Set the Environment Variable 

   Download this script files: `set_mlflow_tracking_uri.sh`.

2. **Make the Script Executable**:
   Make the script executable by running:
   ```bash
   chmod +x set_mlflow_tracking_uri.sh
   ```

3. **Run the Script**:
   Execute the script by running:
   ```bash
   ./set_mlflow_tracking_uri.sh
    ```


##### Option 2: Add manually in Bashrc 

Open the bashrc with following command:
```bash
nano ~/.bashrc
```

Add the follwong line in ~/.bashrc file:

```bash
export MLFLOW_TRACKING_URI=http://192.168.1.147:5000
```

Update environment with:

```bash
source ~/.bashrc
```

##### Option 3: Set the Tracking URI in Python Script (Permanent for the Script)
In each Python script where they are logging experiments, they can set the `tracking_uri` programmatically:

```python
import mlflow

mlflow.set_tracking_uri("http://192.168.1.147:5000")
```

This will direct MLflow to log all experiments to the centralized server.

#### 2. **Log an Experiment**

Once the tracking URI is set to your server, they can start logging experiments as usual. Here’s an example Python script for logging an experiment:

```python
import mlflow

# Optionally set the experiment name (this will create a new experiment or use an existing one)
experiment_name = "team_project_experiment"
mlflow.set_experiment(experiment_name)

# Start a new MLflow run
with mlflow.start_run():
    # Log a parameter (e.g., a hyperparameter)
    mlflow.log_param("learning_rate", 0.01)
    
    # Log a metric (e.g., accuracy)
    mlflow.log_metric("accuracy", 0.95)
    
    # Log an artifact (e.g., a model file)
    mlflow.log_artifact("model.pkl")
    
    # Optionally log other things, like plots or data files
    # mlflow.log_artifact("data.csv")
```

### 3. **Access the MLflow UI**

After running the script, the experiment and run will be logged to the centralized server. Team members can access the MLflow UI on the server by visiting:

```bash
http://192.168.1.147:5000
```

Here they can:
- View the experiments
- Compare different runs
- Monitor metrics, parameters, and artifacts
- Download logged artifacts (like models or data files)

### 4. **Best Practices for Logging Experiments**

To ensure consistency and effective collaboration, it’s good practice for your team to follow these guidelines:

- **Use Meaningful Experiment Names**: Set clear and descriptive names for each experiment using `mlflow.set_experiment("experiment_name")`.
- **Log Key Metrics and Parameters**: Always log important hyperparameters, metrics, and other relevant data so that the experiments can be compared easily.
- **Log Artifacts**: Save models, training data, or other valuable files using `mlflow.log_artifact()`. This makes it easy to retrieve files later and use them in future runs.
- **Use Version Control**: Keep track of versions of your code, models, and data. You can use versioning systems like Git to ensure everyone is on the same page with code and experiment management.

### 5. **Review and Compare Experiments in the UI**

Once your team members have logged multiple runs, they can visit the MLflow UI to:
- **View experiments and runs**: The experiment list shows all the logged runs.
- **Compare different runs**: Compare different runs based on metrics, parameters, or tags to find the best-performing models.
- **Access artifacts**: Download the models or data files that were logged as artifacts during a run.

### 6. **Access Permissions (Optional)**

If your MLflow server is running in a production environment or with multiple users, it may be important to restrict access to the MLflow UI or certain experiments. You can secure access by:
- **Setting up authentication**: Use HTTP Basic Authentication or integrate with an authentication system (e.g., OAuth, SSO) via a reverse proxy like Nginx or Apache.
- **Creating separate experiments for teams**: Organize experiments based on different tasks or teams (e.g., `team_A_experiment`, `team_B_experiment`).

---

### Recap of the Key Steps:

1. **Set the Tracking URI**: Point to the MLflow tracking server (`http://192.168.1.147:5000`).
2. **Log an Experiment**: Use `mlflow.start_run()` to log parameters, metrics, and artifacts.
3. **Access the UI**: Visit the MLflow UI on `http://192.168.1.147:5000` to view and compare experiments.

By following these steps, all team members will be able to log their machine learning experiments to the centralized MLflow tracking server, enabling easier collaboration and experiment management.