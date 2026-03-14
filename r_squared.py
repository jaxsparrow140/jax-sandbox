"""
R-squared calculation from scratch without sklearn or numpy
"""

def r_squared(actual, predicted):
    """
    Calculate R-squared (coefficient of determination) given two lists:
    - actual: list of actual values
    - predicted: list of predicted values
    
    Returns the R-squared value (float)
    """
    # Validate inputs
    if len(actual) != len(predicted):
        raise ValueError("Actual and predicted lists must have the same length")
    
    if len(actual) == 0:
        return 0.0
    
    # Calculate mean of actual values
    mean_actual = sum(actual) / len(actual)
    
    # Calculate total sum of squares (TSS)
    tss = sum((actual_i - mean_actual) ** 2 for actual_i in actual)
    
    # Calculate residual sum of squares (RSS)
    rss = sum((actual_i - predicted_i) ** 2 for actual_i, predicted_i in zip(actual, predicted))
    
    # Calculate R-squared: 1 - (RSS/TSS)
    # Handle edge case where TSS is 0 (all actual values are the same)
    if tss == 0:
        return 1.0
    
    return 1 - (rss / tss)

# Example usage (for testing)
if __name__ == "__main__":
    # Test with sample data
    actual_values = [3, -0.5, 2, 7]
    predicted_values = [2.5, 0.0, 2, 8]
    r2 = r_squared(actual_values, predicted_values)
    print(f"R-squared: {r2:.6f}")
    
    # Test with identical values (should be 1.0)
    actual_values2 = [1, 2, 3, 4, 5]
    predicted_values2 = [1, 2, 3, 4, 5]
    r2_2 = r_squared(actual_values2, predicted_values2)
    print(f"R-squared (identical): {r2_2:.6f}")
    
    # Test with all same actual values (should be 1.0)
    actual_values3 = [5, 5, 5, 5]
    predicted_values3 = [4, 6, 5, 5]
    r2_3 = r_squared(actual_values3, predicted_values3)
    print(f"R-squared (all actual same): {r2_3:.6f}")