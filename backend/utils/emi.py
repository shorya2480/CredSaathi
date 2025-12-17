"""
EMI (Equated Monthly Installment) Calculator Module
Implements standard Indian loan calculation formulas
"""

def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """
    Calculate EMI using the standard formula:
    EMI = P * R * (1 + R)^N / ((1 + R)^N - 1)
    
    Where:
    - P = Principal (loan amount)
    - R = Monthly interest rate (annual rate / 12 / 100)
    - N = Number of months (tenure)
    
    Args:
        principal: Loan amount in rupees
        annual_rate: Annual interest rate (e.g., 10.5 for 10.5% per annum)
        tenure_months: Loan tenure in months
    
    Returns:
        Monthly EMI amount
    
    Example:
        >>> calculate_emi(500000, 10.5, 60)  # ₹5L at 10.5% for 5 years
        10657.92
    """
    if principal <= 0 or tenure_months <= 0 or annual_rate < 0:
        raise ValueError("Principal, tenure, and rate must be positive values")
    
    monthly_rate = annual_rate / 12 / 100
    
    # Avoid division by zero for 0% interest
    if monthly_rate == 0:
        return principal / tenure_months
    
    # EMI formula
    numerator = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months)
    denominator = ((1 + monthly_rate) ** tenure_months) - 1
    
    emi = numerator / denominator
    return round(emi, 2)


def calculate_total_repayment(emi: float, tenure_months: int) -> float:
    """Calculate total amount to be repaid (EMI * number of months)"""
    return round(emi * tenure_months, 2)


def calculate_total_interest(principal: float, total_repayment: float) -> float:
    """Calculate total interest paid"""
    return round(total_repayment - principal, 2)


def validate_emi_affordability(emi: float, monthly_salary: float, max_emi_ratio: float = 0.5) -> tuple[bool, str]:
    """
    Validate if EMI is affordable based on salary.
    Standard lending rule: EMI should not exceed 50% of monthly salary.
    
    Args:
        emi: Monthly EMI amount
        monthly_salary: Monthly salary
        max_emi_ratio: Maximum allowed EMI as percentage of salary (default 50%)
    
    Returns:
        Tuple of (is_affordable: bool, reason: str)
    
    Example:
        >>> validate_emi_affordability(10000, 25000)
        (True, "EMI is 40.0% of monthly salary")
        >>> validate_emi_affordability(15000, 25000)
        (False, "EMI is 60.0% of monthly salary (max allowed: 50.0%)")
    """
    if monthly_salary <= 0:
        return False, "Invalid monthly salary"
    
    emi_ratio = (emi / monthly_salary) * 100
    
    if emi_ratio <= max_emi_ratio * 100:
        return True, f"EMI is {emi_ratio:.1f}% of monthly salary"
    else:
        return False, f"EMI is {emi_ratio:.1f}% of monthly salary (max allowed: {max_emi_ratio * 100:.1f}%)"


def suggest_tenure_for_affordability(principal: float, annual_rate: float, monthly_salary: float, max_emi_ratio: float = 0.5) -> dict:
    """
    Suggest optimal tenure for a given principal and rate to stay within affordability.
    
    Args:
        principal: Loan amount
        annual_rate: Annual interest rate
        monthly_salary: Monthly salary
        max_emi_ratio: Maximum allowed EMI ratio
    
    Returns:
        Dictionary with suggested tenure and corresponding EMI
    """
    max_emi = monthly_salary * max_emi_ratio
    
    # Try tenures from 12 to 120 months
    for tenure in range(12, 121, 12):
        emi = calculate_emi(principal, annual_rate, tenure)
        if emi <= max_emi:
            return {
                "suggested_tenure_months": tenure,
                "suggested_tenure_years": tenure / 12,
                "resulting_emi": emi,
                "affordable": True
            }
    
    # If no tenure works, return max tenure option
    emi = calculate_emi(principal, annual_rate, 120)
    return {
        "suggested_tenure_months": 120,
        "suggested_tenure_years": 10,
        "resulting_emi": emi,
        "affordable": emi <= max_emi,
        "note": "Could not find affordable tenure within 10 years"
    }
