from typing import Dict, NamedTuple
from google.cloud import aiplatform
from kfp import dsl
from kfp import compiler
from day_2.components import fetch_iris_features
from ailabs.automl import PipelineConfig
from ailabs.automl.classification.gradient_boosting import gradient_boosting_pipeline

cfg = PipelineConfig()


@dsl.pipeline(
    pipeline_root=cfg.pipeline_root,
    name=cfg.pipeline_name,
)
def pipeline(
    project_id: str,
    feature_view: str,
    early_stop_rounds: int,
    target_label: str,
    eval_ratio: float,
    max_evals: int,
    test_ratio: float,
    num_boost_round: int,
    num_class: int,
    hyperparameter_space: Dict,
    xgb_parms: Dict,
):

    fetch_iris_features_task = (
        fetch_iris_features(
            project_id=project_id,
            feature_view=feature_view,
            test_ratio=test_ratio,
        )
        .set_display_name("Fetch Features")
        .set_cpu_limit("2")
        .set_memory_limit("2G")
    )

    gradient_boosting_pipeline_task = gradient_boosting_pipeline(
        train_set=fetch_iris_features_task.outputs["train_set"],
        test_set=fetch_iris_features_task.outputs["test_set"],
        target_label=target_label,
        # num_class=num_class,
        num_boost_round=num_boost_round,
        early_stop_rounds=early_stop_rounds,
        eval_ratio=eval_ratio,
        max_evals=max_evals,
        xgb_parms=xgb_parms,
        hyperparameter_space=hyperparameter_space,
    )


if __name__ == "__main__":

    arguments = dict(
        project_id=cfg.settings["PROJECT_ID"],
        feature_view="sams_iris_demo_v1",
        target_label="species",
        num_class=3,
        test_ratio=0.25,
        eval_ratio=0.2,
        num_boost_round=100,
        early_stop_rounds=3,
        max_evals=10,
        hyperparameter_space=dict(
            colsample_bytree=[0.1, 1.0],
            learning_rate=[0.001, 0.5],
            max_depth=[5, 50, 1],
            alpha=[0, 20, 1],
            gamma=[0, 0.5],
            subsample=[0.1, 1.0],
            colsample_bylevel=[0.1, 1.0],
            reg_lambda=[0, 2.0],
        ),
        xgb_parms=dict(
            objective="multi:softprob",
            num_class=3,
            tree_method="auto",
        ),
    )

    TMP_PIPELINE_JSON = "/tmp/persona-pipeline.json"

    compiler.Compiler().compile(
        pipeline_func=pipeline,
        pipeline_parameters=arguments,
        package_path=TMP_PIPELINE_JSON,
    )

    pipeline_job = aiplatform.PipelineJob(
        display_name=cfg.job_name,
        template_path=TMP_PIPELINE_JSON,
        parameter_values=arguments,
        enable_caching=True,
        project=cfg.project_id,
    )

    pipeline_job.submit(service_account=cfg.service_account, network=cfg.network)
