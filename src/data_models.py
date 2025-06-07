"""
Data models and validation for the reimbursement system.

This module defines the core data structures and validation logic
to ensure data integrity throughout the system.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import logging


logger = logging.getLogger(__name__)


@dataclass
class TripInput:
    """
    Represents the input parameters for a trip reimbursement calculation.
    
    Attributes:
        trip_duration_days: Number of days spent traveling (must be positive)
        miles_traveled: Total miles traveled (must be non-negative)
        total_receipts_amount: Total dollar amount of receipts (must be non-negative)
    """
    trip_duration_days: int
    miles_traveled: float
    total_receipts_amount: float
    
    def __post_init__(self):
        """Validate input parameters after initialization"""
        self.validate()
    
    def validate(self) -> None:
        """
        Validate trip input parameters.
        
        Raises:
            ValueError: If any parameter is invalid
        """
        if not isinstance(self.trip_duration_days, int) or self.trip_duration_days <= 0:
            raise ValueError(f"trip_duration_days must be a positive integer, got {self.trip_duration_days}")
        
        if not isinstance(self.miles_traveled, (int, float)) or self.miles_traveled < 0:
            raise ValueError(f"miles_traveled must be non-negative, got {self.miles_traveled}")
        
        if not isinstance(self.total_receipts_amount, (int, float)) or self.total_receipts_amount < 0:
            raise ValueError(f"total_receipts_amount must be non-negative, got {self.total_receipts_amount}")
        
        # Sanity checks for reasonable values
        if self.trip_duration_days > 365:
            logger.warning(f"Unusually long trip: {self.trip_duration_days} days")
        
        if self.miles_traveled > 10000:
            logger.warning(f"Unusually long distance: {self.miles_traveled} miles")
        
        if self.total_receipts_amount > 50000:
            logger.warning(f"Unusually high receipts: ${self.total_receipts_amount}")
    
    @property
    def miles_per_day(self) -> float:
        """Calculate miles per day (efficiency metric)"""
        return self.miles_traveled / self.trip_duration_days
    
    @property
    def receipts_per_day(self) -> float:
        """Calculate receipts per day (spending rate)"""
        return self.total_receipts_amount / self.trip_duration_days


@dataclass
class ReimbursementResult:
    """
    Represents the result of a reimbursement calculation.
    
    Attributes:
        amount: The calculated reimbursement amount
        confidence: Optional confidence score (0-1) for the prediction
        breakdown: Optional breakdown of how the amount was calculated
        warnings: Optional list of warnings about the calculation
    """
    amount: float
    confidence: Optional[float] = None
    breakdown: Optional[Dict[str, float]] = None
    warnings: Optional[List[str]] = None
    
    def __post_init__(self):
        """Validate result after initialization"""
        self.validate()
    
    def validate(self) -> None:
        """
        Validate reimbursement result.
        
        Raises:
            ValueError: If the result is invalid
        """
        if not isinstance(self.amount, (int, float)) or self.amount < 0:
            raise ValueError(f"Reimbursement amount must be non-negative, got {self.amount}")
        
        if self.confidence is not None:
            if not isinstance(self.confidence, (int, float)) or not 0 <= self.confidence <= 1:
                raise ValueError(f"Confidence must be between 0 and 1, got {self.confidence}")
        
        if self.amount > 100000:  # Sanity check
            logger.warning(f"Unusually high reimbursement: ${self.amount}")


@dataclass
class TestCase:
    """
    Represents a test case for validation.
    
    Attributes:
        input_data: The trip input data
        expected_output: Expected reimbursement amount (None for private cases)
        case_id: Optional identifier for the test case
    """
    input_data: TripInput
    expected_output: Optional[float] = None
    case_id: Optional[str] = None
    
    def __post_init__(self):
        """Validate test case after initialization"""
        if self.expected_output is not None and self.expected_output < 0:
            raise ValueError(f"Expected output must be non-negative, got {self.expected_output}")


@dataclass
class ValidationMetrics:
    """
    Metrics for evaluating model performance.
    
    Attributes:
        mean_absolute_error: Average absolute error
        exact_matches: Number of exact matches (within tolerance)
        close_matches: Number of close matches (within tolerance)
        max_error: Maximum absolute error
        total_cases: Total number of test cases
        score: Overall score (lower is better)
    """
    mean_absolute_error: float
    exact_matches: int
    close_matches: int
    max_error: float
    total_cases: int
    score: float
    
    @property
    def exact_match_rate(self) -> float:
        """Calculate exact match rate as percentage"""
        return (self.exact_matches / self.total_cases) * 100 if self.total_cases > 0 else 0
    
    @property
    def close_match_rate(self) -> float:
        """Calculate close match rate as percentage"""
        return (self.close_matches / self.total_cases) * 100 if self.total_cases > 0 else 0
    
    def __str__(self) -> str:
        """Human-readable representation of metrics"""
        return (
            f"ValidationMetrics:\n"
            f"  Mean Absolute Error: ${self.mean_absolute_error:.2f}\n"
            f"  Exact Matches: {self.exact_matches}/{self.total_cases} ({self.exact_match_rate:.1f}%)\n"
            f"  Close Matches: {self.close_matches}/{self.total_cases} ({self.close_match_rate:.1f}%)\n"
            f"  Max Error: ${self.max_error:.2f}\n"
            f"  Score: {self.score:.2f}"
        )