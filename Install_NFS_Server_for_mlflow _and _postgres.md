# NFS Server Installation for MLflow and PostgreSQL

**Note:** You can follow the ansible method to install MLflow and NFS Server https://github.com/jahangir842/mlflow/tree/main/ansible

This guide configures an NFS server to provide persistent storage for an MLflow tracking server and PostgreSQL backend on Kubernetes, using shared directories `/mnt/mlflow` (for MLflow artifacts) and `/mnt/postgres` (for PostgreSQL data). It includes specific permissions for PostgreSQL to avoid startup issues.

---

## Step 1: Install the NFS Kernel Server
Install the NFS server package on the host machine (assumed to be `192.168.1.185`).

### For Ubuntu/Debian
1. **Update the Package Repository**:
   Ensure the latest package versions are available:
   ```bash
   sudo apt update
   ```

2. **Install the NFS Kernel Server**:
   ```bash
   sudo apt install nfs-kernel-server -y
   ```
   - The `-y` flag confirms installation automatically.

3. **Enable and Start the NFS Service**:
   ```bash
   sudo systemctl enable --now nfs-server
   sudo systemctl start nfs-server
   ```

### For RHEL-Based Systems (RHEL 8/9, CentOS, Rocky Linux, etc.)
1. **Update the Package Repository**:
   Ensure the latest package versions are available:
   ```bash
   sudo dnf update -y
   ```
   - Use `sudo yum update -y` for older systems (e.g., CentOS 7).

2. **Install NFS Utilities**:
   RHEL uses `nfs-utils` for NFS functionality:
   ```bash
   sudo dnf install nfs-utils -y
   ```
   - Use `sudo yum install nfs-utils -y` for older systems.

3. **Enable and Start the NFS Service**:
   ```bash
   sudo systemctl enable --now nfs-server
   sudo systemctl start nfs-server
   sudo systemctl status nfs-server
   ```
   - Verify the service is `active (running)`.

---

## Step 2: Configure the Shared Directories
Set up directories to share with client machines, ensuring proper ownership and permissions for MLflow and PostgreSQL.

### For Both Ubuntu/Debian and RHEL
1. **Create the Directories**:
   ```bash
   sudo mkdir -p /mnt/mlflow /mnt/postgres
   ```

2. **Set Ownership**:
   - **For MLflow Artifacts (`/mnt/mlflow`)**:
     Set ownership to `nobody:nogroup` (Ubuntu/Debian) or `nobody:nobody` (RHEL) for general access:
     - Ubuntu/Debian:
       ```bash
       sudo chown nobody:nogroup /mnt/mlflow
       ```
     - RHEL:
       ```bash
       sudo chown nobody:nobody /mnt/mlflow
       ```
   - **For PostgreSQL Data (`/mnt/postgres`)**:
     PostgreSQL runs as UID 999 (the `postgres` user in the container), so set ownership accordingly:
     ```bash
     sudo chown 999:999 /mnt/postgres
     ```

3. **Set Permissions**:
   - **For MLflow Artifacts**:
     Allow read, write, and execute access for all:
     ```bash
     sudo chmod 777 /mnt/mlflow
     ```
   - **For PostgreSQL Data**:
     PostgreSQL requires restrictive permissions (only the owner can access):
     ```bash
     sudo chmod 700 /mnt/postgres
     ```

---

## Step 3: Configure Access in the Exports File
Grant client access by editing the `/etc/exports` file. This step is the same for Ubuntu/Debian and RHEL.

1. **Open the Exports File**:
   ```bash
   sudo nano /etc/exports
   ```

2. **Add Client Access**:
   Specify directories and permissions:
   ```
   # /mnt/mlflow 192.168.1.0/24(rw,sync,no_subtree_check)
   /mnt/mlflow 192.168.1.0/24(rw,sync,all_squash,anonuid=65534,anongid=65534)
   /mnt/postgres 192.168.1.0/24(rw,sync,no_subtree_check,no_root_squash)
   ```
   - Replace `192.168.1.0/24` with your subnet or specific client IP (e.g., `192.168.1.182`).
   - `rw`: Read and write access.
   - `sync`: Ensures data is written before responding.
   - `no_subtree_check`: Improves performance by disabling subtree checks.
   - `no_root_squash` (for `/mnt/postgres`): Allows the PostgreSQL container to manage ownership, preventing `chown` errors.

