from kfp import dsl
import pytest

# override this to ensure any unit tests generate local files
dsl.get_uri = lambda suffix: '/tmp/'+suffix

@pytest.fixture
def generated_artifact():
    return dsl.Artifact(uri="./tests/day_1/artifacts/generated_artifact.txt")

@pytest.fixture
def updated_artifact():
    return dsl.Artifact(uri="./tests/day_1/artifacts/updated_artifact.txt")
