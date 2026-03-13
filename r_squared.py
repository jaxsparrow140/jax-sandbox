"""
Calculate R-squared value from scratch without sklearn or numpy.

R-squared = 1 - (SS_res / SS_tot)
where SS_res = sum of squared residuals
      SS_tot = total sum of squares
"""

def r_squared(actual, predicted):
    """
    Calculate the R-squared value given two lists of actual and predicted values.
    
    Args:
        actual: List of actual values
        predicted: List of predicted values
        
    Returns:
        float: R-squared value between 0 and 1 (higher is better)
        
    Raises:
        ValueError: If lists have different lengths or are empty
    """
    # Check if lists have the same length and are not empty
    if len(actual) != len(predicted):
        raise ValueError("Actual and predicted lists must have the same length")
    
    if len(actual) == 0:
        raise ValueError("Lists cannot be empty")
    
    # Calculate mean of actual values
    mean_actual = sum(actual) / len(actual)
    
    # Calculate sum of squared residuals (SS_res)
    ss_res = sum((actual[i] - predicted[i]) ** 2 for i in range(len(actual)))
    
    # Calculate total sum of squares (SS_tot)
    ss_tot = sum((actual[i] - mean_actual) ** 2 for i in range(len(actual)))
    
    # Handle edge case where SS_tot is 0 (all actual values are the same)
    if ss_tot == 0:
        return 1.0 if ss_res == 0 else 0.0
    
    # Calculate R-squared
    r2 = 1 - (ss_res / ss_tot)
    
    return r2

# Example usage (for testing)
if __name__ == "__main__":
    # Test with sample data
    actual_values = [3, -0.5, 2, 7]
    predicted_values = [2.5, 0.0, 2, 8]
    
    result = r_squared(actual_values, predicted_values)
    print(f"Actual: {actual_values}")
    print(f"Predicted: {predicted_values}")
    print(f"R-squared: {result:.4f}")
    
    # Test with identical values (should be 1.0)
    actual_values2 = [1, 2, 3, 4, 5]
    predicted_values2 = [1, 2, 3, 4, 5]
    result2 = r_squared(actual_values2, predicted_values2)
    print(f"\nIdentical values test:")
    print(f"Actual: {actual_values2}")
    print(f"Predicted: {predicted_values2}")
    print(f"R-squared: {result2:.4f}")
    
    # Test with constant actual values (should be 0.0 if predictions are wrong)
    actual_values3 = [2, 2, 2, 2]
    predicted_values3 = [1, 3, 1, 3]
    result3 = r_squared(actual_values3, predicted_values3)
    print(f"\nConstant actual values test:")
    print(f"Actual: {actual_values3}")
    print(f"Predicted: {predicted_values3}")
    print(f"R-squared: {result3:.4f}")