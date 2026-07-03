# Self-Hosted MLflow for Teams

Deploy a centralized [MLflow](https://mlflow.org/) tracking server so multiple
developers can log experiments, register models, and share artifacts from any
machine. Backed by **PostgreSQL** (metadata) and an **S3-compatible object
store** (artifacts), with per-user **authentication**.

## Using MLflow (developers)

If the server is already running and you just want to log experiments, see the
**[Developers Guide](developers-guide.md)** — client setup, logging runs/models, the
model registry, and troubleshooting.

## Deployment options

| Method | When to use | Guide |
|--------|-------------|-------|
| **Docker Compose** ⭐ | Single server/VM. Simplest, fully self-contained (Postgres + MinIO + auth). **Recommended.** | [docker_compose_installation](installation/docker_compose_installation/README.md) |
| **Kubernetes** | You already run a cluster. | [kubernetes_installation](installation/kubernetes_installation/README.md) |
| **Linux + systemd** | Bare metal / VM without containers. | [linux_installation](installation/linux_installation/README.md) |
| **Ansible** | Automate provisioning the Compose stack on a remote host. | [ansible](installation/ansible/README.md) |

## Architecture (recommended Compose stack)

```
  developers ──► Caddy :80 ──► MLflow server ──► PostgreSQL   (runs, params, metrics, registry)
   (client)     (reverse       (auth + proxied   └► MinIO / S3 (artifacts: models, plots, files)
                 proxy)         artifact serving)
```

The tracking server proxies artifacts, so **remote developers only need the
server URL and their credentials** — no NFS mounts, no S3 keys on the client.

## Quick start (Docker Compose)

```bash
git clone https://github.com/jahangir842/mlflow.git
cd mlflow/installation/docker_compose_installation
cp .env.example .env          # then edit and change EVERY password
docker compose up -d --build
```

Open `http://<server-ip>` (the Caddy proxy serves on port 80 — no `:5000`) and
log in with the admin credentials from `.env`.
Full walkthrough, client setup, user management, and backups:
**[installation/docker_compose_installation/README.md](installation/docker_compose_installation/README.md)**.

## Images

- **Base**: [ghcr.io/mlflow/mlflow](https://github.com/mlflow/mlflow/pkgs/container/mlflow)
- **Custom** (this repo's `installation/Dockerfile`, adds `psycopg2` + `boto3`):
  [jahangir842/mlflow-with-psycopg2](https://hub.docker.com/repository/docker/jahangir842/mlflow-with-psycopg2/general)

## Security

- All credentials live in `.env` / Kubernetes `Secret` (git-ignored) — never in
  the repo.
- MLflow basic-auth is enabled by default in the Compose stack. For internet
  exposure, add a TLS reverse proxy — see
  [linux_installation/authentication_for_mlflow.md](installation/linux_installation/authentication_for_mlflow.md).
- If you previously used the committed default password, rotate it now.