3. **Save and Exit**:
   - In `nano`: `Ctrl+O`, `Enter`, `Ctrl+X`.
   - In `vi`: `:wq`, `Enter`.

---

## Step 4: Export the Shared Directories
Apply the export configuration and restart the NFS server.

### For Both Ubuntu/Debian and RHEL
1. **Export the Directories**:
   ```bash
   sudo exportfs -a
   ```
   - This makes all directories in `/etc/exports` available.

2. **Restart the NFS Server**:
   - Ubuntu/Debian:
     ```bash
     sudo systemctl restart nfs-kernel-server
     ```
   - RHEL:
     ```bash
     sudo systemctl restart nfs-server
     ```

3. **Configure Firewall**:
   Allow NFS traffic:
   ```bash
   sudo firewall-cmd --permanent --add-service=nfs
   sudo firewall-cmd --permanent --add-service=rpc-bind
   sudo firewall-cmd --permanent --add-service=mountd
   sudo firewall-cmd --reload
   ```

Your NFS server is now configured to share `/mnt/mlflow` and `/mnt/postgres` with clients, with proper permissions for PostgreSQL.

---

## Client-End Configurations
Configure client machines (e.g., Kubernetes worker nodes) to access the NFS shares.

### Step 1: Install NFS Client Utilities
Install the necessary packages on the client.

#### For Ubuntu/Debian
1. **Update the Package Index**:
   ```bash
   sudo apt update
   ```

2. **Install NFS Common**:
   ```bash
   sudo apt install nfs-common -y
   ```

#### For RHEL-Based Systems
1. **Update the Package Repository**:
   ```bash
   sudo dnf update -y
   ```
   - Use `sudo yum update -y` for older systems.

2. **Install NFS Utilities**:
   ```bash
   sudo dnf install nfs-utils -y
   ```
   - Use `sudo yum install nfs-utils -y` for older systems.

### Step 2: Create Mount Points
Create directories on the client to mount the NFS shares.

#### For Both Ubuntu/Debian and RHEL
```bash
sudo mkdir -p /mnt/mlflow /mnt/postgres
```

### Step 3: Mount the Shared Directories
Mount the NFS server’s shares to the client’s mount points.

#### For Both Ubuntu/Debian and RHEL
1. **Mount the Directories**:
   ```bash
   sudo mount 192.168.1.185:/mnt/mlflow /mnt/mlflow
   sudo mount 192.168.1.185:/mnt/postgres /mnt/postgres
   ```

2. **Verify the Mount**:
   ```bash
   df -h
   ```
   - Look for entries like `192.168.1.185:/mnt/mlflow` and `192.168.1.185:/mnt/postgres` under `Filesystem`.

Once mounted, the client can access the shared files at `/mnt/mlflow` and `/mnt/postgres`.

---

## Additional Notes
- **PostgreSQL Permissions**: The `/mnt/postgres` directory must be owned by UID 999 (GID 999) with `700` permissions to match the `postgres` user in the container, preventing startup errors like `chown: Operation not permitted`.
- **Firewall Configuration**: Ensure NFS ports (2049, 111, etc.) are open on both server and client for connectivity.
- **Persistent Mounts**:
  To persist mounts across reboots, edit `/etc/fstab` on the client:
  ```bash
  sudo nano /etc/fstab
  ```
  Add:
  ```
  192.168.1.185:/mnt/mlflow /mnt/mlflow nfs defaults 0 0
  192.168.1.185:/mnt/postgres /mnt/postgres nfs defaults 0 0
  ```
  Save, then test:
  ```bash
  sudo systemctl daemon-reload
  sudo mount -a
  ```
- **Testing the Setup**:
  - On the server:
    ```bash
    sudo touch /mnt/mlflow/testfile.txt
    ```
  - On the client:
    ```bash
    ls /mnt/mlflow
    ```
    - Expect to see `testfile.txt`.

---

This updated guide ensures your NFS server supports both MLflow and PostgreSQL in your Kubernetes setup, with specific attention to PostgreSQL’s permission requirements. Apply these steps on `192.168.1.185` and your client nodes, then let me know if you need help integrating this with your Kubernetes deployment!
