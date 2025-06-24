# MLflow with PostgreSQL 

This project is about set up MLflow with PostgreSQL backend 
---

**Official MLflow with Docker**: https://github.com/mlflow/mlflow/pkgs/container/mlflow

**Customised Mlflow Image with Postgres Capability:** https://hub.docker.com/repository/docker/jahangir842/mlflow-with-psycopg2/general

---

## Prerequisites

- Docker installed ([Docker Installation Guide](https://docs.docker.com/get-docker/))
- Docker Compose installed ([Docker Compose Installation Guide](https://docs.docker.com/compose/install/))

## Installation Steps

### 1. Build the Custom MLflow Image

```bash
# Clone this repository (if you haven't already)
git clone git@github.com:jahangir842/mlflow.git
cd mlflow

# Build the custom MLflow image
docker build -t mlflow-with-psycopg2:v2.20.3 -f Dockerfile .
```

---
