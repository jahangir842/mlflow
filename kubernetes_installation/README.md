# MLflow on Kubernetes with NFS Persistence

This guide deploys an MLflow tracking server with a PostgreSQL backend on Kubernetes, leveraging an NFS server at `192.168.1.185` for persistent storage of PostgreSQL data and MLflow artifacts. It ensures data persists across pod restarts and node failures without requiring a StatefulSet.

---

## Prerequisites
- **Kubernetes Cluster**: A running cluster with at least one node.
- **kubectl**: Configured to manage your cluster.
- **MLflow Image**: `jahangir842/mlflow-with-psycopg2:v2.20.3` available in your container registry.
- **NFS Server**: Running at `192.168.1.185` with shared directories `/mnt/postgres` (for PostgreSQL) and `/mnt/mlflow` (for MLflow artifacts). See the NFS setup section if not configured.

---

## Step 1: Create Namespace
Set up a dedicated namespace for MLflow resources.

1. **Create and Activate Namespace**:
   ```bash
   kubectl create namespace mlflow
   kubectl config set-context --current --namespace=mlflow
   ```

2. **Verify Active Namespace**:
   ```bash
   kubectl config get-contexts
   ```
   - Confirm the current context (marked with `*`) shows `mlflow` as the namespace.

---

## Step 2: Create YAML Files with NFS Storage

### 1. PostgreSQL PersistentVolume and PersistentVolumeClaim
File: `postgres-pv-pvc.yaml`

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: postgres-pv
spec:
  capacity:
    storage: 5Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  nfs:
    path: /mnt/postgres  # NFS share for PostgreSQL data
    server: 192.168.1.185  # NFS server IP
---
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

### 2. MLflow PersistentVolume and PersistentVolumeClaim
File: `mlflow-pv-pvc.yaml`

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: mlflow-pv
spec:
  capacity:
    storage: 20Gi  # Increased from 10Gi for flexibility
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  nfs:
    path: /mnt/mlflow  # NFS share for MLflow artifacts
    server: 192.168.1.185  # NFS server IP
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mlflow-pvc
  namespace: mlflow
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
```

### 3. PostgreSQL Deployment, Service, and ConfigMap
File: `postgres-deployment.yaml`

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
        - name: init-script
          mountPath: /docker-entrypoint-initdb.d
        readinessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - admin
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 5
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
      - name: init-script
        configMap:
          name: postgres-config
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: mlflow
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: postgres-config
  namespace: mlflow
data:
  init.sql: |
    CREATE DATABASE mlflowdb;
    \c mlflowdb;
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

### 4. MLflow Deployment and Service
File: `mlflow-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mlflow
  namespace: mlflow
spec:
  selector:
    matchLabels:
      app: mlflow
  replicas: 1
  template:
    metadata:
      labels:
        app: mlflow
    spec:
      containers:
      - name: mlflow
        image: jahangir842/mlflow-with-psycopg2:v2.20.3
        resources:
          limits:
            memory: "1Gi"
            cpu: "500m"
          requests:
            memory: "512Mi"
            cpu: "250m"
        ports:
        - containerPort: 5000
        command:
        - mlflow
        - server
        - --host
        - 0.0.0.0
        - --port
        - "5000"
        - --backend-store-uri
        - postgresql://admin:pakistan@postgres:5432/mlflowdb
        - --default-artifact-root
        - file:///mlflow/artifacts
        readinessProbe:
          httpGet:
            path: /
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
        volumeMounts:
        - name: mlflow-artifacts
          mountPath: /mlflow/artifacts
      volumes:
      - name: mlflow-artifacts
        persistentVolumeClaim:
          claimName: mlflow-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: mlflow
  namespace: mlflow
spec:
  type: NodePort
  selector:
    app: mlflow
  ports:
  - port: 5000
    targetPort: 5000
    nodePort: 30500
