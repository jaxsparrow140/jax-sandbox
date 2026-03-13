"""
Calculate R-squared (coefficient of determination) without sklearn or numpy.

R-squared measures how well the predicted values explain the variation in actual values.
Formula: R² = 1 - (SS_res / SS_tot)
where:
  SS_res = sum of squared residuals = Σ(y_actual - y_pred)²
  SS_tot = total sum of squares = Σ(y_actual - y_mean)²
"""


def calculate_r_squared(actual: list[float], predicted: list[float]) -> float:
    """
    Calculate R-squared value given actual and predicted values.
    
    Args:
        actual: List of actual/observed values
        predicted: List of predicted values
    
    Returns:
        R-squared value (float between 0 and 1 for good fits, can be negative)
    
    Raises:
        ValueError: If lists are empty, have different lengths, or SS_tot is zero
    """
    if len(actual) != len(predicted):
        raise ValueError("Actual and predicted lists must have the same length")
    
    if len(actual) == 0:
        raise ValueError("Lists cannot be empty")
    
    # Calculate mean of actual values
    n = len(actual)
    actual_mean = sum(actual) / n
    
    # Calculate SS_res (sum of squared residuals)
    ss_res = sum((a - p) ** 2 for a, p in zip(actual, predicted))
    
    # Calculate SS_tot (total sum of squares)
    ss_tot = sum((a - actual_mean) ** 2 for a in actual)
    
    if ss_tot == 0:
        raise ValueError("SS_tot is zero - all actual values are identical")
    
    # R² = 1 - (SS_res / SS_tot)
    r_squared = 1 - (ss_res / ss_tot)
    
    return r_squared


if __name__ == "__main__":
    # Test with simple example
    actual = [1.0, 2.0, 3.0, 4.0, 5.0]
    predicted = [1.1, 2.1, 2.9, 4.2, 4.8]
    
    r2 = calculate_r_squared(actual, predicted)
    print(f"R-squared: {r2:.4f}")
    
    # Perfect fit test
    perfect = [1.0, 2.0, 3.0, 4.0, 5.0]
    r2_perfect = calculate_r_squared(actual, perfect)
    print(f"Perfect fit R-squared: {r2_perfect:.4f}")
    
    # Poor fit test
    poor = [5.0, 4.0, 3.0, 2.0, 1.0]
    r2_poor = calculate_r_squared(actual, poor)
    print(f"Poor fit R-squared: {r2_poor:.4f}")