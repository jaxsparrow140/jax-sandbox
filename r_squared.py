"""
R-squared calculation function without sklearn or numpy
"""

def r_squared(actual, predicted):
    """
    Calculate R-squared value given two lists: actual and predicted values.
    
    Args:
        actual: list of actual values
        predicted: list of predicted values
        
    Returns:
        float: R-squared value
    """
    # Check if lists have same length
    if len(actual) != len(predicted):
        raise ValueError("Actual and predicted lists must have the same length")
    
    # Calculate mean of actual values
    n = len(actual)
    mean_actual = sum(actual) / n
    
    # Calculate total sum of squares (TSS)
    tss = sum((actual_i - mean_actual) ** 2 for actual_i in actual)
    
    # Calculate residual sum of squares (RSS)
    rss = sum((actual_i - predicted_i) ** 2 for actual_i, predicted_i in zip(actual, predicted))
    
    # Calculate R-squared
    if tss == 0:
        return 1.0  # Perfect fit when all actual values are the same
    
    r2 = 1 - (rss / tss)
    
    return r2

# Example usage (for testing)
if __name__ == "__main__":
    # Test with sample data
    actual_values = [3, -0.5, 2, 7]
    predicted_values = [2.5, 0.0, 2, 8]
    result = r_squared(actual_values, predicted_values)
    print(f"R-squared: {result}")