from datetime import datetime
from typing import Dict
from google.cloud import aiplatform
from kfp import dsl
from kfp import compiler
from day_2.components import fetch_iris_features, train, evaluate_model, mlflow_run
from day_2.components.config import (
    GCP_PROJECT,
    SERVICE_ACCOUNT,
    NETWORK,
    PIPELINE_NAME,
    PIPELINE_ROOT,
    CPU_LIMIT,
    MEMORY_LIMIT)


@dsl.pipeline(name="iris training pipeline")
def pipeline():

    fetch_iris_features_task = (
        fetch_iris_features(
            project_id= GCP_PROJECT,
            feature_view="sams_iris_demo_v1",
            test_ratio=0.25,
        )
        .set_display_name("Fetch Features")
        .set_cpu_limit(CPU_LIMIT)
        .set_memory_limit(MEMORY_LIMIT)
    )

    train_task = (
        train(
            train_set=fetch_iris_features_task.outputs["train_set"],
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

    evaluate_model_task = (
        evaluate_model(
            test_set=fetch_iris_features_task.outputs["test_set"],
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

    mlflow_task = (
        mlflow_run(
            model=train_task.output,  # Use the "model" output from the train task
            experiment_id="iris_training_mlops",  # Replace with actual experiment ID or pipeline input
            run_id="241204",  # Replace with actual run ID or pipeline input
            tags={"pipeline": "iris_training"},  # Example tag
            metrics=evaluate_model_task.outputs["eval_metrics"],  # Use "eval_metrics" from evaluate_model task
            feature_importance=evaluate_model_task.outputs["feature_importance"],
            # Use "feature_importance" from evaluate_model task
            hyperparameters=dict(  # Same hyperparameters as the train task
                alpha=1,
                colsample_bylevel=0.48916684982960545,
                colsample_bytree=0.3419495606800822,
                gamma=0.06938003793539216,
                learning_rate=0.08389415232327328,
                max_depth=5,
                reg_lambda=1.5137699910649667,
                subsample=0.9936504203234391,
            )
        )
        .set_display_name("Log to MLflow")
        .set_cpu_limit(CPU_LIMIT)
        .set_memory_limit(MEMORY_LIMIT)
    )


if __name__ == "__main__":

    TMP_PIPELINE_JSON = "/tmp/iris-training-pipeline.json"

    # Compile the pipeline into a json DAG specification
    compiler.Compiler().compile(
        pipeline_func=pipeline,
        package_path=TMP_PIPELINE_JSON,
    )

    pipeline_job = aiplatform.PipelineJob(
        display_name="iris-training-pipeline-"
        + datetime.now().strftime("%Y%m%d%H%M%S"),
        project=GCP_PROJECT,
        template_path=TMP_PIPELINE_JSON,
        enable_caching=True,
    )

    pipeline_job.submit(
        service_account=SERVICE_ACCOUNT,
        network=NETWORK,
    )
