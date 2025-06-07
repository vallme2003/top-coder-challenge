"""
Feature engineering module for the reimbursement system.

This module handles feature extraction and transformation to convert
raw trip data into features suitable for machine learning models.
"""

import math
import logging
from typing import List, Dict, Any, Optional
import numpy as np
from dataclasses import dataclass

from .data_models import TripInput
from .config import ModelConfig


logger = logging.getLogger(__name__)


@dataclass
class FeatureSet:
    """
    Container for extracted features.
    
    Attributes:
        basic_features: Core input features
        derived_features: Calculated features (ratios, interactions, etc.)
        categorical_features: Binary indicator features
        transformed_features: Log, polynomial, etc. transformations
        feature_names: Names of all features for interpretability
    """
    basic_features: List[float]
    derived_features: List[float]
    categorical_features: List[float]
    transformed_features: List[float]
    feature_names: List[str]
    
    @property
    def all_features(self) -> List[float]:
        """Get all features as a single list"""
        return (self.basic_features + 
                self.derived_features + 
                self.categorical_features + 
                self.transformed_features)
    
    @property
    def feature_count(self) -> int:
        """Get total number of features"""
        return len(self.all_features)
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary mapping feature names to values"""
        if len(self.feature_names) != self.feature_count:
            raise ValueError("Feature names length doesn't match feature count")
        return dict(zip(self.feature_names, self.all_features))


class FeatureEngineer:
    """
    Feature engineering pipeline for trip reimbursement data.
    
    This class handles the extraction and transformation of features
    from raw trip data in a consistent, reproducible manner.
    """
    
    def __init__(self, config: ModelConfig):
        """
        Initialize the feature engineer.
        
        Args:
            config: Configuration object containing feature engineering parameters
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    def extract_features(self, trip_input: TripInput) -> FeatureSet:
        """
        Extract all features from a trip input.
        
        Args:
            trip_input: The trip data to extract features from
            
        Returns:
            FeatureSet containing all extracted features
            
        Raises:
            ValueError: If trip_input is invalid
        """
        try:
            # Validate input
            trip_input.validate()
            
            # Extract different types of features
            basic_features = self._extract_basic_features(trip_input)
            derived_features = self._extract_derived_features(trip_input)
            categorical_features = self._extract_categorical_features(trip_input)
            transformed_features = self._extract_transformed_features(trip_input)
            
            # Get feature names
            feature_names = self._get_feature_names()
            
            feature_set = FeatureSet(
                basic_features=basic_features,
                derived_features=derived_features,
                categorical_features=categorical_features,
                transformed_features=transformed_features,
                feature_names=feature_names
            )
            
            self.logger.debug(f"Extracted {feature_set.feature_count} features")
            return feature_set
            
        except Exception as e:
            self.logger.error(f"Feature extraction failed: {e}")
            raise
    
    def _extract_basic_features(self, trip_input: TripInput) -> List[float]:
        """Extract basic input features"""
        return [
            float(trip_input.trip_duration_days),
            float(trip_input.miles_traveled),
            float(trip_input.total_receipts_amount)
        ]
    
    def _extract_derived_features(self, trip_input: TripInput) -> List[float]:
        """Extract derived features (ratios, interactions, etc.)"""
        days = trip_input.trip_duration_days
        miles = trip_input.miles_traveled
        receipts = trip_input.total_receipts_amount
        
        # Avoid division by zero
        mpd = miles / days if days > 0 else 0
        rpd = receipts / days if days > 0 else 0
        
        derived = [
            mpd,  # miles per day
            rpd,  # receipts per day
            days * miles,  # interaction: days * miles
            days * receipts,  # interaction: days * receipts
            miles * receipts / 1000,  # interaction: miles * receipts (scaled)
            days * miles * receipts / 1000,  # three-way interaction (scaled)
        ]
        
        # Add efficiency ratios
        if receipts > 0:
            derived.extend([
                miles / receipts,  # miles per dollar
                1 / (1 + receipts),  # inverse receipts (diminishing returns)
            ])
        else:
            derived.extend([float('inf'), 1.0])  # Handle zero receipts case
        
        if miles > 0:
            derived.append(1 / (1 + miles))  # inverse miles
        else:
            derived.append(1.0)
        
        return derived
    
    def _extract_categorical_features(self, trip_input: TripInput) -> List[float]:
        """Extract binary categorical indicator features"""
        days = trip_input.trip_duration_days
        miles = trip_input.miles_traveled
        receipts = trip_input.total_receipts_amount
        mpd = miles / days if days > 0 else 0
        
        categorical = [
            1.0 if days == 5 else 0.0,  # 5-day bonus indicator
            1.0 if days >= 7 else 0.0,  # long trip indicator
            1.0 if receipts < 50 else 0.0,  # small receipts indicator
            1.0 if receipts > 1000 else 0.0,  # high receipts indicator
            1.0 if 180 <= mpd <= 220 else 0.0,  # optimal efficiency indicator
        ]
        
        # Receipt amount buckets
        categorical.extend([
            1.0 if 50 <= receipts < 200 else 0.0,
            1.0 if 200 <= receipts < 500 else 0.0,
            1.0 if 500 <= receipts < 1000 else 0.0,
        ])
        
        # Efficiency buckets
        categorical.extend([
            1.0 if mpd < 50 else 0.0,
            1.0 if 50 <= mpd < 100 else 0.0,
            1.0 if 100 <= mpd < 150 else 0.0,
            1.0 if mpd >= 150 else 0.0,
        ])
        
        # Special receipt endings (mentioned in interviews)
        cents = int(round(receipts * 100)) % 100
        categorical.extend([
            float(cents),  # cents portion
            1.0 if cents == 49 else 0.0,  # ends in 49
            1.0 if cents == 99 else 0.0,  # ends in 99
        ])
        
        return categorical
    
    def _extract_transformed_features(self, trip_input: TripInput) -> List[float]:
        """Extract transformed features (log, polynomial, etc.)"""
        days = trip_input.trip_duration_days
        miles = trip_input.miles_traveled
        receipts = trip_input.total_receipts_amount
        
        transformed = [
            math.log1p(days),  # log(1 + days)
            math.log1p(miles),  # log(1 + miles)
            math.log1p(receipts),  # log(1 + receipts)
        ]
        
        # Conservative polynomial features (only if enabled in config)
        if self.config.use_polynomial_features:
            if self.config.max_polynomial_degree >= 2:
                transformed.extend([
                    days ** 2,
                    miles ** 2 / 1e6,  # scaled to prevent huge values
                    receipts ** 2 / 1e6,  # scaled to prevent huge values
                ])
            
            if self.config.max_polynomial_degree >= 3:
                transformed.extend([
                    days ** 3,
                    miles ** 3 / 1e9,  # heavily scaled
                    receipts ** 3 / 1e9,  # heavily scaled
                ])
        
        return transformed
    
    def _get_feature_names(self) -> List[str]:
        """Get names for all features in order"""
        names = []
        
        # Basic features
        names.extend(['days', 'miles', 'receipts'])
        
        # Derived features
        names.extend([
            'miles_per_day', 'receipts_per_day',
            'days_miles', 'days_receipts', 'miles_receipts_scaled',
            'three_way_interaction',
            'miles_per_dollar', 'inv_receipts', 'inv_miles'
        ])
        
        # Categorical features
        names.extend([
            'is_5_days', 'is_long_trip', 'is_small_receipts', 'is_high_receipts',
            'is_optimal_efficiency',
            'receipts_50_200', 'receipts_200_500', 'receipts_500_1000',
            'mpd_lt_50', 'mpd_50_100', 'mpd_100_150', 'mpd_gte_150',
            'cents', 'ends_49', 'ends_99'
        ])
        
        # Transformed features
        names.extend(['log_days', 'log_miles', 'log_receipts'])
        
        if self.config.use_polynomial_features:
            if self.config.max_polynomial_degree >= 2:
                names.extend(['days_sq', 'miles_sq_scaled', 'receipts_sq_scaled'])
            if self.config.max_polynomial_degree >= 3:
                names.extend(['days_cube', 'miles_cube_scaled', 'receipts_cube_scaled'])
        
        return names
    
    def get_feature_importance_explanation(self, feature_importances: List[float]) -> Dict[str, float]:
        """
        Create a mapping of feature names to their importance scores.
        
        Args:
            feature_importances: List of importance scores from a trained model
            
        Returns:
            Dictionary mapping feature names to importance scores
        """
        feature_names = self._get_feature_names()
        if len(feature_importances) != len(feature_names):
            raise ValueError("Number of importances doesn't match number of features")
        
        return dict(zip(feature_names, feature_importances))