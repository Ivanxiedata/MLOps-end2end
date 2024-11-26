from day_1.components import file_generator
from kfp import dsl

def test_file_generator():
    output: dsl.Artifact = file_generator.python_func()
    assert isinstance(output, dsl.Artifact)
    # assert file from component invocation has one line of data within
    assert 1 == sum(1 for _ in open(output.path))