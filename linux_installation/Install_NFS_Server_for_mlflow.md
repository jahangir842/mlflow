Below is a rewritten guide for setting up an NFS server and client, including commands for both Ubuntu/Debian (using `apt`) and RHEL-based systems (using `dnf` or `yum`). The guide follows the same structure as your original, with added RHEL-specific instructions based on standard practices and references like the one you linked (Medium article on RHEL 8 NFS setup).

---

### NFS Server Installation

Follow these steps to set up an NFS server on either an Ubuntu/Debian or RHEL-based system.

---

### Step 1: Install the NFS Kernel Server

Install the NFS server package on the host machine.

#### For Ubuntu/Debian:
1. **Update the Package Repository**:
   Ensure the latest package versions are available:
   ```bash
   sudo apt update
   ```

2. **Install the NFS Kernel Server**:
   ```bash
   sudo apt install nfs-kernel-server -y
   ```
   - The `-y` flag automatically confirms the installation.

3. **Enable and Start the NFS Service**:
   ```bash
   sudo systemctl enable --now nfs-server
   sudo systemctl start nfs-server
   ```

#### For RHEL-Based Systems (RHEL 8/9, CentOS, Rocky Linux, etc.):
1. **Update the Package Repository**:
   Ensure the latest package versions are available:
   ```bash
   sudo dnf update -y
   ```
   - Use `yum update -y` if `dnf` is unavailable (e.g., older CentOS versions).

2. **Install the NFS Utilities**:
   RHEL uses `nfs-utils` for NFS server functionality:
   ```bash
   sudo dnf install nfs-utils -y
   ```
   - Use `yum install nfs-utils -y` for older systems.

3. **Enable and Start the NFS Service**:
   ```bash
   sudo systemctl enable --now nfs-server
   sudo systemctl start nfs-server
   ```

---

### Step 2: Configure the Shared Directory

Set up a directory to share with client machines.

#### For Both Ubuntu/Debian and RHEL:
1. **Create the Directory**:
   ```bash
   sudo mkdir -p /mnt/mlflow
   ```
   - Note: Your original guide had `/mnt/` and later `/mnt/nfsdir`. I’ve standardized it to `/mnt/mlflow` for consistency with your MLflow context. Adjust as needed.

2. **Change Ownership**:
   Set the directory’s ownership to `nobody:nogroup` (Ubuntu/Debian) or `nobody:nobody` (RHEL) for public access:
   - **Ubuntu/Debian**:
     ```bash
     sudo chown nobody:nogroup /mnt/mlflow
     ```
   - **RHEL**:
     ```bash
     sudo chown nobody:nobody /mnt/mlflow
     ```
     - RHEL typically uses `nobody:nobody` as the default unprivileged user/group.

3. **Set Permissions**:
   Allow read, write, and execute access for everyone:
   ```bash
   sudo chmod 777 /mnt/mlflow
   ```

---

### Step 3: Configure Access in the Exports File

Grant client access by editing the `/etc/exports` file. This step is identical for both Ubuntu/Debian and RHEL.

1. **Open the Exports File**:
   Use a text editor (e.g., `nano` or `vi`):
   ```bash
   sudo nano /etc/exports
   ```

2. **Add Client Access**:
   Specify the directory and permissions for a single client:
   ```bash
   /mnt/mlflow clientIP(rw,sync,no_subtree_check)
   ```
   - Replace `clientIP` with the client’s IP address (e.g., `192.168.1.100`).

3. **Add Subnet Access** (Optional):
   To allow an entire subnet (e.g., `192.168.1.0-192.168.1.255`):
   ```bash
   /mnt/mlflow 192.168.1.0/24(rw,sync,no_subtree_check)
   ```
   - **rw**: Read and write access.
   - **sync**: Ensures data is written to disk before responding.
   - **no_subtree_check**: Disables subtree checking for better performance.

4. **Save and Exit**:
   - In `nano`, press `Ctrl+O`, `Enter`, then `Ctrl+X`.
   - In `vi`, type `:wq` and press `Enter`.

---

### Step 4: Export the Shared Directory

Apply the changes to make the directory available.

#### For Both Ubuntu/Debian and RHEL:
1. **Export the Shared Directories**:
   ```bash
   sudo exportfs -a
   ```
   - This exports all directories listed in `/etc/exports`.

2. **Restart the NFS Server**:
   - **Ubuntu/Debian**:
     ```bash
     sudo systemctl restart nfs-kernel-server
     ```
   - **RHEL**:
     ```bash
     sudo systemctl restart nfs-server
     ```

Your NFS server is now configured and ready to share `/mnt/mlflow` with clients.

---

## Client-End Configurations

Configure client machines to access the NFS share.

---

### Step 1: Install NFS Client Utilities

Install the necessary packages on the client machine.

#### For Ubuntu/Debian:
1. **Update the Package Index**:
   ```bash
   sudo apt update
   ```

2. **Install NFS Common**:
   ```bash
   sudo apt install nfs-common -y
   ```

#### For RHEL-Based Systems:
1. **Update the Package Repository**:
   ```bash
   sudo dnf update -y
   ```
   - Use `yum update -y` for older systems.

2. **Install NFS Utilities**:
   ```bash
   sudo dnf install nfs-utils -y
   ```
   - Use `yum install nfs-utils -y` for older systems.
   - `nfs-utils` includes both server and client tools on RHEL.

---

### Step 2: Create a Mount Point

Create a directory on the client to mount the NFS share.

#### For Both Ubuntu/Debian and RHEL:
```bash
sudo mkdir -p /mnt/mlflow
```

---

### Step 3: Mount the Shared Directory

Mount the NFS server’s shared directory to the client’s mount point.

#### For Both Ubuntu/Debian and RHEL:
1. **Mount the Directory**:
   ```bash
   sudo mount host_IP:/mnt/mlflow /mnt/mlflow
   ```
   - Replace `host_IP` with the NFS server’s IP (e.g., `192.168.1.147`).
   - Example:
     ```bash
     sudo mount 192.168.1.147:/mnt/mlflow /mnt/mlflow
     ```

2. **Verify the Mount**:
   Check that the share is mounted:
   ```bash
   df -h
   ```
   - Look for an entry like `192.168.1.147:/mnt/mlflow` under the `Filesystem` column.

Once mounted, the client can access the shared files at `/mnt/mlflow`.

---

### Additional Notes
- **Firewall Configuration (RHEL)**:
  On RHEL systems, you may need to allow NFS traffic through the firewall:
  ```bash
  sudo firewall-cmd --permanent --add-service=nfs
  sudo firewall-cmd --permanent --add-service=mountd
  sudo firewall-cmd --permanent --add-service=rpc-bind
  sudo firewall-cmd --reload
  ```

- **Persistent Mounts**:
  To make the mount persistent across reboots, add an entry to `/etc/fstab` on the client:
  ```bash
  sudo nano /etc/fstab
  ```
  Add:
  ```
  192.168.1.147:/mnt/mlflow /mnt/mlflow nfs defaults 0 0
  ```
  Save and exit, then test with:
  ```bash
  sudo mount -a
  ```

- **Testing the Setup**:
  On the server, create a test file:
  ```bash
  sudo touch /mnt/mlflow/testfile.txt
  ```
  On the client, check if it’s visible:
  ```bash
  ls /mnt/mlflow
  ```

---

This guide now supports both Ubuntu/Debian and RHEL-based systems, with consistent commands and additional considerations (e.g., firewall for RHEL). Let me know if you need further adjustments or help integrating this with your MLflow setup!
