# MLflow with Docker Compose (PostgreSQL + MinIO + Auth)

Production-style, self-hosted MLflow tracking server for a team of remote
developers. This is the **recommended** deployment path in this repo.

## Architecture

```
                     ┌─────────┐     ┌───────────────────────────┐
  developer laptop ─►│  Caddy  │ ──► │  mlflow server  :5000      │
  (mlflow client)    │  :80    │     │  - basic auth (user/pass)  │
                     └─────────┘     │  - proxied artifact serving│
                                     └────────┬───────────┬───────┘
                                  backend store│           │artifact store
                                              ▼           ▼
                                      ┌────────────┐  ┌────────────┐
                                      │ PostgreSQL │  │   MinIO    │
                                      │ (metadata) │  │ (S3 bucket)│
                                      └────────────┘  └────────────┘
```

A Caddy reverse proxy publishes MLflow on port **80**, so clients use
`http://<host>` with no `:5000`. MLflow itself is not published to the host.

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
cd installation/docker_compose_installation
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

- **MLflow UI**: http://<server-ip> — you'll be prompted for the admin
  username/password from `.env`.
- **MinIO console**: http://<server-ip>:9001 — log in with `MINIO_ROOT_USER` /
  `MINIO_ROOT_PASSWORD`; you should see the `mlflow` bucket.

## Client usage (developers)

Each developer installs the client and points at the server. Credentials go in
environment variables — never hardcode them in scripts.

```bash
pip install mlflow

export MLFLOW_TRACKING_URI="http://<server-ip>"
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

## Enable / disable authentication

Auth is controlled by a single switch in `.env`:

```bash
MLFLOW_AUTH_ENABLED=true    # login required (basic-auth) -- recommended
MLFLOW_AUTH_ENABLED=false   # open server, no login at all
```

To change it on a running stack, edit `.env` and recreate the MLflow container:

```bash
# turn OFF (open access)
sed -i 's/^MLFLOW_AUTH_ENABLED=.*/MLFLOW_AUTH_ENABLED=false/' .env
docker compose up -d mlflow

# turn ON (login required)
sed -i 's/^MLFLOW_AUTH_ENABLED=.*/MLFLOW_AUTH_ENABLED=true/' .env
docker compose up -d mlflow
```

Check which mode is active in the startup log:

```bash
docker compose logs mlflow | grep basic-auth
# ">> basic-auth ENABLED (login required)"  or  ">> basic-auth DISABLED (open server...)"
```

Notes:
- **Disabled = fully open.** Anyone who can reach the server has read/write/delete
  access to all experiments, models, and artifacts. Only do this on a trusted
  network, and ideally restrict port 80 at the firewall.
- User accounts persist in the `mlflow_auth` volume while auth is off, so
  re-enabling restores them — no need to recreate users.

## Managing users

> Applies when `MLFLOW_AUTH_ENABLED=true`.

The bootstrap admin (from `.env`) can create per-developer accounts. See the
MLflow auth REST API, e.g. create a user:

```bash
curl -u admin:admin-password -X POST http://<server-ip>/api/2.0/mlflow/users/create \
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
- Basic-auth protects the API/UI, and access is via the Caddy proxy on port 80.
  **This is plain HTTP — credentials are not encrypted in transit**, so only run
  it on a trusted LAN. For untrusted networks, enable TLS in the `Caddyfile`
  (swap the `:80` site for your domain and remove `auto_https off`; Caddy then
  provisions a certificate automatically).
- Postgres and MLflow are not published to the host (internal network only).
  MinIO ports 9000/9001 are published for convenience — restrict them in production.
