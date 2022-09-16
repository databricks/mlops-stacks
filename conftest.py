"""
This pytest configuration was adapted from MLflow:
https://github.com/mlflow/mlflow/blob/d382b2dd92065a68ea7ab6db16980fc65e1a8dca/conftest.py
"""
import os
import posixpath
import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--large-only",
        action="store_true",
        dest="large_only",
        default=False,
        help="Run only tests decorated with 'large' annotation",
    )
    parser.addoption(
        "--large",
        action="store_true",
        dest="large",
        default=False,
        help="Run tests decorated with 'large' annotation",
    )


def pytest_configure(config):
    # Register markers to suppress `PytestUnknownMarkWarning`
    config.addinivalue_line("markers", "large")


def pytest_runtest_setup(item):
    markers = [mark.name for mark in item.iter_markers()]
    marked_as_large = "large" in markers
    large_option = item.config.getoption("--large")
    large_only_option = item.config.getoption("--large-only")
    if marked_as_large and not (large_option or large_only_option):
        pytest.skip("use `--large` or `--large-only` to run this test")
    if not marked_as_large and large_only_option:
        pytest.skip("remove `--large-only` to run this test")
