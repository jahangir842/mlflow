# Self-Hosted MLflow for Teams

A centralized [MLflow](https://mlflow.org/) tracking server so your team can log
experiments, register models, and share artifacts from any machine — backed by
**PostgreSQL** (metadata) and **MinIO / S3** (artifacts), with **authentication**.

## What do you want to do?

- **Use MLflow** (log runs from your code) → **[Developers Guide](developers-guide.md)**
- **Deploy the server** (set it up) → **[Installation](installation/README.md)**

## Deploy in 4 commands (Docker Compose)

```bash
git clone https://github.com/jahangir842/mlflow.git
cd mlflow/installation/docker_compose_installation
cp .env.example .env          # edit and change every password
docker compose up -d --build
```

Then open `http://<server-ip>` (port 80 — no `:5000`). See
[installation/](installation/README.md) for other methods (Kubernetes, systemd,
Ansible) and the full walkthrough.
