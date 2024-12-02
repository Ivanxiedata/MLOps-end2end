from kfp import dsl
from typing import Dict, NamedTuple


@dsl.component(
    base_image="python:3.10-slim",
    packages_to_install=[
        "xgboost",
        "pandas",
        "scikit-learn",
        "pyarrow",
    ],
)
def evaluate_model(
    test_set: dsl.Dataset,
    model: dsl.Model,
    target_label: str,
    xgb_parms: Dict,
) -> NamedTuple("outputs", eval_metrics=dsl.Metrics, feature_importance=dsl.Metrics):  # type: ignore
    import xgboost as xgb
    import pandas as pd
    import joblib
    from collections.abc import Mapping
    from sklearn.metrics import (
        classification_report,
    )

    # Load test dataset
    df_test = pd.read_parquet(test_set.path)
    df_x = df_test.drop(target_label, axis=1)
    df_y = df_test[target_label]
    d_test = xgb.DMatrix(data=df_x, label=df_y)

    # Make predictions on the test data
    # this prediction reshaping is specific to multinomial classification
    model: xgb.Booster = joblib.load(model.path)
    y_pred = model.predict(d_test).reshape(-1, xgb_parms["num_class"]).argmax(axis=1)
    if df_test.shape[0] != len(y_pred):
        raise ValueError(
            f"{df_test[0].shape} records were used for evaluation, but {len(y_pred)} predictions were generated. Ensure that num_class accurately reflects the number of classifications you wish to predict with."
        )

    # gather standard classification metrics
    eval_metrics = dsl.Metrics()
    report = classification_report(df_y, y_pred, output_dict=True)

    def flatten_metrics(nested_dict: dict, prefix="") -> dict:
        for k, v in nested_dict.items():
            suffix = k.replace(".0", "")  # fixes formatting of class-level metrics
            label = f"{prefix}_{str(suffix)}" if prefix != "" else str(suffix)
            if isinstance(v, Mapping):
                flatten_metrics(v, label)
            else:
                eval_metrics.log_metric(label.replace(" ", "_").replace("-", "_"), v)

    flatten_metrics(report)

    # gather feature importance metrics
    feature_importance = dsl.Metrics()
    fi_dict = model.get_score(importance_type="gain")
    for k in sorted(fi_dict, key=fi_dict.get, reverse=True):
        feature_importance.log_metric(k, fi_dict[k])

    outputs = NamedTuple(
        "outputs", eval_metrics=dsl.Metrics, feature_importance=dsl.Metrics
    )
    return outputs(eval_metrics, feature_importance)
