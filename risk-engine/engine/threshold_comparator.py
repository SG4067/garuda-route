"""Threshold comparator for waterlogging risk determination."""

from typing import Tuple
from models.risk import RiskLevel


class ThresholdComparator:
    """Compares current continuous rainfall duration against historical road threshold.
    
    Rule:
    - NORMAL: duration < monitor_threshold
    - MONITOR: monitor_threshold <= duration < historical_threshold
    - HIGH_RISK: duration >= historical_threshold
    
    monitor_threshold is derived as:
        historical_threshold * monitor_ratio (default 0.70, or 70%)
    """

    DEFAULT_MONITOR_RATIO = 0.70

    def __init__(self, monitor_ratio: float = DEFAULT_MONITOR_RATIO):
        """Initialize comparator with configurable monitor ratio.
        
        Args:
            monitor_ratio: Float between 0.0 and 1.0 (exclusive) defining when
                           MONITOR alert triggers relative to historical threshold.
        """
        if not (0.0 < monitor_ratio < 1.0):
            raise ValueError(f"monitor_ratio must be between 0.0 and 1.0 exclusive, got {monitor_ratio}.")
        self.monitor_ratio = float(monitor_ratio)

    def evaluate(
        self,
        current_duration_minutes: float,
        historical_threshold_minutes: float,
    ) -> Tuple[RiskLevel, str]:
        """Evaluate risk level and return tuple of (RiskLevel, explanation_reason).
        
        Args:
            current_duration_minutes: Continuous rain duration in minutes.
            historical_threshold_minutes: Road vulnerability threshold in minutes.
            
        Returns:
            Tuple[RiskLevel, str]: Evaluated risk level and human-readable explanation.
            
        Raises:
            ValueError: If duration or threshold are invalid.
        """
        if current_duration_minutes is None or not isinstance(current_duration_minutes, (int, float)):
            raise ValueError(f"current_duration_minutes must be numeric, got {type(current_duration_minutes)}")

        if historical_threshold_minutes is None or not isinstance(historical_threshold_minutes, (int, float)):
            raise ValueError(f"historical_threshold_minutes must be numeric, got {type(historical_threshold_minutes)}")

        if current_duration_minutes < 0:
            raise ValueError(f"current_duration_minutes cannot be negative, got {current_duration_minutes}")

        if historical_threshold_minutes <= 0:
            raise ValueError(f"historical_threshold_minutes must be greater than 0, got {historical_threshold_minutes}")

        monitor_threshold = historical_threshold_minutes * self.monitor_ratio

        if current_duration_minutes >= historical_threshold_minutes:
            level = RiskLevel.HIGH_RISK
            reason = (
                f"Continuous rainfall duration ({current_duration_minutes:.1f}m) has reached or exceeded "
                f"historical waterlogging threshold ({historical_threshold_minutes:.1f}m). "
                f"Historically, this road segment has experienced waterlogging under these conditions."
            )
        elif current_duration_minutes >= monitor_threshold:
            level = RiskLevel.MONITOR
            reason = (
                f"Continuous rainfall duration ({current_duration_minutes:.1f}m) has exceeded early-warning "
                f"monitor threshold ({monitor_threshold:.1f}m, {self.monitor_ratio * 100:.0f}% of {historical_threshold_minutes:.1f}m). "
                f"Approaching historical waterlogging conditions."
            )
        else:
            level = RiskLevel.NORMAL
            reason = (
                f"Continuous rainfall duration ({current_duration_minutes:.1f}m) is comfortably below "
                f"monitor threshold ({monitor_threshold:.1f}m) and historical threshold ({historical_threshold_minutes:.1f}m)."
            )

        return level, reason
