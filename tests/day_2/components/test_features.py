from day_2.components.features import fetch_iris_features
from kfp import dsl

def test_fetch_iris_features():
    data = fetch_iris_features.python_func(
        project_id = 'dev-sams-ds-train',
        feature_view = 'sams_iris_demo_v1',
        test_ratio = 0.25,
    )
    assert isinstance(data.train_set, dsl.Dataset)
    assert isinstance(data.test_set, dsl.Dataset)
