def calculate_r_squared(actual, predicted):
    """
    Calculate the R-squared (coefficient of determination) value.
    
    Args:
        actual: List of actual values
        predicted: List of predicted values
    
    Returns:
        R-squared value (float)
    
    R-squared = 1 - (SS_res / SS_tot)
    where:
        SS_res = sum of squared residuals = sum((actual - predicted)^2)
        SS_tot = total sum of squares = sum((actual - mean(actual))^2)
    """
    # Check that lists have the same length
    if len(actual) != len(predicted):
        raise ValueError("Actual and predicted lists must have the same length")
    
    if len(actual) == 0:
        raise ValueError("Lists cannot be empty")
    
    # Calculate the mean of actual values
    mean_actual = sum(actual) / len(actual)
    
    # Calculate SS_res (sum of squared residuals)
    ss_res = sum((a - p) ** 2 for a, p in zip(actual, predicted))
    
    # Calculate SS_tot (total sum of squares)
    ss_tot = sum((a - mean_actual) ** 2 for a in actual)
    
    # Handle edge case where all actual values are the same
    if ss_tot == 0:
        if ss_res == 0:
            return 1.0  # Perfect prediction
        else:
            return 0.0  # Can't explain any variance
    
    # Calculate R-squared
    r_squared = 1 - (ss_res / ss_tot)
    
    return r_squared


# Example usage and test
if __name__ == "__main__":
    # Test case 1: Perfect prediction
    actual1 = [1, 2, 3, 4, 5]
    predicted1 = [1, 2, 3, 4, 5]
    print(f"Perfect prediction: {calculate_r_squared(actual1, predicted1)}")
    
    # Test case 2: Good prediction
    actual2 = [1, 2, 3, 4, 5]
    predicted2 = [1.1, 2.1, 2.9, 4.2, 4.8]
    print(f"Good prediction: {calculate_r_squared(actual2, predicted2)}")
    
    # Test case 3: Poor prediction
    actual3 = [1, 2, 3, 4, 5]
    predicted3 = [5, 4, 3, 2, 1]
    print(f"Poor prediction: {calculate_r_squared(actual3, predicted3)}")
    
    # Test case 4: All same values
    actual4 = [3, 3, 3, 3, 3]
    predicted4 = [3, 3, 3, 3, 3]
    print(f"All same values: {calculate_r_squared(actual4, predicted4)}")