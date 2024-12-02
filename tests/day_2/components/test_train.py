from day_2.components.train import train
from kfp import dsl


def test_train(iris_train_set, xgb_parms):
    model = train.python_func(
        train_set=iris_train_set,
        hyperparameters=dict(
            alpha=1,
            colsample_bylevel=0.48916684982960545,
            colsample_bytree=0.3419495606800822,
            gamma=0.06938003793539216,
            learning_rate=0.08389415232327328,
            max_depth=5,
            reg_lambda=1.5137699910649667,
            subsample=0.9936504203234391,
        ),
        target_label="species",
        num_boost_round=100,
        xgb_parms=dict(
            objective="multi:softprob",
            tree_method="auto",
            num_class=3,
        ),
    )
    assert isinstance(model, dsl.Model)
