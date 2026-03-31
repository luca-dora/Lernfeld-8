"""Tests for the usd_as_eur function in yfinance_abfrage module."""
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
import pytest
import yfinance

# Add src to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from yfinance_abfrage import usd_as_eur, get_usd_eur


class TestUsdAsEur:
    """Test suite for USD to EUR conversion function."""

    @patch('yfinance_abfrage.api.get_data')
    def test_usd_as_eur_conversion(self, mock_get_data):
        """Test that usd_as_eur correctly converts USD to EUR using the exchange rate."""
        # Setup mock to return a Series with Close prices (as api.get_data() actually does)
        mock_series = pd.Series([1.09])
        
        mock_get_data.return_value = mock_series
        
        # Test conversion: 100 USD at 1.09 EUR/USD = 109 EUR
        result = usd_as_eur(100)
        assert result == pytest.approx(109.0)

    @patch('yfinance_abfrage.api.get_data')
    def test_usd_as_eur_zero_usd(self, mock_get_data):
        """Test that converting 0 USD returns 0 EUR."""
        mock_series = pd.Series([1.09])
        mock_get_data.return_value = mock_series
        
        result = usd_as_eur(0)
        assert result == 0

    @patch('yfinance_abfrage.api.get_data')
    def test_usd_as_eur_negative_usd(self, mock_get_data):
        """Test that negative USD values are handled (for consistency)."""
        mock_series = pd.Series([1.09])
        mock_get_data.return_value = mock_series
        
        # Test with negative value
        result = usd_as_eur(-50)
        assert result == pytest.approx(-54.5)

    @patch('yfinance_abfrage.api.get_data')
    def test_usd_as_eur_various_rates(self, mock_get_data):
        """Test conversion with various exchange rates."""
        test_cases = [
            (1.0, 100, 100.0),      # 1.0 rate: 100 USD = 100 EUR
            (1.1, 100, 110.0),      # 1.1 rate: 100 USD = 110 EUR
            (0.95, 100, 95.0),      # 0.95 rate: 100 USD = 95 EUR
            (1.5, 200, 300.0),      # 1.5 rate: 200 USD = 300 EUR
        ]
        
        for rate, usd_amount, expected_eur in test_cases:
            mock_series = pd.Series([rate])
            mock_get_data.return_value = mock_series
            
            result = usd_as_eur(usd_amount)
            assert result == pytest.approx(expected_eur), \
                f"Failed for rate {rate} and USD {usd_amount}: expected {expected_eur}, got {result}"

    @patch('yfinance_abfrage.api.get_data')
    def test_get_usd_eur_returns_float(self, mock_get_data):
        """Test that get_usd_eur returns a numeric exchange rate."""
        mock_series = pd.Series([1.09])
        mock_get_data.return_value = mock_series
        
        result = get_usd_eur()
        assert isinstance(result, (float, int, np.floating))
        assert result > 0, "Exchange rate should be positive"

    @patch('yfinance_abfrage.api.get_data')
    def test_usd_as_eur_with_fractional_amounts(self, mock_get_data):
        """Test conversion with decimal USD amounts."""
        mock_series = pd.Series([1.09])
        mock_get_data.return_value = mock_series
        
        result = usd_as_eur(99.99)
        assert result == pytest.approx(109.98, rel=1e-2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
