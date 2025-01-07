from datetime import datetime
from google.cloud import aiplatform
from kfp import dsl
from kfp import compiler
from loguru import logger
import os
from day_2.components import fetch_dataset, train, evaluate_model, mlflow_run, test_db_connection,extract_secrets
from config import (
    GCP_PROJECT_ID,
    SERVICE_ACCOUNT,
    NETWORK,
    PIPELINE_NAME,
    PIPELINE_ROOT,
    CPU_LIMIT,
    MEMORY_LIMIT,
)

@dsl.pipeline(name="mlops_training_pipeline")
def pipeline():
    # Fetch Dataset Task
    fetch_dataset_task = (
        fetch_dataset(
            source='bigquery',
            csv_file_name='',  # Full path to the CSV file
            test_ratio=0.25,
            extracted_path= '',
            bigquery_query= "SELECT * FROM `mlops-end-to-end-443901.iris_1.test1` LIMIT 1000"

        )
        .set_display_name("Fetch Dataset")
        .set_cpu_limit(CPU_LIMIT)
        .set_memory_limit(MEMORY_LIMIT)
    )

    # # Train Model Task
    train_task = (
        train(
            train_set=fetch_dataset_task.outputs["train_set"],
            hyperparameters=dict(
                alpha=1,
                colsample_bylevel=0.48916684982960545,
                colsample_bytree=0.3419495606800822,
                gamma=0.06938003793539216,
                learning_rate=0.08389415232327328,
                max_depth=5,
                reg_lambda=1.5137699910649667,
                subsample=0.9936504203234391,
            ),
            target_label="Species",
            num_boost_round=100,
            xgb_parms=dict(
                objective="multi:softprob",
                tree_method="auto",
                num_class=3,
            ),
        )
        .set_display_name("Train Model")
        .set_cpu_limit(CPU_LIMIT)
        .set_memory_limit(MEMORY_LIMIT)
    )


    # Evaluate Model Task
    evaluate_model_task = (
        evaluate_model(
            test_set=fetch_dataset_task.outputs["test_set"],
            model=train_task.output,
            target_label="Species",
            xgb_parms=dict(
                objective="multi:softprob",
                tree_method="auto",
                num_class=3,
            ),
        )
        .set_display_name("Evaluate Model")
        .set_cpu_limit(CPU_LIMIT)
        .set_memory_limit(MEMORY_LIMIT)
    )

    secret_manager_task = (
        extract_secrets(
            project_id=GCP_PROJECT_ID
        )
        .set_display_name("Extract Secrets")
        .set_cpu_limit(CPU_LIMIT)
        .set_memory_limit(MEMORY_LIMIT)

    )

    # # Log Results to MLflow Task
    mlflow_task = (
        mlflow_run(
            backend_store_uri=secret_manager_task.outputs["mlflow_uri"],  # Pass the backend_store_uri
            model=train_task.output,
            experiment_name="mlops_training_pipeline",
            run_id="241204",
            tags={"pipeline": "mlops_training"},
            metrics=evaluate_model_task.outputs["eval_metrics"],
            feature_importance=evaluate_model_task.outputs["feature_importance"],
            hyperparameters=dict(
                alpha=1,
                colsample_bylevel=0.48916684982960545,
                colsample_bytree=0.3419495606800822,
                gamma=0.06938003793539216,
                learning_rate=0.08389415232327328,
                max_depth=5,
                reg_lambda=1.5137699910649667,
                subsample=0.9936504203234391,
            ),
        )
        .set_display_name("Log to MLflow")
        .set_cpu_limit(CPU_LIMIT)
        .set_memory_limit(MEMORY_LIMIT)
    )


if __name__ == "__main__":
    TMP_PIPELINE_JSON = "/tmp/mlops-training-pipeline.json"

    # Compile the pipeline into a JSON DAG specification
    compiler.Compiler().compile(
        pipeline_func=pipeline,
        package_path=TMP_PIPELINE_JSON,
    )

    pipeline_job = aiplatform.PipelineJob(
        display_name="mlops-training-pipeline-"
        + datetime.now().strftime("%Y%m%d%H%M%S"),
        project=GCP_PROJECT_ID,
        template_path=TMP_PIPELINE_JSON,
        enable_caching=True,
    )

    pipeline_job.submit(
        service_account=SERVICE_ACCOUNT,
        network=NETWORK,
    )
