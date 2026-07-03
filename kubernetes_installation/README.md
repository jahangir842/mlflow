# MLflow on Kubernetes (PostgreSQL + NFS)

Deploys an MLflow tracking server with a PostgreSQL backend on Kubernetes, using
an NFS server for persistent storage of PostgreSQL data and MLflow artifacts.

> **Which path should I use?** For most teams the
> [Docker Compose stack](../docker_compose_installation/README.md) (Postgres +
> MinIO + basic-auth) is simpler and is the recommended deployment. Use this
> Kubernetes path only if you already operate a cluster. This manifest set does
> not yet include MinIO or basic-auth — add an object-store artifact backend and
> an auth proxy (Ingress + oauth2-proxy, or MLflow basic-auth) before exposing
> it beyond a trusted network.

## Prerequisites

- A Kubernetes cluster and `kubectl`.
- The MLflow image `jahangir842/mlflow-with-psycopg2:v2.20.3` (or your own build
  of the repo `Dockerfile`) reachable from the cluster.
- An NFS server exporting `/mnt/postgres` and `/mnt/mlflow`. See
  [../Install_NFS_Server_for_mlflow _and _postgres.md](../Install_NFS_Server_for_mlflow%20_and%20_postgres.md).
  Update the `server:` IP in `postgres-pv-pvc.yaml` and `mlflow-pv-pvc.yaml` to
  match your NFS host.

## Deploy

```bash
# 1. Namespace
kubectl create namespace mlflow

# 2. Secret (credentials) -- copy the example, edit passwords, then apply.
cp secret.yaml.example secret.yaml
$EDITOR secret.yaml
kubectl apply -f secret.yaml

# 3. Storage
kubectl apply -f postgres-pv-pvc.yaml
kubectl apply -f mlflow-pv-pvc.yaml

# 4. Workloads
kubectl apply -f postgres-deployment.yaml
kubectl apply -f mlflow-deployment.yaml
```

`secret.yaml` is git-ignored; the Deployments read credentials from it via
`envFrom`, so no passwords live in the manifests.

## Verify

```bash
kubectl get pods -n mlflow -o wide     # both pods Running, 1/1 Ready
kubectl get pvc -n mlflow              # both Bound
kubectl logs -f deployment/mlflow -n mlflow
```

Access the UI at `http://<node-ip>:30500` (NodePort). For production, replace the
NodePort Service with an Ingress + TLS.

## Notes

- **Artifacts** are served through the tracking server (`--serve-artifacts`), so
  clients only need the server URL, not the NFS mount.
- **NFS permissions**: `/mnt/postgres` must be owned by UID/GID `999` with `700`
  perms (the container's `postgres` user) or Postgres fails to start.
- **Backup / restore**: see [backup_sql.md](backup_sql.md) and
  [restore_sql_backup.md](restore_sql_backup.md). Do not commit `.dump` files to
  git (they are git-ignored).
