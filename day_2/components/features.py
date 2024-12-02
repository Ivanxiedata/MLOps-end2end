from typing import NamedTuple
from kfp import dsl


@dsl.component(
    base_image="python:3.10-slim",
    packages_to_install=[
        "walmart-mlplatforms-wmfs == 0.0.28",
        "google-cloud-secret-manager == 2.16.1",
        "dask[dataframe] == 2024.2.1",
        "scikit-learn == 1.5.1",
    ],
    pip_index_urls=[
        "https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/pythonhosted-pypi-release-remote/simple",
        "https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/mlplatforms-pypi/simple",
    ],
)
def fetch_iris_features(
    project_id: str,
    feature_view: str,
    test_ratio: float = 0.25,
) -> NamedTuple("outputs", train_set=dsl.Dataset, test_set=dsl.Dataset):  # type: ignore
    import logging
    import os
    import time

    from google.cloud import secretmanager
    from wmfs.feature_mart import FeatureMart
    from sklearn.model_selection import train_test_split

    # Set this to False to disable telemetry to usage.feast.dev
    os.environ["FEAST_USAGE"] = "False"

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)

    os.environ["GCP_PROJECT_ID"] = project_id

    def access_secret_version(secret_id):
        project_id = os.environ["GCP_PROJECT_ID"]

        client = secretmanager.SecretManagerServiceClient()
        secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"

        response = client.access_secret_version(request={"name": secret_name})
        secret_string = response.payload.data.decode("UTF-8")

        return secret_string

    os.environ["FEATURESTORE_API_ENV"] = access_secret_version("FEATURESTORE_API_ENV")
    os.environ["FEATURESTORE_API_KEY"] = access_secret_version("FEATURESTORE_API_KEY")
    os.environ["FEATURESTORE_API_SECRET"] = access_secret_version(
        "FEATURESTORE_API_SECRET"
    )
    logger.info("Fetched Feature Store credentials")

    logger.info("Get Feature Store client")
    store = FeatureMart(fs_name="fs_bq_bt", namespace="sams")

    logger.info(f"Retrieving feature view {feature_view}")
    subcat_vw = store.get_feature_view(feature_view)

    logger.info(f"Available features are {subcat_vw.features}")

    feature_names = []
    selected_features = [
        f.name for f in subcat_vw.features
    ]  # ["sepal_length", "sepal_width", "petal_length", petal_width]
    for feature in selected_features:
        feature_names.append(f"{feature_view}:{feature}")

    logger.info(f"Feature names to pull are {feature_names}")

    # Access the data source of the feature view
    data_source = subcat_vw.batch_source
    logger.info(f"The data source of the feature view is {data_source.name}")

    # Get the table name or BigQuery SQL string
    table_name_or_sql = data_source.get_table_query_string()
    logger.info(f"The table name or sql string is {table_name_or_sql}")

    # Retrieve features
    entity_sql = f"""
        SELECT
            membership_id,
            MAX(event_timestamp) AS event_timestamp,
        FROM {table_name_or_sql}
        WHERE DATE(event_timestamp) BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH) AND CURRENT_DATE()
        GROUP BY membership_id
    """

    logger.info("Fetching features from feature store")

    t = time.time()
    features = store.get_historical_features(
        entity_df=entity_sql,
        features=feature_names,
    ).to_df(timeout=10000)
    logger.info(f"Fetching features took {time.time() - t} seconds")
    features = features.drop(["membership_id", "event_timestamp"], axis=1)

    # map species to integers for label encoding
    label_mapping = {"setosa": 0, "virginica": 1, "versicolor": 2}
    features["species"] = features["species"].map(label_mapping)

    logger.info(f"Succesfully fetched all features with size {features.shape}")
    logger.info(f"Fetched columns are {features.columns}")

    train_df, test_df = train_test_split(
        features, test_size=test_ratio, random_state=1128
    )
    logger.info(f"training dataset shape {train_df.shape}")
    logger.info(f"test dataset shape {test_df.shape}")

    train_set = dsl.Dataset(uri=dsl.get_uri(suffix="train_set.parquet"))
    train_df.to_parquet(train_set.path, index=False)

    test_set = dsl.Dataset(uri=dsl.get_uri("test_set.parquet"))
    test_df.to_parquet(test_set.path, index=False)

    outputs = NamedTuple("outputs", train_set=dsl.Dataset, test_set=dsl.Dataset)
    return outputs(train_set, test_set)
