from typing import NamedTuple
from kfp import dsl

@dsl.component(
    base_image="python:3.10-slim",
    packages_to_install=[
        "pandas==2.2.3",
        "scikit-learn==1.5.1",
        "google-cloud-bigquery==3.10.0",
        "zipfile36==0.1.3",
        "loguru==0.7.3",
        "db-dtypes==1.1.0",
    ],
)
def fetch_dataset(
        source: str,  # "local" or "bigquery"
        csv_file_name: str,  # Name of the CSV file inside the ZIP (for "local" source)
        test_ratio: float = 0.25,
        extracted_path: str = None,
        bigquery_query: str = None,
) -> NamedTuple("outputs", [("train_set", dsl.Dataset), ("test_set", dsl.Dataset)]):
    import pandas as pd
    from sklearn.model_selection import train_test_split
    import os
    from google.cloud import bigquery
    from loguru import logger


    # Helper function: Load dataset from local files
    def load_local_dataset(extract_path, csv_name) -> pd.DataFrame:
        if not os.path.exists(extract_path):
            print('Path does not exist.')

        csv_path = os.path.join(extract_path, csv_name)
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV file {csv_name} not found in {extract_path}.")

        return pd.read_csv(csv_path)

    # Helper function: Load dataset from BigQuery
    def load_bigquery_dataset(query: str) -> pd.DataFrame:
        client = bigquery.Client(project="mlops-end-to-end-443901")
        query_job = client.query(query)
        return query_job.to_dataframe()

    # Load dataset based on the source
    if source == "local":
        logger.info(f"Loading dataset from local files... {csv_file_name}")
        if not (extracted_path and csv_file_name):
            raise ValueError(
                "For 'local' source, provide 'dataset_zip_path', 'extracted_path', and 'csv_file_name'."
            )
        data = load_local_dataset(extracted_path, csv_file_name)
    elif source == "bigquery":
        if not bigquery_query:
            raise ValueError("For 'bigquery' source, provide 'bigquery_query'.")
        data = load_bigquery_dataset(bigquery_query)
    else:
        raise ValueError("Invalid source. Choose either 'local' or 'bigquery'.")

    # Log dataset information
    print(f"Loaded dataset shape: {data.shape}")
    print(f"Columns: {data.columns}")

    # Perform any necessary preprocessing (update according to your specific data)
    data = data.dropna()  # Example: Drop missing values

    # Split into training and testing datasets
    train_df, test_df = train_test_split(
        data, test_size=test_ratio, random_state=1128
    )

    print(f"Training dataset shape: {train_df.shape}")
    print(f"Test dataset shape: {test_df.shape}")

    # Save the training and test_connection datasets
    train_set = dsl.Dataset(uri=dsl.get_uri(suffix="train_set.parquet"))
    train_df.to_parquet(train_set.path, index=False)

    test_set = dsl.Dataset(uri=dsl.get_uri(suffix="test_set.parquet"))
    test_df.to_parquet(test_set.path, index=False)

    # Return outputs
    outputs = NamedTuple("outputs", [("train_set", dsl.Dataset), ("test_set", dsl.Dataset)])
    return outputs(train_set, test_set)
