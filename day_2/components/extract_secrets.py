
#list out all the secrets
#gcloud secrets list --project=mlops-end-to-end-443901

#access a secret
#gcloud secrets versions access latest --secret="your-secret-id" --project="your-project-id"

#delete a secret
# gcloud secrets delete 'mlflow-db-password' --project='mlops-end-to-end-443901'

#create a secret
# gcloud secrets create 'mlflow-db-password' --replication-policy='automatic' --project='mlops-end-to-end-443901'
# echo -n "secret_value" | gcloud secrets versions add 'mlflow-db-password' --data-file=- --project='mlops-end-to-end-443901'

from typing import NamedTuple
from kfp import dsl

@dsl.component(
    base_image="python:3.10-slim",
    packages_to_install=[
        "loguru",
        "protobuf==4.23.3",
        "google-cloud-secret-manager",
    ],
)
def extract_secrets(project_id: str) -> NamedTuple('outputs', [('mlflow_uri', str)]):
    """
    Extract secrets from Google Cloud Secret Manager and construct a backend_store_uri.

    Args:
        project_id (str): Google Cloud Project ID.

    Returns:
        NamedTuple: Contains the constructed backend_store_uri for MLflow.
    """
    import loguru
    from google.cloud import secretmanager
    logger = loguru.logger
    client = secretmanager.SecretManagerServiceClient()

    def access_secret(secret_name: str) -> str:
        """Access a secret from Secret Manager."""
        secret_version = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        response = client.access_secret_version(name=secret_version)
        return response.payload.data.decode("UTF-8")

    # Retrieve secrets
    encoded_password = access_secret("mlflow-db-password")
    db_host = access_secret("db-public-ip")
    db_port = access_secret("db_port")
    db_name = access_secret("db_name")
    db_user = access_secret("db_user")

    # Construct the backend store URI
    mlflow_uri = f"postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"


    logger.info(f"MLflow backend store URI: {mlflow_uri}")

    #Return outputs
    outputs =  NamedTuple('outputs', [('mlflow_uri', str)])
    return outputs(mlflow_uri)

