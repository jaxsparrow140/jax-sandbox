"""Pure-Python R-squared calculation — no external libraries."""


def r_squared(actual: list[float], predicted: list[float]) -> float:
    """Return the coefficient of determination (R²) for actual vs predicted values.

    R² = 1 - SS_res / SS_tot

    where
        SS_res = Σ(actual_i - predicted_i)²   (residual sum of squares)
        SS_tot = Σ(actual_i - mean(actual))²   (total sum of squares)

    Args:
        actual:    List of observed values.
        predicted: List of predicted values (same length as actual).

    Returns:
        R² as a float.  1.0 = perfect fit, 0.0 = no better than the mean,
        negative = worse than the mean.

    Raises:
        ValueError: If the lists are empty or differ in length.
        ZeroDivisionError: If all actual values are identical (SS_tot == 0).
    """
    if len(actual) != len(predicted):
        raise ValueError(
            f"Length mismatch: actual has {len(actual)} elements, "
            f"predicted has {len(predicted)}"
        )
    if not actual:
        raise ValueError("Lists must not be empty")

    mean_actual = sum(actual) / len(actual)

    ss_res = sum((a - p) ** 2 for a, p in zip(actual, predicted))
    ss_tot = sum((a - mean_actual) ** 2 for a in actual)

    if ss_tot == 0:
        raise ZeroDivisionError(
            "R² is undefined when all actual values are identical (SS_tot = 0)"
        )

    return 1 - ss_res / ss_tot


# ── quick demo ──────────────────────────────────────────────
if __name__ == "__main__":
    y      = [3, -0.5, 2, 7]
    y_hat  = [2.5, 0.0, 2, 8]

    score = r_squared(y, y_hat)
    print(f"Actual:    {y}")
    print(f"Predicted: {y_hat}")
    print(f"R²:        {score:.6f}")