```

---

## Step 3: Apply Kubernetes Configurations
Deploy the resources:
```bash
kubectl apply -f postgres-pv-pvc.yaml
kubectl apply -f mlflow-pv-pvc.yaml
kubectl apply -f postgres-deployment.yaml
kubectl apply -f mlflow-deployment.yaml
```

---

## Step 4: Verify the Setup

1. **Check Pods**:
   ```bash
   kubectl get pods -n mlflow -o wide
   ```
   - Expected: `mlflow-*` and `postgres-*` pods in `Running` state with `Ready: 1/1`.

2. **Check PVCs**:
   ```bash
   kubectl get pvc -n mlflow
   ```
   - Expected:
     ```
     NAME          STATUS   VOLUME        CAPACITY   ACCESS MODES
     mlflow-pvc    Bound    mlflow-pv     20Gi       RWO
     postgres-pvc  Bound    postgres-pv   5Gi        RWO
     ```

3. **Check PVs**:
   ```bash
   kubectl get pv
   ```
   - Expected:
     ```
     NAME          CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM
     mlflow-pv     20Gi       RWO            Retain           Bound    mlflow/mlflow-pvc
     postgres-pv   5Gi        RWO            Retain           Bound    mlflow/postgres-pvc
     ```

4. **Check Services**:
   ```bash
   kubectl get svc -n mlflow -o wide
   ```
   - Expected:
     ```
     NAME      TYPE       CLUSTER-IP     PORT(S)
     mlflow    NodePort   <cluster-ip>   5000:30500/TCP
     postgres  ClusterIP  <cluster-ip>   5432/TCP
     ```

5. **Check Logs**:
   - **PostgreSQL**:
     ```bash
     kubectl logs -f deployment/postgres -n mlflow
     ```
     - Expected: `database system is ready to accept connections`.
   - **MLflow**:
     ```bash
     kubectl logs -f deployment/mlflow -n mlflow
     ```
     - Expected: No `Connection refused` or `OperationalError` messages.

6. **Test Connectivity**:
   ```bash
   MLFLOW_POD=$(kubectl get pods -n mlflow -l app=mlflow -o jsonpath="{.items[0].metadata.name}")
   kubectl exec -it $MLFLOW_POD -n mlflow -- bash
   apt-get update && apt-get install -y netcat
   nc -zv postgres 5432
   exit
   ```
   - Expected: `Connection to postgres 5432 port [tcp/postgresql] succeeded!`

7. **Access MLflow UI**:
   ```bash
   kubectl get nodes -o wide
   ```
   - Open: `http://<node-ip>:30500` (e.g., `http://192.168.1.182:30500`).
   - Expected: MLflow UI loads successfully.

---

## Notes
- **NFS Persistence**: The NFS server at `192.168.1.185` ensures data persists across pod restarts and node failures.
- **PostgreSQL Permissions**: The `/mnt/postgres` directory must be owned by UID 999 (GID 999) with `700` permissions to avoid `chown` errors during PostgreSQL startup.
- **Readiness Probes**: Added to both MLflow and PostgreSQL to ensure they’re marked `Ready` only when fully operational.
- **Namespace**: Resources are in the `mlflow` namespace; recreate if missing (`kubectl create namespace mlflow`).
- **Networking**: If `No route to host` occurs, verify NFS connectivity and firewall rules on `192.168.1.185` and worker nodes.

---


---

## Next Steps
1. **Apply and Verify**:
   - Deploy the YAML files and share outputs from verification steps (e.g., `kubectl get pods -n mlflow -o wide`, `kubectl logs`).
2. **Restore Backup (If Applicable)**:
   If you have an MLflow database backup:
   ```bash
   POSTGRES_POD=$(kubectl get pods -n mlflow -l app=postgres -o jsonpath="{.items[0].metadata.name}")
   kubectl cp backup_mlflow.dump $POSTGRES_POD:/tmp/backup_mlflow.dump -n mlflow
   kubectl exec -it $POSTGRES_POD -n mlflow -- bash -c "PGPASSWORD=pakistan pg_restore -U admin -d mlflowdb --verbose /tmp/backup_mlflow.dump"
   ```
3. **Troubleshooting**:
   - If PostgreSQL crashes with `chown` errors, recheck `/mnt/postgres` permissions on `192.168.1.185`.
   - If MLflow isn’t ready, ensure PostgreSQL is stable first.

Let me know how it goes or if you need further assistance!