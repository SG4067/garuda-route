"""Unit tests for ThresholdComparator."""

import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.threshold_comparator import ThresholdComparator
from models.risk import RiskLevel


class TestThresholdComparator(unittest.TestCase):
    """Test suite covering threshold comparison logic and edge cases."""

    def setUp(self):
        # 70% monitor ratio: for 60 min threshold -> monitor at 42.0 min
        self.comparator = ThresholdComparator(monitor_ratio=0.70)
        self.threshold = 60.0

    def test_10_clearly_normal(self):
        """10. Duration well below monitor threshold (20m < 42m) evaluates to NORMAL."""
        level, reason = self.comparator.evaluate(
            current_duration_minutes=20.0,
            historical_threshold_minutes=self.threshold,
        )
        self.assertEqual(level, RiskLevel.NORMAL)
        self.assertIn("comfortably below", reason)

    def test_11_monitor(self):
        """11. Duration between monitor and historical threshold (45m) evaluates to MONITOR."""
        level, reason = self.comparator.evaluate(
            current_duration_minutes=45.0,
            historical_threshold_minutes=self.threshold,
        )
        self.assertEqual(level, RiskLevel.MONITOR)
        self.assertIn("early-warning monitor threshold", reason)

    def test_12_exactly_at_threshold(self):
        """12. Duration exactly at historical threshold (60m) evaluates to HIGH_RISK."""
        level, reason = self.comparator.evaluate(
            current_duration_minutes=60.0,
            historical_threshold_minutes=self.threshold,
        )
        self.assertEqual(level, RiskLevel.HIGH_RISK)
        self.assertIn("reached or exceeded", reason)

    def test_13_above_threshold(self):
        """13. Duration exceeding threshold (75m > 60m) evaluates to HIGH_RISK."""
        level, reason = self.comparator.evaluate(
            current_duration_minutes=75.0,
            historical_threshold_minutes=self.threshold,
        )
        self.assertEqual(level, RiskLevel.HIGH_RISK)
        self.assertIn("reached or exceeded", reason)

    def test_14_missing_or_invalid_threshold(self):
        """14. Missing or invalid threshold (<= 0 or None) raises ValueError."""
        with self.assertRaises(ValueError):
            self.comparator.evaluate(30.0, None)

        with self.assertRaises(ValueError):
            self.comparator.evaluate(30.0, 0)

        with self.assertRaises(ValueError):
            self.comparator.evaluate(30.0, -10.0)

    def test_negative_duration_raises_error(self):
        """Negative continuous duration is rejected with ValueError."""
        with self.assertRaises(ValueError):
            self.comparator.evaluate(-5.0, self.threshold)

    def test_invalid_monitor_ratio(self):
        """Invalid monitor ratio out of range (0, 1) raises ValueError."""
        with self.assertRaises(ValueError):
            ThresholdComparator(monitor_ratio=1.5)
        with self.assertRaises(ValueError):
            ThresholdComparator(monitor_ratio=0.0)


if __name__ == "__main__":
    unittest.main()
