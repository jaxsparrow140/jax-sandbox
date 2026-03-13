"""
r2_calculator.py

R-squared (coefficient of determination) from scratch.
No sklearn, no numpy — pure Python.

R² measures how well predictions approximate actual values:
  R² = 1 - (SS_res / SS_tot)

Where:
  SS_res = Σ(actual_i - predicted_i)²  (residual sum of squares)
  SS_tot = Σ(actual_i - mean_actual)²   (total sum of squares)

Interpretation:
  R² = 1.0  → perfect fit (predictions match actuals exactly)
  R² = 0.0  → model performs no better than predicting the mean
  R² < 0.0  → model performs worse than predicting the mean
"""


def r_squared(actual: list[float], predicted: list[float]) -> float:
    """
    Calculate the R-squared (coefficient of determination) between actual
    and predicted values.

    Args:
        actual:    List of observed/ground-truth values.
        predicted: List of model-predicted values, same length as actual.

    Returns:
        R-squared as a float.

    Raises:
        ValueError: If lists are empty or have different lengths.
        TypeError:  If any element is non-numeric.
    """
    if len(actual) == 0 or len(predicted) == 0:
        raise ValueError("actual and predicted must not be empty")

    if len(actual) != len(predicted):
        raise ValueError(
            f"Length mismatch: actual has {len(actual)} elements, "
            f"predicted has {len(predicted)}"
        )

    # Validate types up front
    for i, (a, p) in enumerate(zip(actual, predicted)):
        if not isinstance(a, (int, float)):
            raise TypeError(f"actual[{i}] = {a!r} is not numeric")
        if not isinstance(p, (int, float)):
            raise TypeError(f"predicted[{i}] = {p!r} is not numeric")

    n = len(actual)

    # Mean of actual values
    mean_actual = sum(actual) / n

    # Total sum of squares — variance of actual values (scaled by n)
    ss_tot = sum((a - mean_actual) ** 2 for a in actual)

    # Edge case: all actual values are identical → R² is undefined;
    # return 1.0 only if predictions are also perfect, else 0.0.
    if ss_tot == 0.0:
        ss_res = sum((a - p) ** 2 for a, p in zip(actual, predicted))
        return 1.0 if ss_res == 0.0 else 0.0

    # Residual sum of squares
    ss_res = sum((a - p) ** 2 for a, p in zip(actual, predicted))

    return 1.0 - (ss_res / ss_tot)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def _approx_equal(a: float, b: float, tol: float = 1e-9) -> bool:
    return abs(a - b) < tol


def run_tests():
    passed = 0
    failed = 0

    def check(name, actual_val, expected, tol=1e-9):
        nonlocal passed, failed
        if _approx_equal(actual_val, expected, tol):
            print(f"  PASS  {name}")
            passed += 1
        else:
            print(f"  FAIL  {name}: got {actual_val}, expected {expected}")
            failed += 1

    print("Running tests...\n")

    # Perfect fit
    check(
        "perfect fit",
        r_squared([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),
        1.0
    )

    # sklearn reference value: actual=[3,-0.5,2,7], predicted=[2.5,0,2,8] → ~0.9486...
    check(
        "sklearn reference case",
        r_squared([3, -0.5, 2, 7], [2.5, 0.0, 2, 8]),
        0.9486081370449679,
        tol=1e-9
    )

    # Mean predictor: predicted = mean(actual) → R² should be 0
    actual = [1.0, 2.0, 3.0, 4.0, 5.0]
    mean = sum(actual) / len(actual)
    check(
        "mean predictor → R²=0",
        r_squared(actual, [mean] * len(actual)),
        0.0,
        tol=1e-9
    )

    # Terrible predictor → R² < 0
    r2 = r_squared([1, 2, 3], [10, 20, 30])
    if r2 < 0:
        print(f"  PASS  negative R² for bad predictor (got {r2:.4f})")
        passed += 1
    else:
        print(f"  FAIL  expected negative R², got {r2}")
        failed += 1

    # Single element
    check("single element, perfect", r_squared([42.0], [42.0]), 1.0)
    check("single element, wrong pred", r_squared([42.0], [0.0]), 0.0)

    # All-same actuals (constant series), perfect prediction
    check("constant actuals, perfect pred", r_squared([5, 5, 5], [5, 5, 5]), 1.0)

    # All-same actuals, imperfect prediction
    check("constant actuals, bad pred", r_squared([5, 5, 5], [1, 2, 3]), 0.0)

    # Floats
    check(
        "floats",
        r_squared([0.1, 0.2, 0.3], [0.1, 0.2, 0.3]),
        1.0
    )

    # ValueError: mismatched lengths
    try:
        r_squared([1, 2, 3], [1, 2])
        print("  FAIL  should have raised ValueError for length mismatch")
        failed += 1
    except ValueError:
        print("  PASS  raises ValueError on length mismatch")
        passed += 1

    # ValueError: empty lists
    try:
        r_squared([], [])
        print("  FAIL  should have raised ValueError for empty input")
        failed += 1
    except ValueError:
        print("  PASS  raises ValueError on empty input")
        passed += 1

    # TypeError: non-numeric values
    try:
        r_squared([1, "two", 3], [1, 2, 3])
        print("  FAIL  should have raised TypeError for non-numeric actual")
        failed += 1
    except TypeError:
        print("  PASS  raises TypeError on non-numeric actual")
        passed += 1

    print(f"\n{passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    # Quick demo
    actual    = [3, -0.5, 2, 7]
    predicted = [2.5, 0.0, 2, 8]
    print(f"Demo — actual={actual}, predicted={predicted}")
    print(f"R² = {r_squared(actual, predicted):.6f}\n")

    run_tests()
