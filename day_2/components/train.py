from typing import Dict
from kfp import dsl

@dsl.component(
    base_image="python:3.10-slim",
    packages_to_install=[
        'xgboost',
        'pandas',
        'scikit-learn',
        'pyarrow',
    ],
)
def train(
    train_set: dsl.Dataset,
    hyperparameters: dict,
    target_label: str,
    num_boost_round: int,
    xgb_parms: Dict,
) -> dsl.Model:
    import pandas as pd
    import joblib
    import xgboost as xgb

    df_train = pd.read_parquet(train_set.path)
    dmatrix = xgb.DMatrix(
        data=df_train.drop(target_label, axis=1), 
        label=df_train[target_label]
    )

    model = xgb.train(
        params={**xgb_parms, **hyperparameters},
        dtrain=dmatrix,
        num_boost_round=num_boost_round,
    )

    # Save model
    model_output = dsl.Model(uri=dsl.get_uri(suffix='model.joblib'))
    joblib.dump(model, model_output.path)

    return model_output