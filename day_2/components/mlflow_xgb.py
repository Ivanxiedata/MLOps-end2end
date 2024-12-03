from typing import Dict
from kfp import dsl


@dsl.component(
    base_image="python:3.10-slim",
    packages_to_install=[
        'samsclub-datascienceservices-element-mlflow-plugins==0.0.1',
        'mlflow==1.27.0',
        'google-cloud-secret-manager',
        'joblib',
        'xgboost',
        'protobuf==4.23.3'
    ],
    pip_index_urls=[
        'https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/datascienceservices-pypi/simple',
    ]
)
def mlflow_run(
    model: dsl.Model,
    experiment_id: str,
    run_id: str,
    tags: dict,
    metrics: dsl.Metrics,               # Accept eval_metrics as dsl.Metrics
    hyperparameters: dict,
    feature_importance: dsl.Metrics    # Accept feature_importance as dsl.Metrics
) -> None:
    import mlflow
    import joblib
    import pandas as pd
    import logging

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)

    try:
        with mlflow.start_run(
            run_name=run_id,
            experiment_name=experiment_id
        ):
            # Load and log the model
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


            # Log metrics
            if metrics:
                logger.info('metrics found')
                for key, value in metrics.get().items():
                    mlflow.log_metric(key, value)

            # Log hyperparameters
            if hyperparameters:
                logger.info('hyperparameters found')
                mlflow.log_params(hyperparameters)

            # Log feature importance
            if feature_importance:
                logger.info('feature importance found')
                # Convert feature importance to a Pandas DataFrame
                feature_importance_df = pd.DataFrame.from_dict(
                    feature_importance.get(), orient="index", columns=["importance"]
                )
                # Save to CSV and log as an artifact
                feature_importance_path = "/tmp/feature_importance.csv"
                feature_importance_df.to_csv(feature_importance_path)
                mlflow.log_artifact(feature_importance_path)

    except Exception as e:  # Fix typo "Execption"
        logger.error(f"Failed to log to MLflow: {e}")

    logger.info("MLflow run completed successfully.")