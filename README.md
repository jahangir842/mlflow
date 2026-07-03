# Self-Hosted MLflow for Teams

Deploy a centralized [MLflow](https://mlflow.org/) tracking server so multiple
developers can log experiments, register models, and share artifacts from any
machine. Backed by **PostgreSQL** (metadata) and an **S3-compatible object
store** (artifacts), with per-user **authentication**.

## Deployment options

| Method | When to use | Guide |
|--------|-------------|-------|
| **Docker Compose** ⭐ | Single server/VM. Simplest, fully self-contained (Postgres + MinIO + auth). **Recommended.** | [docker_compose_installation](docker_compose_installation/README.md) |
| **Kubernetes** | You already run a cluster. | [kubernetes_installation](kubernetes_installation/README.md) |
| **Linux + systemd** | Bare metal / VM without containers. | [linux_installation](linux_installation/README.md) |
| **Ansible** | Automate provisioning the Compose stack on a remote host. | [ansible](ansible/README.md) |

## Architecture (recommended Compose stack)

```
  developers ──► MLflow server :5000 ──► PostgreSQL   (runs, params, metrics, registry)
   (client)     (auth + proxied         └► MinIO / S3 (artifacts: models, plots, files)
                 artifact serving)
```

The tracking server proxies artifacts, so **remote developers only need the
server URL and their credentials** — no NFS mounts, no S3 keys on the client.

## Quick start (Docker Compose)

```bash
git clone https://github.com/jahangir842/mlflow.git
cd mlflow/docker_compose_installation
cp .env.example .env          # then edit and change EVERY password
docker compose up -d --build
```

Open `http://<server-ip>:5000` and log in with the admin credentials from `.env`.
Full walkthrough, client setup, user management, and backups:
**[docker_compose_installation/README.md](docker_compose_installation/README.md)**.

## Images

- **Base**: [ghcr.io/mlflow/mlflow](https://github.com/mlflow/mlflow/pkgs/container/mlflow)
- **Custom** (this repo's `Dockerfile`, adds `psycopg2` + `boto3`):
  [jahangir842/mlflow-with-psycopg2](https://hub.docker.com/repository/docker/jahangir842/mlflow-with-psycopg2/general)

## Security

- All credentials live in `.env` / Kubernetes `Secret` (git-ignored) — never in
  the repo.
- MLflow basic-auth is enabled by default in the Compose stack. For internet
  exposure, add a TLS reverse proxy — see
  [linux_installation/authentication_for_mlflow.md](linux_installation/authentication_for_mlflow.md).
- If you previously used the committed default password, rotate it now.
