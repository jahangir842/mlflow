# MLflow on Kubernetes

This guide explains how to deploy MLflow tracking server with PostgreSQL backend on Kubernetes. MLflow helps you track your machine learning experiments, manage models, and deploy them.

## Architecture Overview

The deployment consists of:
1. **PostgreSQL Database**
   - Stores MLflow metadata (experiments, runs, parameters, metrics)
   - Persistent storage using Kubernetes PV/PVC
   - Internal service accessible only within cluster

2. **MLflow Tracking Server**
   - Web UI and API for experiment tracking
   - Connects to PostgreSQL for metadata storage
   - Stores artifacts in persistent volume
   - Exposed via NodePort for external access

```ascii
                   ┌──────────────┐
External Access    │   MLflow UI  │
(Port 30500) ─────►|  (Service)   │
                   └──────┬───────┘
                         │
                   ┌─────▼──────┐      ┌────────────┐
                   │   MLflow   │      │ PostgreSQL │
                   │   Server   ├─────►│  Database  │
                   └─────┬──────┘      └─────┬──────┘
                         │                   │
                   ┌─────▼───────┐     ┌─────▼──────┐
                   │   MLflow    │     │ PostgreSQL │
                   │  Artifacts  │     │   Data     │
                   │  Storage    │     │  Storage   │
                   └─────────────┘     └────────────┘
```

## Prerequisites

1. **Kubernetes Cluster**
   - Minikube, kind, or any other Kubernetes cluster
   - kubectl installed and configured

2. **Storage**
   - At least 5GB for PostgreSQL
   - At least 10GB for MLflow artifacts

