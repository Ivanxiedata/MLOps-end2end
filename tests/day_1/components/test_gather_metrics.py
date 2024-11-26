from day_1.components import gather_metrics
from kfp import dsl

def test_gather_metrics(updated_artifact):
    output: dsl.Metrics = gather_metrics.python_func(
        artifact=updated_artifact
    )
    assert isinstance(output, dsl.Metrics)
    
    assert output.metadata['file_length'] == 2