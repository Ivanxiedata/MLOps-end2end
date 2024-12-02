from typing import Dict
from kfp import dsl
import pytest

# override this to ensure any unit tests generate local files
dsl.get_uri = lambda suffix: "/tmp/" + suffix


@pytest.fixture
def generated_artifact():
    return dsl.Artifact(uri="./tests/day_1/artifacts/generated_artifact.txt")


@pytest.fixture
def updated_artifact():
    return dsl.Artifact(uri="./tests/day_1/artifacts/updated_artifact.txt")


@pytest.fixture
def iris_train_set():
    return dsl.Dataset(uri="./tests/day_2/artifacts/train_set.parquet")


@pytest.fixture
def iris_test_set():
    return dsl.Dataset(uri="./tests/day_2/artifacts/test_set.parquet")


@pytest.fixture
def iris_model():
    return dsl.Model(uri="./tests/day_2/artifacts/model.joblib")
