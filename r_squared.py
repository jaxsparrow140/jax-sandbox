"""
Calculate R-squared (coefficient of determination) from scratch without sklearn or numpy.

R-squared = 1 - (SS_res / SS_tot)
where:
- SS_res = sum of squared residuals (actual - predicted)^2
- SS_tot = total sum of squares (actual - mean_actual)^2
"""

def r_squared(actual, predicted):
    """
    Calculate R-squared given two lists of actual and predicted values.
    
    Args:
        actual: list of actual values
        predicted: list of predicted values
        
    Returns:
        float: R-squared value between 0 and 1 (higher is better)
        
    Raises:
        ValueError: if lists have different lengths or are empty
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

# Example usage and test cases
if __name__ == "__main__":
    # Test case 1: Perfect prediction
    actual1 = [1, 2, 3, 4, 5]
    predicted1 = [1, 2, 3, 4, 5]
    print(f"Test 1 - Perfect prediction: R² = {r_squared(actual1, predicted1):.4f}")
    
    # Test case 2: Random prediction
    actual2 = [1, 2, 3, 4, 5]
    predicted2 = [2, 3, 4, 5, 6]
    print(f"Test 2 - Random prediction: R² = {r_squared(actual2, predicted2):.4f}")
    
    # Test case 3: All same values
    actual3 = [3, 3, 3, 3]
    predicted3 = [3, 3, 3, 3]
    print(f"Test 3 - All same values: R² = {r_squared(actual3, predicted3):.4f}")
    
    # Test case 4: Negative correlation
    actual4 = [1, 2, 3, 4, 5]
    predicted4 = [5, 4, 3, 2, 1]
    print(f"Test 4 - Negative correlation: R² = {r_squared(actual4, predicted4):.4f}")
    
    # Test case 5: Mixed results
    actual5 = [10, 15, 20, 25, 30]
    predicted5 = [12, 14, 18, 26, 32]
    print(f"Test 5 - Mixed results: R² = {r_squared(actual5, predicted5):.4f}")