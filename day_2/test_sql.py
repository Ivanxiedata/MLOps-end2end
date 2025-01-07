import mlflow

# Set tracking URI to the same backend store URI
backend_store_uri = "postgresql://mlops-end2end-sql:57913Asd%40@34.135.189.108:5432/mlflow-db"
mlflow.set_tracking_uri(backend_store_uri)

try:
    # Attempt to list experiments (which confirms the connection)
    experiments = mlflow.search_experiments()
    print("MLflow connection successful!")
    print("Experiments:", experiments)

    # Start an experiment and log parameters and metrics
    mlflow.set_experiment("test_experiment")
    with mlflow.start_run():
        mlflow.log_param("learning_rate", 0.01)
        mlflow.log_param("batch_size", 32)
        mlflow.log_metric("accuracy", 0.95)
        print(f"Run ID: {mlflow.active_run().info.run_id}")

        # Optional: Log a simple artifact
        with open("example_artifact.txt", "w") as f:
            f.write("This is a test_connection artifact.")
        mlflow.log_artifact("example_artifact.txt")
except Exception as e:
    print(f"MLflow connection failed: {e}")


