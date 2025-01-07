from datetime import datetime
from google.cloud import aiplatform
from kfp import dsl
from kfp import compiler
from day_2.components import fetch_dataset, train, evaluate_model, mlflow_run
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
def pipeline(
    source: str,  # "local" or "bigquery"
    dataset_zip_path: str = None,  # Path to the Kaggle ZIP file (for "local")
    extracted_path: str = None,    # Path to extract the ZIP file (for "local")
    csv_file_name: str = None,     # Name of the CSV file (for "local")
    bigquery_query: str = None,    # SQL query (for "bigquery")
    test_ratio: float = 0.25,      # Train-test_connection split ratio
):
    # Fetch Dataset Task
    fetch_dataset_task = (
        fetch_dataset(
            source=source,
            dataset_zip_path=dataset_zip_path,
            extracted_path=extracted_path,
            csv_file_name=csv_file_name,
            bigquery_query=bigquery_query,
            test_ratio=test_ratio,
        )
        .set_display_name("Fetch Dataset")
        .set_cpu_limit(CPU_LIMIT)
        .set_memory_limit(MEMORY_LIMIT)
    )

    # Train Model Task
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
            target_label="species",
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
            target_label="species",
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

    # Log Results to MLflow Task
    mlflow_task = (
        mlflow_run(
            model=train_task.output,
            experiment_id="mlops_training_pipeline",
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
