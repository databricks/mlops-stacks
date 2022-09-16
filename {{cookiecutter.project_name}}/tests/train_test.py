from steps.train import estimator_fn
from sklearn.utils.estimator_checks import check_estimator


def test_train_fn_returns_object_with_correct_spec():
    regressor = estimator_fn()
    assert callable(getattr(regressor, "fit", None))
    assert callable(getattr(regressor, "predict", None))


def test_train_fn_passes_check_estimator():
    regressor = estimator_fn()
    check_estimator(regressor)
