"""Pure-Python R-squared (R²) implementation.

No numpy, no sklearn — just standard Python.

R² (coefficient of determination) is defined as:

    R² = 1 - SS_res / SS_tot

where
    SS_res = Σ(y_true - y_pred)²
    SS_tot = Σ(y_true - mean(y_true))²

Notes on edge-cases:
- If the true values are constant (SS_tot == 0), many libraries (e.g., sklearn)
  define R² as:
    * 1.0 if predictions are perfect (SS_res == 0)
    * 0.0 otherwise
  This avoids division-by-zero while still being informative.
"""

from __future__ import annotations


def r2_score(y_true: list[float], y_pred: list[float]) -> float:
    """Compute the R-squared (R²) value for two equal-length lists.

    Args:
        y_true: Actual/observed values.
        y_pred: Predicted values (same length as y_true).

    Returns:
        R² as a float.

    Raises:
        ValueError: If inputs are empty or lengths differ.
    """
    if len(y_true) != len(y_pred):
        raise ValueError(
            f"Length mismatch: y_true has {len(y_true)} elements, "
            f"y_pred has {len(y_pred)}"
        )
    if len(y_true) == 0:
        raise ValueError("Inputs must be non-empty")

    mean_true = sum(y_true) / len(y_true)

    ss_res = 0.0
    ss_tot = 0.0
    for yt, yp in zip(y_true, y_pred):
        diff = yt - yp
        ss_res += diff * diff

        centered = yt - mean_true
        ss_tot += centered * centered

    if ss_tot == 0.0:
        # True values are constant.
        return 1.0 if ss_res == 0.0 else 0.0

    return 1.0 - (ss_res / ss_tot)


if __name__ == "__main__":
    y = [3, -0.5, 2, 7]
    y_hat = [2.5, 0.0, 2, 8]
    print(r2_score(y, y_hat))
