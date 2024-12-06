from typing import Dict, NamedTuple
from google.cloud import aiplatform
from kfp import dsl
from kfp import compiler
from day_2.components import fetch_iris_features
from ailabs.automl import PipelineConfig
from ailabs.automl.classification.gradient_boosting import gradient_boosting_pipeline

cfg = PipelineConfig()

project_id=cfg.settings["PROJECT_ID"]
print(project_id)