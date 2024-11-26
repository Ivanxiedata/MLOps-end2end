from day_1.components import file_updater
from kfp import dsl

def test_file_updater(generated_artifact):
    output: dsl.Artifact = file_updater.python_func(
        artifact=generated_artifact
    )
    assert isinstance(output, dsl.Artifact)
    # assert file from component invocation has one line of data within
    assert 2 == sum(1 for _ in open(output.path))