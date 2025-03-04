## Testing MLflow Docker Image Locally

### 1. Create Docker Compose File

Create a `docker-compose.yml` file:

```yaml
version: '3'
services:
  postgres:
    image: postgres:14
    environment:
      - POSTGRES_USER=mlflowuser
      - POSTGRES_PASSWORD=mlflowpass
      - POSTGRES_DB=mlflowdb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  mlflow:
    image: mlflow-with-psycopg2:v2.20.3  # Your custom image
    depends_on:
      - postgres
    ports:
      - "5000:5000"
    environment:
      - POSTGRES_USER=mlflowuser
      - POSTGRES_PASSWORD=mlflowpass
      - POSTGRES_DB=mlflowdb
    command: >
      mlflow server 
      --host 0.0.0.0 
      --port 5000 
      --backend-store-uri postgresql://mlflowuser:mlflowpass@postgres:5432/mlflowdb 
      --default-artifact-root file:///mlflow/artifacts
    volumes:
      - mlflow_artifacts:/mlflow/artifacts

volumes:
  postgres_data:
  mlflow_artifacts:
```

### 2. Start the Services

```bash
# Create a directory for testing
mkdir mlflow-test && cd mlflow-test

# Save the docker-compose.yml file here

# Start the services
docker-compose up -d

# Check the logs
docker-compose logs -f
```

### 3. Verify the Setup

1. Check if MLflow UI is accessible:
   - Open http://localhost:5000 in your browser

2. Test with Python client:
```python
import mlflow
mlflow.set_tracking_uri("http://localhost:5000")

# Should work without psycopg2 errors
mlflow.create_experiment("test-experiment")
```

### 4. Clean Up

```bash
# Stop the services
docker-compose down

# Remove volumes (optional)
docker-compose down -v
```

### Troubleshooting

1. If MLflow can't connect to PostgreSQL:
   ```bash
   # Check PostgreSQL logs
   docker-compose logs postgres
   
   # Connect to PostgreSQL directly
   docker-compose exec postgres psql -U mlflowuser -d mlflowdb
   ```

2. If MLflow container exits:
   ```bash
   # Check MLflow logs
   docker-compose logs mlflow
   ```

3. To rebuild the image:
   ```bash
   docker-compose build mlflow
   ```
