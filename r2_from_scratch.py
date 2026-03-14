"""R-squared (coefficient of determination) implementation.

Constraints:
- Pure Python (no numpy / sklearn)
- Accepts two equal-length iterables of actual (y_true) and predicted (y_pred)

Definition:
    R^2 = 1 - SS_res / SS_tot
where
    SS_res = sum((y_i - yhat_i)^2)
    SS_tot = sum((y_i - mean(y))^2)

Edge case (constant y_true): SS_tot == 0.
Common convention (matches scikit-learn's default behavior):
- If predictions are perfect (SS_res == 0), return 1.0
- Otherwise return 0.0
"""

from __future__ import annotations

from typing import Iterable, Sequence, Union


Number = Union[int, float]


def r2_score(y_true: Sequence[Number], y_pred: Sequence[Number]) -> float:
    """Compute R-squared from two lists/sequences of actual and predicted values.

    Args:
        y_true: Sequence of actual values.
        y_pred: Sequence of predicted values.

    Returns:
        R-squared as a float.

    Raises:
        ValueError: If inputs have different lengths or are empty.
        TypeError: If any element cannot be converted to float.
    """

    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length")
    if len(y_true) == 0:
        raise ValueError("y_true and y_pred must be non-empty")

    # Convert to floats once to ensure consistent numeric behavior.
    try:
        yt = [float(v) for v in y_true]
        yp = [float(v) for v in y_pred]
    except (TypeError, ValueError) as e:
        raise TypeError("All elements in y_true and y_pred must be numeric") from e

    mean_y = sum(yt) / len(yt)

    ss_res = 0.0
    ss_tot = 0.0
    for a, p in zip(yt, yp):
        diff = a - p
        ss_res += diff * diff

        dev = a - mean_y
        ss_tot += dev * dev

    if ss_tot == 0.0:
        return 1.0 if ss_res == 0.0 else 0.0

    return 1.0 - (ss_res / ss_tot)
