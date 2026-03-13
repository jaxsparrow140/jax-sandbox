# R-squared calculation function
# No sklearn or numpy dependencies

def r_squared(actual, predicted):
    """
    Calculate the R-squared value given two lists of actual and predicted values.
    
    Args:
        actual: list of actual values
        predicted: list of predicted values
        
    Returns:
        float: R-squared value
    """
    if len(actual) != len(predicted):
        raise ValueError("Actual and predicted lists must have the same length")
    
    n = len(actual)
    if n == 0:
        return 0
    
    # Calculate mean of actual values
    mean_actual = sum(actual) / n
    
    # Calculate total sum of squares (TSS)
    tss = sum((a - mean_actual) ** 2 for a in actual)
    
    # Calculate residual sum of squares (RSS)
    rss = sum((a - p) ** 2 for a, p in zip(actual, predicted))
    
    # Handle edge case where TSS is 0 (all actual values are the same)
    if tss == 0:
        return 1.0 if rss == 0 else 0.0
    
    # Calculate R-squared
    r2 = 1 - (rss / tss)
    
    return r2

# Example usage (for testing)
if __name__ == "__main__":
    # Test with sample data
    actual = [3, -0.5, 2, 7]
    predicted = [2.5, 0.0, 2, 8]
    result = r_squared(actual, predicted)
    print(f"R-squared: {result}")