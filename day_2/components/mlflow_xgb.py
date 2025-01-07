from datetime import datetime
from google.cloud import aiplatform
from kfp import dsl
from kfp import compiler
from loguru import logger
from typing import Dict
import os
from day_2.components import fetch_dataset, train, evaluate_model
from config import (
    GCP_PROJECT_ID,
    SERVICE_ACCOUNT,
    NETWORK,
    PIPELINE_NAME,
    PIPELINE_ROOT,
    CPU_LIMIT,
    MEMORY_LIMIT,
)

@dsl.component(
    base_image="python:3.10-slim",
    packages_to_install=[
        'mlflow==1.27.0',
        "loguru",
        "protobuf==4.23.3",
        'psycopg2-binary',
        'xgboost'
    ],
)
def mlflow_run(
    backend_store_uri: str,
    model: dsl.Model,
    experiment_name: str,
    run_id: str,
    tags: dict,
    metrics: dsl.Metrics,
    hyperparameters: Dict[str, float],
    feature_importance: dsl.Metrics
) -> None:
    import mlflow
    from loguru import logger
    import psycopg2
    import joblib
    import xgboost


    # Set tracking URI

    mlflow.set_tracking_uri(backend_store_uri)
    experiment_id = mlflow.get_experiment_by_name(experiment_name)
    if experiment_id is None:
        experiment_id = mlflow.create_experiment(name=experiment_name)
    else:
        experiment_id = mlflow.set_experiment(experiment_name).experiment_id

    try:


        with mlflow.start_run(
            run_name=run_id,
            experiment_id=experiment_id,
        ):

            # load the model
            loaded_model = joblib.load(model.path)
            logger.info('successfully loaded model')
            mlflow.xgboost.log_model(
                xgb_model=loaded_model,
                artifact_path="model"
            )

            # Log tags
            if tags:
                logger.info('tag found')
                mlflow.set_tags(tags)

            # Log hyperparameters
            if hyperparameters:
                logger.info('hyperparameters found')
                mlflow.log_params(hyperparameters)

            # Log metrics
            if metrics:
                logger.info('metrics found')
                for key, value in metrics.get().items():
                    mlflow.log_metric(key, value)


            # Log feature importance
            # if feature_importance:
            #     logger.info(f"Logging feature importance: {feature_importance}")
            #
            #     # Log feature importance
            #     if feature_importance:
            #         logger.info('feature importance found')
            #         # Convert feature importance to a Pandas DataFrame
            #         feature_importance_df = pd.DataFrame.from_dict(
            #             feature_importance.get(), orient="index", columns=["importance"]
            #         )
            #         # Save to CSV and log as an artifact
            #         feature_importance_path = "/tmp/feature_importance.csv"
            #         feature_importance_df.to_csv(feature_importance_path)
            #         mlflow.log_artifact(feature_importance_path)



    except Exception as e:
        logger.error(f"MLflow connection or logging failed: {e}")
        raise