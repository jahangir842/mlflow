### Setting Up an MLflow Server on Ubuntu

To set up an MLflow server on Ubuntu for tracking your team's machine learning experiments, follow these steps. This setup allows team members to log their experiments to a centralized MLflow tracking server.

---

### Step 1: Install Dependencies

Ensure you have Python, pip, and other required dependencies installed.

1. **Update the package index and install Python, pip, and PostgreSQL development libraries**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip libpq-dev -y
   ```

2. **Create a Python Virtual Environment**:
   Use `venv` to isolate the MLflow environment.

   - Navigate to the desired directory:
     ```bash
     cd /path/to/your/project
     ```

   - Create a virtual environment named `.mlflow`:
     ```bash
     python3 -m venv .mlflow
     ```

   - Activate the virtual environment:
     ```bash
     source .mlflow/bin/activate
     ```

   - Verify the environment is active. The terminal prompt should change to include `.mlflow`:
     ```bash
     (.mlflow) user@machine:~/project$
     ```

   - To deactivate the environment later, use:
     ```bash
     deactivate
     ```

3. **Install MLflow and PostgreSQL Adapter**:
   With the virtual environment activated, install the required packages:
   ```bash
   pip install psycopg2
   pip install mlflow
   ```

   For Rhel based linux: (is it same for ubuntu based? Verify?)
   ```bash
   pip install psycopg2-binary
   pip install mlflow
   ```

---

### 2. Set Up a Backend Storage (Optional, but recommended) https://github.com/jahangir842/mlflow/blob/main/authentication_for_mlflow.md

MLflow tracks experiments and stores results in a backend store, like a database or file system. For simplicity, you can start with local file-based storage, but using a relational database like PostgreSQL is recommended for production.

#### Option 1: Using Local File Storage
MLflow can store experiment data in a local directory. For this, you need to specify the directory when running the server.

#### Option 2: Using PostgreSQL (Recommended for production) https://github.com/jahangir842/mlflow/blob/main/authentication_for_mlflow.md
To use PostgreSQL, you'll first need to install it:

   ```bash
   sudo apt install postgresql postgresql-contrib
   ```
   
   For Rhel based linux:
   
   ```bash
   sudo dnf install postgresql-server postgresql-contrib -y
   ```
   **Initialize the PostgreSQL database**:

   ```bash
   sudo postgresql-setup --initdb
   sudo systemctl enable postgresql
   sudo systemctl start postgresql
   ```


Then, configure PostgreSQL:
1. Log into PostgreSQL:
   ```bash
   sudo -u postgres psql
   ```

2. Create a new database and user:
   ```sql
   CREATE DATABASE mlflowdb;
   CREATE USER mlflowuser WITH PASSWORD 'yourpassword';
   ALTER ROLE mlflowuser SET client_encoding TO 'utf8';
   ALTER ROLE mlflowuser SET default_transaction_isolation TO 'read committed';
   ALTER ROLE mlflowuser SET timezone TO 'UTC';
   GRANT ALL PRIVILEGES ON DATABASE mlflowdb TO mlflowuser;
   \q
   ```

---

### Open Port 6000 in Firewall (RHEL Based Linux)

1. **Allow Port 6000:**
   ```bash
   sudo firewall-cmd --permanent --add-port=6000/tcp
   ```

2. **Reload Firewall:**
   ```bash
   sudo firewall-cmd --reload
   ```

3. **Verify:**
   ```bash
   sudo firewall-cmd --list-ports
   ```

4. **(Optional) SELinux:**
   If SELinux is enforcing:
   ```bash
   sudo semanage port -a -t http_port_t -p tcp 6000
   ```

Done! Port 6000 is now open.

---

### 3. Start the MLflow Server

Now that you've installed MLflow and set up your storage backend, you can start the server. Use the following command to start the MLflow server.

```bash
mlflow server \
  --backend-store-uri postgresql://mlflowuser:yourpassword@localhost/mlflowdb \
  --default-artifact-root /mnt/mlflow
  --host 0.0.0.0 --port 5000
```

- Replace `/mnt/mlflow` with the directory where you want to store your artifacts. (Can be NFS Share or Blob Storage if Cloud)
- Replace `postgresql://mlflowuser:yourpassword@localhost/mlflowdb` with your actual database connection string.

This command will start the MLflow server and make it accessible on port 5000. It will also allow team members on different machines to log their experiments to the centralized server.

### 4. Allow External Access (if required)

