import pytest
import os
import tempfile
import pandas as pd
from pandas import DataFrame
from steps.ingest import load_file_as_dataframe


@pytest.fixture
def sample_data():
    return pd.read_parquet(
        os.path.join(os.path.dirname(__file__), "test_sample.parquet")
    )


def test_ingest_function_reads_csv_correctly(sample_data):
    tempdir = tempfile.mkdtemp()
    csv_path = os.path.join(tempdir, "test_sample.csv")
    sample_data.to_csv(csv_path)

    ingested = load_file_as_dataframe(csv_path, "csv")
    assert isinstance(ingested, DataFrame)
