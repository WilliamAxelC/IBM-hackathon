"""
Benchmark test runner — imports parametrized tests from conftest.py.
This file exists to give pytest a discoverable test module in the benchmarks directory.
The actual test functions and parametrization are defined in conftest.py.
"""
# Tests are defined in conftest.py via pytest_collect_file / parametrize.
# This file is intentionally minimal — pytest discovers tests from conftest.py.

from kevgate.benchmarks.conftest import (
    test_true_positive_is_blocked,
    test_false_positive_is_not_blocked,
)

__all__ = ["test_true_positive_is_blocked", "test_false_positive_is_not_blocked"]
