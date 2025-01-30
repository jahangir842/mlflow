# Guide to Log Experiments to MLflow Tracking Server

### Step 1: Install MLflow:

1. **MLflow Installed**: Ensure that each team member has MLflow installed on their machine. They can install it using `pip`:
   ```bash
   pip install mlflow
   ```

2. **Access to the Tracking Server**: Ensure that your MLflow server is running and accessible to your team members. They should be able to access the server’s URL (e.g., http://192.168.1.147:5000) from their machines.

---

### Step 2: Create Shared Directory (NFS) For Linux:

Install the NFS client utilities on each machine that will access the shared directory. Follow these steps:

1. Update the package index to ensure the latest versions are available:
   ```bash
   sudo apt update
   ```

2. Install the NFS common package:
   ```bash
   sudo apt install nfs-common -y
   ```

**Create a Mount Point**

On the client machine, set up a directory to serve as the mount point for the shared directory. Run the following command:  

```bash
sudo mkdir -p /opt/mlflow
```

**Mount the Shared Directory**  
Mount the shared directory exported by the server to the client’s mount point using the command below:  

```bash
sudo mount 192.168.1.147:/opt/mlflow /opt/mlflow
```  

Replace `<server_IP>` with the IP address of the NFS server.

**Configure Persistent Mounting**
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

---

### Step 3: Create Shared Directory (NFS) For Windows:

#### **Step 1: Enable NFS Client on Windows 10**
1. **Open Control Panel**: Press `Windows + R`, type `control`, and hit Enter.
2. **Go to "Programs"**: Click "Programs" and then "Turn Windows features on or off".
3. **Enable NFS Client**: 
   - Find "Services for NFS", expand it, and check "Client for NFS".
   - Click OK and restart if prompted.

#### **Step 2: Map the NFS Share in File Explorer**
1. **Open File Explorer**: Press `Windows + E`.
2. **Go to "This PC"**: In the left sidebar, click "This PC".
3. **Map Network Drive**: 
   - Right-click "This PC" and select "Map Network Drive".
   - Choose a Drive letter and enter the NFS server path: `\\<MLFLOW_SERVER_IP>\<NFS_SHARE_PATH>`. For example: `\\192.168.1.147\opt\mlflow`.
4. **Reconnect at Sign-in**: Check "Reconnect at sign-in" if you want it to reconnect automatically.
5. **Finish**: Click **Finish**. The share will be mounted and accessible from "This PC".

---

Your guide looks good overall, but there are a few improvements that could make it more comprehensive and clear. Here's a refined version:

### Step 5: Set the Tracking URI in the Python Script (Permanent for the Script)

To ensure that all experiment logs are directed to your centralized MLflow server, set the tracking URI programmatically in each Python script:

```python
import mlflow

# Set the tracking URI to the centralized MLflow server
mlflow.set_tracking_uri("http://192.168.1.147:5000")
```
This step will configure MLflow to log experiments to the specified server every time the script is run.

### 6. Log an Experiment

Once the tracking URI is set, you can start logging experiments. Below is an example Python script for logging an experiment:

```python
import mlflow

# Set the experiment name (Change the experiment name and also add developer name)
mlflow.set_experiment("LLM Experiment by Daniel")

# Start a new MLflow run
with mlflow.start_run(run_name="Run Name"):
    # Log general hyperparameters
    mlflow.log_param("learning_rate", 0.001)
    mlflow.log_param("epochs", 10)
    mlflow.log_param("batch_size", 32)
    mlflow.log_param("optimizer", "Adam")
    mlflow.log_param("model_architecture", "CNN")
    mlflow.log_param("dropout_rate", 0.3)
    mlflow.log_param("weight_decay", 0.01)
    mlflow.log_param("activation_function", "ReLU")
    mlflow.log_param("data_augmentation", "True")
    mlflow.log_param("pretrained_model", "True")
    mlflow.log_param("training_time", "2 hours")
    mlflow.log_param("model_version", "v1.0")

    # Example: Log a metric
    mlflow.log_metric("accuracy", 0.85)

    # Log an artifact (e.g., a file)
    mlflow.log_artifact("path/to/output/file")
    # e.g mlflow.log_artifact("C:/windows/users/daniel/project/llm")
    # e.g mlflow.log_artifact("/home/daniel/project")

```

### Key Notes:
1. **Experiment Setup**: The `mlflow.set_experiment()` method ensures that the logs are grouped under the specified experiment name. It creates a new experiment if one does not exist.
2. **Logging Parameters**: Use `mlflow.log_param()` to log parameters, which can include hyperparameters, configuration details, or any other relevant settings.
3. **Metrics and Artifacts**: `mlflow.log_metric()` logs numerical values like accuracy, loss, etc. `mlflow.log_artifact()` is used to save files or models that are generated during the experiment.
4. **Server Interaction**: Once set, all the experiments will automatically be logged to the centralized MLflow server, making it easy to track and manage them.

### Additional Tips:
- You can also log additional data such as plots, models, or source code as artifacts.
- Ensure that the MLflow server is running and accessible at the specified URI.

This version is a bit more concise while still being thorough and includes some extra clarification for users who might be less familiar with the MLflow setup.
