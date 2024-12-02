from day_2.components.evaluate import evaluate_model
from kfp import dsl


def test_evaluate_model(iris_test_set, iris_model):
    metrics = evaluate_model.python_func(
        test_set=iris_test_set,
        model=iris_model,
        target_label="species",
        xgb_parms=dict(
            objective="multi:softprob",
            tree_method="auto",
            num_class=3,
        ),
    )
    assert isinstance(metrics.eval_metrics, dsl.Metrics)
    assert isinstance(metrics.feature_importance, dsl.Metrics)
