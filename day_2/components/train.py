from typing import Dict
from kfp import dsl


@dsl.component(
    base_image="python:3.10-slim",
    packages_to_install=[
        "xgboost",
        "pandas",
        "scikit-learn",
        "pyarrow",
        "loguru"
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
    from sklearn.preprocessing import LabelEncoder
    import loguru

    # Set up logging
    logger = loguru.logger

    # Load training data
    df_train = pd.read_parquet(train_set.path)

    # Encode target column
    label_encoder = LabelEncoder()
    df_train[target_label] = label_encoder.fit_transform(df_train[target_label])


    # Prepare DMatrix
    dmatrix = xgb.DMatrix(
        data=df_train.drop(target_label, axis=1),
        label=df_train[target_label]
    )

    # Train the XGBoost model
    model = xgb.train(
        params={**xgb_parms, **hyperparameters},
        dtrain=dmatrix,
        num_boost_round=num_boost_round,
    )

    # Save model
    model_output = dsl.Model(uri=dsl.get_uri(suffix="model_with_encoder.joblib"))
    logger.info(f"Model will be saved to: {model_output.path}")
    joblib.dump((model, label_encoder), model_output.path)

    return model_output
