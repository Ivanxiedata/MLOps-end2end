from google.cloud import secretmanager
# from ..secret_keys.credential import GCP_PROJECT_ID
import mlflow

GCP_PROJECT_ID = "mlops-end-to-end-443901"
def access_secret(secret_name):
    """Access a secret from Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    secret_version = f"projects/{GCP_PROJECT_ID}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(name=secret_version)
    return response.payload.data.decode("UTF-8")

# Retrieve the artifact and database URLs from Secret Manager
mlflow_artifact_url = access_secret("mlflow_artifact_url")
mlflow_database_url = access_secret("mlflow_database_url")

print(mlflow_database_url)

mlflow.get_artifact_uri(mlflow_artifact_url)
mlflow.set_tracking_uri(mlflow_database_url)



#
# from google.cloud import storage
#
# def get_gcp_project_id():
#     client = storage.Client()
#     return client.project
#
# GCP_PROJECT_ID = get_gcp_project_id()
# print(GCP_PROJECT_ID)