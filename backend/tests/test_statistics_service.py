import pytest
from pydantic import ValidationError

from app.schemas.statistics import (
    GroupedSamplesRequest,
    NumericSeriesRequest,
    RegressionRequest,
    TwoSampleRequest,
)
from app.services.statistics import (
    describe_values,
    independent_t_test,
    one_way_anova,
    simple_linear_regression,
)


def test_describe_values_returns_core_metrics():
    result = describe_values([1, 2, 3, 4])

    assert result["n"] == 4
    assert result["mean"] == pytest.approx(2.5)
    assert result["std"] == pytest.approx(1.2909944487)


def test_independent_t_test_returns_p_value():
    result = independent_t_test([10, 11, 12, 13], [12, 13, 14, 15], equal_var=True)

    assert result["test"] == "independent_t_test"
    assert result["statistic"] < 0
    assert 0 < result["p_value"] < 1


def test_one_way_anova_detects_group_difference():
    result = one_way_anova([[1, 2, 1], [5, 6, 5], [9, 10, 9]])

    assert result["test"] == "one_way_anova"
    assert result["statistic"] > 0
    assert result["p_value"] < 0.01


def test_simple_linear_regression_returns_slope():
    result = simple_linear_regression([1, 2, 3], [2, 4, 6])

    assert result["test"] == "simple_linear_regression"
    assert result["slope"] == pytest.approx(2.0)
    assert result["intercept"] == pytest.approx(0.0)


@pytest.mark.parametrize(
    ("operation", "match"),
    [
        (lambda: describe_values([1, float("nan")]), "Values must be finite"),
        (
            lambda: independent_t_test([1, 2], [float("inf"), 3], equal_var=False),
            "Values must be finite",
        ),
        (
            lambda: one_way_anova([[1, 2], [3, float("-inf")]]),
            "Values must be finite",
        ),
        (
            lambda: simple_linear_regression([1, 2], [3, float("nan")]),
            "Values must be finite",
        ),
    ],
)
def test_service_functions_reject_nan_and_inf(operation, match):
    with pytest.raises(ValueError, match=match):
        operation()


@pytest.mark.parametrize(
    ("operation", "match"),
    [
        (
            lambda: independent_t_test([1], [2, 3], equal_var=False),
            "At least 2 values are required",
        ),
        (
            lambda: one_way_anova([[1], [2, 3]]),
            "At least 2 values are required",
        ),
        (
            lambda: simple_linear_regression([1], [2]),
            "At least 2 values are required",
        ),
    ],
)
def test_short_groups_raise_clear_min_length_error(operation, match):
    with pytest.raises(ValueError, match=match):
        operation()


def test_simple_linear_regression_rejects_unequal_lengths():
    with pytest.raises(ValueError, match="x and y must have the same length"):
        simple_linear_regression([1, 2, 3], [2, 4])


@pytest.mark.parametrize(
    "operation",
    [
        lambda: independent_t_test([1, 1, 1], [1, 1, 1], equal_var=False),
        lambda: one_way_anova([[1, 1], [1, 1]]),
    ],
)
def test_constant_samples_raise_when_statistical_result_is_not_finite(operation):
    with pytest.raises(ValueError, match="Statistical result is not finite"):
        operation()


def test_constant_x_regression_input_raises_clear_value_error():
    with pytest.raises(ValueError, match="x values must not all be identical"):
        simple_linear_regression([1, 1, 1], [2, 3, 4])


@pytest.mark.parametrize(
    "operation",
    [
        lambda: NumericSeriesRequest(values=[1, float("inf")]),
        lambda: TwoSampleRequest(group_a=[1, float("nan")], group_b=[2, 3]),
        lambda: GroupedSamplesRequest(groups=[[1, 2], [3, float("-inf")]]),
        lambda: RegressionRequest(x=[1, 2], y=[3, float("nan")]),
    ],
)
def test_statistics_schemas_reject_non_finite_values(operation):
    with pytest.raises(ValidationError):
        operation()
