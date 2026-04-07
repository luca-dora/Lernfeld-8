"""Tests for the CurrencyConverter class in market_data module."""
import sys
from pathlib import Path
from unittest.mock import patch
import pandas as pd
import numpy as np
import pytest

# Add src to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from market_data import CurrencyConverter


class TestCurrencyConverter:
    """Test suite for CurrencyConverter class."""

    @patch('market_data.currency_converter.CurrencyConverter.get_exchange_rate')
    def test_convert_amount_usd_to_eur(self, mock_rate):
        """Test that convert_amount correctly converts USD to EUR."""
        mock_rate.return_value = 1.09
        
        converter = CurrencyConverter()
        result = converter.convert_amount(100, "USD", "EUR")
        assert result == pytest.approx(109.0)

    @patch('market_data.currency_converter.CurrencyConverter.get_exchange_rate')
    def test_convert_amount_zero(self, mock_rate):
        """Test that converting 0 amount returns 0."""
        mock_rate.return_value = 1.09
        
        converter = CurrencyConverter()
        result = converter.convert_amount(0, "USD", "EUR")
        assert result == 0

    @patch('market_data.currency_converter.CurrencyConverter.get_exchange_rate')
    def test_convert_amount_negative(self, mock_rate):
        """Test that negative amounts are handled."""
        mock_rate.return_value = 1.09
        
        converter = CurrencyConverter()
        result = converter.convert_amount(-50, "USD", "EUR")
        assert result == pytest.approx(-54.5)

    @patch('market_data.currency_converter.CurrencyConverter.get_exchange_rate')
    def test_convert_amount_various_rates(self, mock_rate):
        """Test conversion with various exchange rates."""
        converter = CurrencyConverter()
        
        test_cases = [
            (1.0, 100, 100.0),      # 1.0 rate: 100 USD = 100 EUR
            (1.1, 100, 110.0),      # 1.1 rate: 100 USD = 110 EUR
            (0.95, 100, 95.0),      # 0.95 rate: 100 USD = 95 EUR
            (1.5, 200, 300.0),      # 1.5 rate: 200 USD = 300 EUR
        ]
        
        for rate, usd_amount, expected_eur in test_cases:
            mock_rate.return_value = rate
            
            result = converter.convert_amount(usd_amount, "USD", "EUR")
            assert result == pytest.approx(expected_eur), \
                f"Failed for rate {rate} and USD {usd_amount}: expected {expected_eur}, got {result}"

    @patch('market_data.currency_converter.CurrencyConverter.get_exchange_rate')
    def test_get_exchange_rate_returns_float(self, mock_rate):
        """Test that get_exchange_rate returns a numeric exchange rate."""
        mock_rate.return_value = 1.09
        
        converter = CurrencyConverter()
        result = converter.get_exchange_rate("USD", "EUR")
        assert isinstance(result, (float, int, np.floating))
        assert result > 0, "Exchange rate should be positive"

    @patch('market_data.currency_converter.CurrencyConverter.get_exchange_rate')
    def test_convert_amount_with_fractional(self, mock_rate):
        """Test conversion with decimal amounts."""
        mock_rate.return_value = 1.09
        
        converter = CurrencyConverter()
        result = converter.convert_amount(99.99, "USD", "EUR")
        assert result == pytest.approx(109.98, rel=1e-2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
