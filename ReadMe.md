### Guide to Log Experiments to MLflow Tracking Server

#### Prerequisites:

1. **MLflow Installed**: Ensure that each team member has MLflow installed on their machine. They can install it using `pip`:
   ```bash
   pip install mlflow
   ```

2. **Access to the Tracking Server**: Ensure that your MLflow server is running and accessible to your team members. They should be able to access the server’s URL (e.g., http://192.168.1.147:5000) from their machines.

---

### Step 1: Create Shared Directory (NFS)

Install the NFS client utilities on each machine that will access the shared directory. Follow these steps:

1. Update the package index to ensure the latest versions are available:
   ```bash
   sudo apt update
   ```

2. Install the NFS common package:
   ```bash
   sudo apt install nfs-common -y
   ```

---

### Step 4: Create a Mount Point  
On the client machine, set up a directory to serve as the mount point for the shared directory. Run the following command:  

```bash
sudo mkdir -p /opt/mlflow
```

### Step 3: Mount the Shared Directory  
Mount the shared directory exported by the server to the client’s mount point using the command below:  

```bash
sudo mount 192.168.1.147:/opt/mlflow /opt/mlflow
```  

Replace `<server_IP>` with the IP address of the NFS server.

### Step 4: Configure Persistent Mounting
To ensure the NFS directory mounts automatically on reboot, add an entry to the `/etc/fstab` file. Open the file with a text editor:

```bash
sudo nano /etc/fstab
```

Add the following line:

```plaintext
192.168.1.147:/opt/mlflow /opt/mlflow nfs defaults 0 0
```

Save and exit the file, then test the configuration with:

```bash
sudo mount -a
```

####################################################

#### 1. **Set the Tracking URI**

Each team member must configure their local MLflow environment to point to your centralized MLflow tracking server.

You can set the `MLFLOW_TRACKING_URI` environment variable on their machine to point to your server’s address. They can either set it in their terminal session or in the Python script.

##### Option 1: Add Tracking URI in Bashrc 

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

##### Option 2: Set the Tracking URI in Python Script (Permanent for the Script)
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

# Set the experiment name
mlflow.set_experiment("LLM Fine Tuning with llama4.o")

# Start a new MLflow run
with mlflow.start_run(run_name="first_run"):
    # Log parameters directly
    mlflow.log_param("learning_rate", 0.01)
    mlflow.log_param("model_name", "example_model")
    mlflow.log_param("output_dir", "/path/to/output")
    mlflow.log_param("lora_r", 16)
    mlflow.log_param("lora_alpha", 32)
    mlflow.log_param("lora_dropout", 0.1)
    mlflow.log_param("num_train_epochs", 10)
    mlflow.log_param("batch_size", 32)
    mlflow.log_param("weight_decay", 0.01)
    mlflow.log_param("lr_scheduler", "linear")
    mlflow.log_param("file_name", "allinone.py")

    # Example: Log a metric (optional)
    mlflow.log_metric("accuracy", 0.85)

    # Example: Log an artifact (e.g., a file)
    # mlflow.log_artifact("path/to/local/file")
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
- 

### 5. **Best Practices for Logging Experiments**

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
