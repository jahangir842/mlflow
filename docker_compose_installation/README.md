# MLflow with Docker Compose (PostgreSQL + MinIO + Auth)

Production-style, self-hosted MLflow tracking server for a team of remote
developers. This is the **recommended** deployment path in this repo.

## Architecture

```
                         ┌───────────────────────────┐
  developer laptop  ───► │  mlflow server  :5000      │
  (mlflow client)        │  - basic auth (user/pass)  │
                         │  - proxied artifact serving│
                         └────────┬───────────┬───────┘
                                  │           │
                     backend store│           │artifact store
                                  ▼           ▼
                          ┌────────────┐  ┌────────────┐
                          │ PostgreSQL │  │   MinIO    │
                          │ (metadata) │  │ (S3 bucket)│
                          └────────────┘  └────────────┘
```

**Why this design:** With proxied artifact serving (`--serve-artifacts`),
clients talk **only** to the MLflow server. They do not need NFS mounts or S3
credentials — the server streams artifacts to/from MinIO on their behalf. This
is what makes it work for remote developers on any network, unlike the older
`file://` + NFS approach.

## Prerequisites

- Docker Engine + Docker Compose v2 ([install guide](https://docs.docker.com/engine/install/))

## Setup

### 1. Configure secrets

```bash
cd docker_compose_installation
cp .env.example .env
# Edit .env and change EVERY password.
```

### 2. Build and start

```bash
# Builds the custom MLflow image (adds psycopg2 + boto3) and starts everything
docker compose up -d --build

# Watch startup (postgres + minio become healthy, bucket is created, then mlflow starts)
docker compose ps
docker compose logs -f mlflow
```

### 3. Verify

- **MLflow UI**: http://<server-ip>:5000 — you'll be prompted for the admin
  username/password from `.env`.
- **MinIO console**: http://<server-ip>:9001 — log in with `MINIO_ROOT_USER` /
  `MINIO_ROOT_PASSWORD`; you should see the `mlflow` bucket.

## Client usage (developers)

Each developer installs the client and points at the server. Credentials go in
environment variables — never hardcode them in scripts.

```bash
pip install mlflow

export MLFLOW_TRACKING_URI="http://<server-ip>:5000"
export MLFLOW_TRACKING_USERNAME="your-username"
export MLFLOW_TRACKING_PASSWORD="your-password"
```

```python
import mlflow

mlflow.set_experiment("demo")
with mlflow.start_run():
    mlflow.log_param("lr", 0.001)
    mlflow.log_metric("accuracy", 0.92)
    mlflow.log_artifact("model.pkl")   # streamed to MinIO via the server
```

## Managing users

The bootstrap admin (from `.env`) can create per-developer accounts. See the
MLflow auth REST API, e.g. create a user:

```bash
curl -u admin:admin-password -X POST http://<server-ip>:5000/api/2.0/mlflow/users/create \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "alice-password"}'
```

Permissions default to `READ` for new users (`default_permission` in the
generated `basic_auth.ini`); grant per-experiment permissions as needed. See the
[MLflow authentication docs](https://mlflow.org/docs/latest/auth/index.html).

## Common commands

```bash
docker compose up -d --build        # start / rebuild
docker compose ps                   # status + health
docker compose logs -f mlflow       # tail server logs
docker compose down                 # stop (keeps data volumes)
docker compose down -v              # stop AND delete all data (danger!)
```

## Backups

Two things to back up:

1. **PostgreSQL** (all run metadata + model registry):
   ```bash
   docker compose exec postgres pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > mlflow_pg_backup.sql
   ```
2. **MinIO bucket** (artifacts): mirror it out with `mc`, or snapshot the
   `minio_data` volume.

## Security notes

- All credentials come from `.env` (git-ignored). No secrets in the repo.
- Basic-auth protects the API/UI. For internet exposure, additionally put the
  server behind a TLS reverse proxy (Nginx/Caddy/Traefik) so credentials aren't
  sent in clear text. See `../linux_installation/authentication_for_mlflow.md`.
- Postgres is not published to the host (internal network only). MinIO ports
  9000/9001 are published for convenience — restrict them in production.
