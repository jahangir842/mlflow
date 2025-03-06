### Guide to Switching PostgreSQL to an NFS Server (IP: 192.168.1.185)

#### Prerequisites
- **NFS Server Ready**: An NFS server is running at `192.168.1.185` with a shared directory (e.g., `/mnt/mlflow`). If not set up yet, follow the NFS server installation steps at the end of this guide first.
- **Existing Setup**: Your PostgreSQL pod (`postgres-f7bf59fd9-xb2lz`) is running with a `hostPath` PV (`postgres-pv`) and PVC (`postgres-pvc`).
- **Access**: You have `kubectl` configured and SSH access to the NFS server (if needed for setup).

---

### Step 1: Backup Your Current Database
Before making changes, back up your existing `mlflowdb` to avoid data loss.

1. **Set the Pod Variable**:
   ```bash
   POSTGRES_POD=$(kubectl get pods -n mlflow -l app=postgres -o jsonpath="{.items[0].metadata.name}")
   echo $POSTGRES_POD
   ```

2. **Create a Dump**:
   ```bash
   kubectl exec $POSTGRES_POD -n mlflow -- bash -c "PGPASSWORD=pakistan pg_dump -U admin -d mlflowdb -Fc -f /tmp/backup_mlflow.dump"
   ```

3. **Copy the Backup Locally**:
   ```bash
   kubectl cp $POSTGRES_POD:/tmp/backup_mlflow.dump ./backup_mlflow.dump -n mlflow
   ```

4. **Clean Up**:
   ```bash
   kubectl exec $POSTGRES_POD -n mlflow -- rm /tmp/backup_mlflow.dump
   ```

Store `backup_mlflow.dump` safely as a precaution.

---

### Step 2: Update the PersistentVolume to Use NFS
Modify your PV to point to the NFS server instead of `hostPath`.

1. **Edit or Recreate the PV**:
   - If you want to modify the existing `postgres-pv`, delete it first (after ensuring the pod is stopped—see Step 3), or create a new PV with a different name.
   - Here’s the new PV configuration:

   ```yaml
   apiVersion: v1
   kind: PersistentVolume
   metadata:
     name: postgres-nfs-pv  # New name to avoid conflicts; adjust if reusing postgres-pv
   spec:
     capacity:
       storage: 5Gi
     accessModes:
       - ReadWriteOnce
     persistentVolumeReclaimPolicy: Retain
     nfs:
       path: /mnt/mlflow  # NFS share path on the server
       server: 192.168.1.185  # NFS server IP
   ```

   Save this as `postgres-nfs-pv.yaml`.

2. **Apply the New PV** (if creating a new one):
   ```bash
   kubectl apply -f postgres-nfs-pv.yaml
   ```

---

### Step 3: Update the PersistentVolumeClaim (if Needed)
Your existing PVC (`postgres-pvc`) should work with the new PV as long as the `accessModes` and `storage` match. If you created a new PV (`postgres-nfs-pv`), you’ll need to update the PVC or recreate it.

1. **Check the Current PVC**:
   ```bash
   kubectl get pvc -n mlflow
   ```
   - Output should show `postgres-pvc` bound to `postgres-pv`.

2. **Option 1: Reuse Existing PVC**:
   - If keeping the same PVC name, delete the old PV and PVC after stopping the pod:
     ```bash
     kubectl delete pod $POSTGRES_POD -n mlflow
     kubectl delete pvc postgres-pvc -n mlflow
     kubectl delete pv postgres-pv
     ```
   - Recreate the PVC:
     ```yaml
     apiVersion: v1
     kind: PersistentVolumeClaim
     metadata:
       name: postgres-pvc
       namespace: mlflow
     spec:
       accessModes:
         - ReadWriteOnce
       resources:
         requests:
           storage: 5Gi
     ```
     Save as `postgres-pvc.yaml` and apply:
     ```bash
     kubectl apply -f postgres-pvc.yaml
     ```
   - The PVC will bind to `postgres-nfs-pv`.

3. **Option 2: Create a New PVC** (if using a new PV name):
   ```yaml
   apiVersion: v1
   kind: PersistentVolumeClaim
   metadata:
     name: postgres-nfs-pvc
     namespace: mlflow
   spec:
     accessModes:
       - ReadWriteOnce
     resources:
       requests:
         storage: 5Gi
   ```
   Save as `postgres-nfs-pvc.yaml` and apply:
   ```bash
   kubectl apply -f postgres-nfs-pvc.yaml
   ```
   - Update the Deployment in Step 4 to use `postgres-nfs-pvc`.

---

