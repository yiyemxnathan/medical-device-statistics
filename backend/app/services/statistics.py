import numpy as np
from scipy import stats


def _array(values: list[float], min_length: int = 1) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if arr.size < min_length:
        raise ValueError(f"At least {min_length} values are required")
    if not np.isfinite(arr).all():
        raise ValueError("Values must be finite")
    return arr


def _ensure_finite_result(*values: float) -> None:
    if not np.isfinite(np.asarray(values, dtype=float)).all():
        raise ValueError("Statistical result is not finite")


def describe_values(values: list[float]) -> dict[str, float | int]:
    arr = _array(values)
    return {
        "n": int(arr.size),
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr, ddof=1)) if arr.size > 1 else 0.0,
        "min": float(np.min(arr)),
        "median": float(np.median(arr)),
        "max": float(np.max(arr)),
    }


def independent_t_test(
    group_a: list[float],
    group_b: list[float],
    equal_var: bool,
) -> dict[str, float | str | bool]:
    a = _array(group_a, min_length=2)
    b = _array(group_b, min_length=2)
    if np.ptp(a) == 0 and np.ptp(b) == 0:
        raise ValueError("Statistical result is not finite")
    statistic, p_value = stats.ttest_ind(a, b, equal_var=equal_var)
    _ensure_finite_result(statistic, p_value)
    return {
        "test": "independent_t_test",
        "statistic": float(statistic),
        "p_value": float(p_value),
        "equal_var": equal_var,
    }


def one_way_anova(groups: list[list[float]]) -> dict[str, float | str]:
    arrays = [_array(group, min_length=2) for group in groups]
    if all(np.ptp(group) == 0 for group in arrays):
        raise ValueError("Statistical result is not finite")
    statistic, p_value = stats.f_oneway(*arrays)
    _ensure_finite_result(statistic, p_value)
    return {
        "test": "one_way_anova",
        "statistic": float(statistic),
        "p_value": float(p_value),
    }


def simple_linear_regression(x: list[float], y: list[float]) -> dict[str, float | str]:
    x_arr = _array(x, min_length=2)
    y_arr = _array(y, min_length=2)
    if x_arr.size != y_arr.size:
        raise ValueError("x and y must have the same length")
    if np.ptp(x_arr) == 0:
        raise ValueError("x values must not all be identical")
    result = stats.linregress(x_arr, y_arr)
    _ensure_finite_result(
        result.slope,
        result.intercept,
        result.rvalue,
        result.pvalue,
        result.stderr,
    )
    return {
        "test": "simple_linear_regression",
        "slope": float(result.slope),
        "intercept": float(result.intercept),
        "r_value": float(result.rvalue),
        "p_value": float(result.pvalue),
        "stderr": float(result.stderr),
    }
