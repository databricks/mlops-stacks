import pytest
import os
import pandas as pd
from pandas import DataFrame
from steps.split import process_splits


@pytest.fixture
def sample_data():
    return pd.read_parquet(
        os.path.join(os.path.dirname(__file__), "test_sample.parquet")
    )


def test_post_split_fn_returns_datasets_with_correct_spec(sample_data):
    train = sample_data[0:3]
    validation = sample_data[4:7]
    test = sample_data[7:10]
    (train_processed, validation_processed, test_processed) = process_splits(
        train, validation, test
    )
    assert isinstance(train_processed, DataFrame)
    assert isinstance(validation_processed, DataFrame)
    assert isinstance(test_processed, DataFrame)


def test_post_split_fn_returns_non_empty_datasets(sample_data):
    train = sample_data[0:3]
    validation = sample_data[4:7]
    test = sample_data[7:10]
    (train_processed, validation_processed, test_processed) = process_splits(
        train, validation, test
    )
    assert not train_processed.empty
    assert not validation_processed.empty
    assert not test_processed.empty