### Step 4: Update the PostgreSQL Deployment
Modify your PostgreSQL Deployment to use the NFS-backed PVC.

1. **Edit the Deployment**:
   If using the new PVC (`postgres-nfs-pvc`), update the `claimName`. Here’s the modified section:
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: postgres
     namespace: mlflow
   spec:
     selector:
       matchLabels:
         app: postgres
     replicas: 1
     template:
       metadata:
         labels:
           app: postgres
       spec:
         containers:
         - name: postgres
           image: postgres:14
           resources:
             limits:
               memory: "1Gi"
               cpu: "500m"
             requests:
               memory: "512Mi"
               cpu: "250m"
           env:
           - name: POSTGRES_USER
             value: "admin"
           - name: POSTGRES_PASSWORD
             value: "pakistan"
           - name: POSTGRES_DB
             value: "mlflowdb"
           ports:
           - containerPort: 5432
           volumeMounts:
           - name: postgres-storage
             mountPath: /var/lib/postgresql/data
         volumes:
         - name: postgres-storage
           persistentVolumeClaim:
             claimName: postgres-nfs-pvc  # Update this if using a new PVC; otherwise keep postgres-pvc
   ```

   Save as `postgres-deployment-nfs.yaml`.

2. **Apply the Updated Deployment**:
   ```bash
   kubectl apply -f postgres-deployment-nfs.yaml
   ```

3. **Wait for the Pod to Recreate**:
   ```bash
   kubectl get pods -n mlflow -w
   ```
   - Look for a new `postgres-` pod in the `Running` state.

---

### Step 5: Restore the Database
Since the NFS volume is new, restore your MLflow data from the backup.

1. **Copy the Backup to the Pod**:
   ```bash
   kubectl cp ./backup_mlflow.dump $POSTGRES_POD:/tmp/backup_mlflow.dump -n mlflow
   ```

2. **Exec into the Pod**:
   ```bash
   kubectl exec -it $POSTGRES_POD -n mlflow -- bash
   ```

3. **Set the Password**:
   ```bash
   export PGPASSWORD=pakistan
   ```

4. **Create the Database**:
   ```bash
   psql -U admin -d postgres -c "CREATE DATABASE mlflowdb;"
   psql -U admin -d mlflowdb -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
   ```

5. **Restore the Dump**:
   ```bash
   pg_restore -U admin -d mlflowdb --verbose /tmp/backup_mlflow.dump
   ```

6. **Verify the Data**:
   ```bash
   psql -U admin -d mlflowdb -c "SELECT * FROM experiments LIMIT 5;"
   ```

7. **Exit and Clean Up**:
   ```bash
   rm /tmp/backup_mlflow.dump
   exit
   ```

---

### Step 6: Verify Persistence
Test that the data persists across nodes.

1. **Delete the Pod**:
   ```bash
   kubectl delete pod $POSTGRES_POD -n mlflow
   ```

2. **Check the New Pod**:
   ```bash
   kubectl get pods -n mlflow -o wide
   ```
   - Note the node it’s running on.

3. **Verify Data**:
   ```bash
   kubectl exec -it $(kubectl get pods -n mlflow -l app=postgres -o jsonpath="{.items[0].metadata.name}") -n mlflow -- psql -U admin -d mlflowdb -c "SELECT * FROM experiments LIMIT 5;"
   ```
   - Data should still be there, regardless of the node.

---

### Optional: Set Up the NFS Server (If Not Already Done)
If `192.168.1.185` isn’t yet an NFS server, configure it (assuming RHEL-based):

1. **Install NFS Utilities**:
   ```bash
   sudo dnf install nfs-utils -y
   ```

2. **Create the Shared Directory**:
   ```bash
   sudo mkdir -p /mnt/mlflow
   sudo chown nobody:nobody /mnt/mlflow
   sudo chmod 777 /mnt/mlflow
   ```

3. **Configure Exports**:
   ```bash
   sudo nano /etc/exports
   ```
   Add:
   ```
   /mnt/mlflow 192.168.1.0/24(rw,sync,no_subtree_check)
   ```
   Save and exit.

4. **Start NFS**:
   ```bash
   sudo exportfs -a
   sudo systemctl enable --now nfs-server
   sudo firewall-cmd --permanent --add-service=nfs
   sudo firewall-cmd --reload
   ```

---

### Conclusion
Your PostgreSQL database is now backed by an NFS server at `192.168.1.185`, making it persistent across pod restarts and node failures without needing a StatefulSet. The data lives on the NFS share (`/mnt/mlflow`), accessible cluster-wide. Run the steps above and let me know the output (e.g., from `pg_restore` or verification) or if you hit any snags! Want to test it further or adjust anything?