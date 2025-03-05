# MLflow with PostgreSQL Installation Guide

This guide helps you set up MLflow with PostgreSQL backend using Docker Compose.

## Prerequisites

- Docker installed ([Docker Installation Guide](https://docs.docker.com/get-docker/))
- Docker Compose installed ([Docker Compose Installation Guide](https://docs.docker.com/compose/install/))

## Installation Steps

### 1. Build the Custom MLflow Image

```bash
# Clone this repository (if you haven't already)
git clone <your-repository-url>
cd docker_compose_installation

# Build the custom MLflow image
docker build -t mlflow-with-psycopg2:v2.20.3 -f ../Dockerfile ..
```

### 2. Start the Services

```bash
# Start PostgreSQL and MLflow
docker-compose up -d

# Check if containers are running
docker-compose ps
```

### 3. Verify Installation

1. Access MLflow UI:
   - Open your browser and go to: http://localhost:5000
   - You should see the MLflow interface

2. Test with Python:
```python
import mlflow

# Set the tracking URI
mlflow.set_tracking_uri("http://localhost:5000")

# Start a new run
with mlflow.start_run():
    # Log a parameter
    mlflow.log_param("test_param", 1)
    # Log a metric
    mlflow.log_metric("test_metric", 100)
```

## Configuration

Default credentials (can be changed in docker-compose.yml):
- PostgreSQL User: admin
- PostgreSQL Password: pakistan
- Database Name: mlflowdb
- MLflow URL: http://localhost:5000
- PostgreSQL Port: 5432

## Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop and remove everything (including volumes)
docker-compose down -v
```

## Troubleshooting

1. If PostgreSQL port 5432 is already in use:
   - Change the port mapping in docker-compose.yml from "5432:5432" to "5433:5432"

2. If MLflow container fails to start:
   ```bash
   # Check MLflow logs
   docker-compose logs mlflow
   ```

3. If PostgreSQL connection fails:
   ```bash
   # Check PostgreSQL logs
   docker-compose logs postgres
   ```

## Data Persistence

- PostgreSQL data is stored in the `postgres_data` volume
- MLflow artifacts are stored in the `mlflow_artifacts` volume

These volumes persist even after containers are stopped. To remove them, use:
```bash
docker-compose down -v
```

## Security Note

The default credentials in this setup are for demonstration purposes. For production:
1. Change the default passwords
2. Use environment variables or Docker secrets
3. Enable SSL/TLS
4. Configure proper network security

## Additional Resources

- [MLflow Documentation](https://www.mlflow.org/docs/latest/index.html)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
