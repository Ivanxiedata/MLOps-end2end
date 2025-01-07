import day_1.hello_world_pipeline
from kfp import compiler
import pytest
import day_1

pipelines = [
        day_1.hello_world_pipeline.pipeline,
    ]

@pytest.mark.parametrize("pipeline", pipelines)
def test_pipeline_compilable(pipeline):

    compiler.Compiler().compile(
        pipeline_func=pipeline,
        package_path='/tmp/test_connection-pipeline-compilable.json'
    )