If you want your team members to be able to access the MLflow server remotely (on a different computer or network), ensure that:

- The server machine's firewall allows incoming connections on port 5000.
- Use the IP address or domain name of the server, not `localhost`, when accessing the server.

For example, you can use `http://<server-ip>:5000` in the MLflow client to access the server remotely.

### 5. Configure Clients to Use the Server

Team members need to configure their MLflow client to log experiments to the centralized server.

1. Set the `MLFLOW_TRACKING_URI` to the address of your MLflow server. For example:
   ```bash
   export MLFLOW_TRACKING_URI=http://<server-ip>:5000
   ```

2. After setting this, your team members can use the usual MLflow tracking functions (`mlflow.start_run()`, `mlflow.log_param()`, etc.) and their experiments will be logged to the central server.

### 6. (Optional) Set Up Authentication (MLFLOW Builtin Authentication)

If you want to restrict access to your MLflow server, you can set up authentication. One option is to use Nginx as a reverse proxy with authentication (Basic Auth, OAuth, etc.). This would require configuring an Nginx server to act as a frontend for MLflow and adding user authentication.

### 6. (Optional) Set Up Authentication (With Reverse Proxy)

If you want to restrict access to your MLflow server, you can set up authentication. One option is to use Nginx as a reverse proxy with authentication (Basic Auth, OAuth, etc.). This would require configuring an Nginx server to act as a frontend for MLflow and adding user authentication.


### 7. Verify the Setup

To verify that the server is running, you can open a web browser and visit `http://<server-ip>:5000`. You should see the MLflow UI, where you can see your experiments, metrics, parameters, and artifacts.

---


# Automate the MLflow Server:

#### 1. Create a systemd Service File

You can create a systemd service to manage the MLflow server as a service. Follow these steps:

1. Open a terminal and create a new service file in the `/etc/systemd/system/` directory:

   ```bash
   sudo nano /etc/systemd/system/mlflow-server.service
   ```

2. In the `mlflow-server.service` file, add the following content:

   ```ini
   [Unit]
   Description=MLflow Server
   After=network.target

   [Service]
   User=jahangir
   Group=jahangir
   WorkingDirectory=/home/jahangir/projects/mlflow
   ExecStart=/bin/bash -c "source /home/jahangir/projects/mlflow/.mlflow/bin/activate && /home/jahangir/projects/mlflow/.mlflow/bin/mlflow server --backend-store-uri postgresql://admin:pakistan@localhost/ml>
   Restart=always
   Environment=PATH=/usr/local/bin:$PATH

   [Install]
   WantedBy=multi-user.target

   ```

   - Replace `/usr/local/bin/mlflow` with the actual path to your MLflow binary if it's different. You can find the path by running `which mlflow` in your terminal.
   - Replace `username` with your actual system username.
   - The `Restart=always` ensures that the MLflow server restarts if it crashes unexpectedly.

3. Save and close the file (`Ctrl + X`, then `Y`, and `Enter` to confirm).

#### 2. Reload systemd and Enable the Service

After creating the service file, you'll need to reload the systemd manager and enable the service to start on boot:

1. Reload the systemd manager:

   ```bash
   sudo systemctl daemon-reload
   ```

2. Enable the MLflow service to start automatically at boot:

   ```bash
   sudo systemctl enable mlflow-server
   ```

3. Start the service immediately:

   ```bash
   sudo systemctl start mlflow-server
   ```

#### 3. Check the Status of the Service

To check if the MLflow server is running correctly, you can use:

```bash
sudo systemctl status mlflow-server
```

This will display the status of the MLflow service. You should see that it's running and active. If there are any issues, it will show logs for debugging.

#### 4. Access the MLflow Server

Now, the MLflow server should be running and accessible on `http://localhost:5000`. You can check the logs with:

```bash
sudo journalctl -u mlflow-server -f
```

This will stream the logs for the MLflow service, allowing you to see if there are any issues or errors.

### Additional Notes:
- **Stopping the Service:** You can stop the service with:

  ```bash
  sudo systemctl stop mlflow-server
  ```

- **Restarting the Service:** If you need to restart the service:

  ```bash
  sudo systemctl restart mlflow-server
  ```

- **Disabling the Service:** If you no longer want the MLflow server to start automatically on boot:

  ```bash
  sudo systemctl disable mlflow-server
  ```

This setup will ensure that the MLflow server starts automatically whenever the system boots and can be managed easily through systemd commands.
