"""
R-squared (Coefficient of Determination) — implemented from scratch.

No numpy, no sklearn. Just math.

R² = 1 - (SS_res / SS_tot)

Where:
  SS_res = sum of squared residuals = Σ(y_i - ŷ_i)²
  SS_tot = total sum of squares      = Σ(y_i - ȳ)²

R² ranges from -∞ to 1.0:
  1.0  → perfect fit
  0.0  → model performs no better than predicting the mean
  < 0  → model performs worse than predicting the mean
"""


def r_squared(actual: list[float], predicted: list[float]) -> float:
    """
    Calculate the R-squared (coefficient of determination) between
    actual and predicted values.

    Args:
        actual:    List of true/observed values.
        predicted: List of model-predicted values (same length as actual).

    Returns:
        R² as a float.

    Raises:
        ValueError: If inputs are empty, different lengths, or have zero variance.
    """
    if len(actual) != len(predicted):
        raise ValueError(
            f"Length mismatch: actual has {len(actual)} values, "
            f"predicted has {len(predicted)} values."
        )
    if len(actual) == 0:
        raise ValueError("Input lists must not be empty.")

    n = len(actual)

    # Mean of actual values
    mean_actual = sum(actual) / n

    # SS_res: sum of squared residuals (how far predictions are from truth)
    ss_res = sum((a - p) ** 2 for a, p in zip(actual, predicted))

    # SS_tot: total sum of squares (how far truth is from its mean)
    ss_tot = sum((a - mean_actual) ** 2 for a in actual)

    if ss_tot == 0:
        raise ValueError(
            "Total sum of squares is zero — all actual values are identical. "
            "R² is undefined in this case."
        )

    return 1 - (ss_res / ss_tot)


# ---------------------------------------------------------------------------
# Quick sanity checks
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Perfect predictions → R² should be 1.0
    actual = [1, 2, 3, 4, 5]
    predicted = [1, 2, 3, 4, 5]
    result = r_squared(actual, predicted)
    print(f"Perfect fit:        R² = {result:.4f}  (expected 1.0)")
    assert result == 1.0

    # Predicting the mean → R² should be 0.0
    mean_val = sum(actual) / len(actual)
    predicted_mean = [mean_val] * len(actual)
    result = r_squared(actual, predicted_mean)
    print(f"Mean prediction:    R² = {result:.4f}  (expected 0.0)")
    assert abs(result) < 1e-10

    # Typical case — decent fit
    actual =    [3.0, 4.5, 5.0, 7.0, 8.5]
    predicted = [2.8, 4.2, 5.3, 6.8, 8.7]
    result = r_squared(actual, predicted)
    print(f"Decent fit:         R² = {result:.4f}  (expected > 0.95)")
    assert result > 0.95

    # Bad predictions — worse than the mean → negative R²
    actual =    [1, 2, 3, 4, 5]
    predicted = [5, 4, 3, 2, 1]   # inverted
    result = r_squared(actual, predicted)
    print(f"Inverted (bad fit): R² = {result:.4f}  (expected < 0)")
    assert result < 0

    print("\nAll checks passed ✓")