3. **MLflow Image**
   - Image: `jahangir842/mlflow-with-psycopg2:v2.20.3`
   - Docker Hub: [MLflow with PostgreSQL Client](https://hub.docker.com/repository/docker/jahangir842/mlflow-with-psycopg2/general)
   - Contains:
     - MLflow v2.20.3
     - PostgreSQL client (psycopg2)
     - Required Python dependencies

## Component Details

### 1. Persistent Volumes
- **PostgreSQL PV/PVC**: 5GB for database storage
- **MLflow PV/PVC**: 10GB for experiment artifacts
- Both use hostPath for local development

### 2. PostgreSQL Deployment
- Image: postgres:14
- Environment variables for database configuration
- Resource limits:
  - Memory: 512Mi - 1Gi
  - CPU: 250m - 500m

### 3. MLflow Deployment
- Custom image with MLflow and PostgreSQL client
- Resource limits:
  - Memory: 256Mi - 512Mi
  - CPU: 250m - 500m
- NodePort service exposing port 30500

## Step-by-Step Deployment

1. **Create Namespace and Set Context**:
```bash
# Create dedicated namespace
kubectl create namespace mlflow

# Set it as default for subsequent commands
kubectl config set-context --current --namespace=mlflow

# Verify namespace is set
kubectl config view --minify | grep namespace
```

2. **Create Storage**:
```bash
# Create PV and PVC for both PostgreSQL and MLflow
kubectl apply -f k8s/postgres-pv-pvc.yaml
kubectl apply -f k8s/mlflow-pv-pvc.yaml

# Verify PVCs are bound
kubectl get pvc
```

3. **Deploy PostgreSQL**:
```bash
kubectl apply -f k8s/postgres.yaml

# Wait for PostgreSQL pod to be ready
kubectl get pods -l app=postgres -w
```

4. **Deploy MLflow**:
```bash
kubectl apply -f k8s/mlflow.yaml

# Wait for MLflow pod to be ready
kubectl get pods -l app=mlflow -w
```

## Accessing MLflow

1. **Get Node IP**:
```bash
# If using Minikube
minikube ip

# Or get node IP
kubectl get nodes -o wide
```

2. **Access UI**: Open in browser
```
http://<node-ip>:30500
```

## Using MLflow

1. **Set Environment Variable**:
```bash
export MLFLOW_TRACKING_URI=http://<node-ip>:30500
```

2. **Basic Python Example**:
```python
import mlflow

# Start a new experiment
mlflow.set_experiment("my-experiment")

# Start a new run
with mlflow.start_run():
    # Log parameters
    mlflow.log_param("param1", 5)
    
    # Log metrics
    mlflow.log_metric("accuracy", 0.95)
    
    # Log artifacts
    with open("example.txt", "w") as f:
        f.write("Hello MLflow")
    mlflow.log_artifact("example.txt")
```

## Monitoring and Troubleshooting

### Check Component Status
```bash
# Get all resources
kubectl get all

# Check storage
kubectl get pv,pvc
```

### View Logs
```bash
# MLflow logs
kubectl logs -f deployment/mlflow

# PostgreSQL logs
kubectl logs -f deployment/postgres
```

### Database Connectivity
```bash
# Get PostgreSQL pod name
export PG_POD=$(kubectl get pods -l app=postgres -o jsonpath='{.items[0].metadata.name}')

# Test database connection
kubectl exec -it $PG_POD -- psql -U admin -d mlflowdb -c "\l"
```

## Resource Management

Both services have resource limits defined:
- **PostgreSQL**: 512Mi-1Gi RAM, 250m-500m CPU
- **MLflow**: 256Mi-512Mi RAM, 250m-500m CPU

Monitor resource usage:
```bash
kubectl top pods
```

## Cleanup

Remove all resources:
```bash
kubectl delete namespace mlflow
```

## Common Issues

1. **PostgreSQL Pod Crashes**
   - Check logs: `kubectl logs deployment/postgres`
   - Verify PVC is bound: `kubectl get pvc`
   - Check storage permissions

2. **MLflow Can't Connect**
   - Verify PostgreSQL pod is running
   - Check service: `kubectl get svc postgres`
   - Test connectivity from MLflow pod

3. **Can't Access UI**
   - Verify node IP is correct
   - Check MLflow service: `kubectl get svc mlflow`
   - Ensure port 30500 is accessible

## Database Backup and Restore

### Creating Backups

1. **Create a Full Database Backup**:
```bash
# Get PostgreSQL pod name
export PG_POD=$(kubectl get pods -l app=postgres -o jsonpath='{.items[0].metadata.name}')

# Create backup
kubectl exec -it $PG_POD -- pg_dump -U admin -d mlflowdb > mlflow_backup.sql

# Create compressed backup
kubectl exec -it $PG_POD -- pg_dump -U admin -d mlflowdb | gzip > mlflow_backup.sql.gz
```

2. **Backup Specific Tables**:
```bash
# Backup only experiment and run tables
kubectl exec -it $PG_POD -- pg_dump -U admin -d mlflowdb \
  -t experiments -t runs > experiments_runs_backup.sql
```

### Restoring Backups

1. **Restore Full Database**:
```bash
# Copy backup file to pod
kubectl cp mlflow_backup.sql $PG_POD:/tmp/

# Restore database
kubectl exec -it $PG_POD -- psql -U admin -d mlflowdb -f /tmp/mlflow_backup.sql

# For compressed backup
cat mlflow_backup.sql.gz | gunzip | kubectl exec -i $PG_POD -- psql -U admin -d mlflowdb
```

2. **Clean Restore (if needed)**:
```bash
# First drop the database
kubectl exec -it $PG_POD -- psql -U admin -c "DROP DATABASE mlflowdb;"

# Recreate the database
kubectl exec -it $PG_POD -- psql -U admin -c "CREATE DATABASE mlflowdb;"

# Then restore
kubectl exec -it $PG_POD -- psql -U admin -d mlflowdb -f /tmp/mlflow_backup.sql
```

### Backup Best Practices

1. **Regular Backups**:
```bash
# Create a dated backup
backup_file="mlflow_$(date +%Y%m%d_%H%M%S).sql.gz"
kubectl exec -it $PG_POD -- pg_dump -U admin -d mlflowdb | gzip > $backup_file
```

2. **Verify Backup**:
```bash
# Check backup file size
ls -lh mlflow_backup.sql.gz

# Quick verification of backup content
zcat mlflow_backup.sql.gz | head -n 20
```

3. **Test Restore**:
```bash
# Create a test database
kubectl exec -it $PG_POD -- psql -U admin -c "CREATE DATABASE mlflowdb_test;"

# Restore to test database
zcat mlflow_backup.sql.gz | kubectl exec -i $PG_POD -- psql -U admin -d mlflowdb_test

# Verify test database
kubectl exec -it $PG_POD -- psql -U admin -d mlflowdb_test -c "\dt"
```

### Backup Artifacts

Remember to also backup MLflow artifacts:
```bash
# Get MLflow pod name
export MLFLOW_POD=$(kubectl get pods -l app=mlflow -o jsonpath='{.items[0].metadata.name}')

# Backup artifacts directory
kubectl exec -it $MLFLOW_POD -- tar czf - /mlflow/artifacts > mlflow_artifacts.tar.gz

# Restore artifacts
kubectl cp mlflow_artifacts.tar.gz $MLFLOW_POD:/tmp/
kubectl exec -it $MLFLOW_POD -- tar xzf /tmp/mlflow_artifacts.tar.gz -C /
```
