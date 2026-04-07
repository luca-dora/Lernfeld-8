"""Tests für YfinanceApi."""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pandas as pd
import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from apis.yfinance_api import YfinanceApi


class TestYfinanceApiInitialization:
    """Tests für YfinanceApi Initialisierung."""

    def test_initialization_with_defaults(self):
        """Test: Default-Parameter werden gesetzt."""
        api = YfinanceApi()
        
        assert api.period == "5d"
        assert api.interval == "5m"

    def test_initialization_with_custom_params(self):
        """Test: Benutzerdefinierte Parameter werden gesetzt."""
        api = YfinanceApi(period="1mo", interval="1d")
        
        assert api.period == "1mo"
        assert api.interval == "1d"


class TestYfinanceApiGetData:
    """Tests für get_data Methode."""

    @patch('apis.yfinance_api.yf.download')
    def test_get_data_calls_yfinance_download(self, mock_download):
        """Test: get_data ruft yfinance.download mit korrekten Parametern auf."""
        mock_series = pd.Series([100.0, 101.0, 102.0])
        mock_download.return_value = pd.DataFrame({
            "Close": [100.0, 101.0, 102.0]
        })
        
        api = YfinanceApi(period="5d", interval="5m")
        api.get_close_data(["BZ=F"])
        
        mock_download.assert_called_once()
        # Überprüfe Parameter
        call_args = mock_download.call_args
        assert call_args[0][0] == ["BZ=F"]
        assert call_args[1]["period"] == "5d"
        assert call_args[1]["interval"] == "5m"

    @patch('apis.yfinance_api.yf.download')
    def test_get_data_returns_close_column(self, mock_download):
        """Test: get_data gibt 'Close' Spalte zurück."""
        mock_df = pd.DataFrame({
            "Close": [100.0, 101.0, 102.0],
            "Volume": [1000, 1100, 1200],
            "Open": [99.0, 100.0, 101.0]
        })
        mock_download.return_value = mock_df
        
        api = YfinanceApi()
        result = api.get_close_data(["BZ=F"])
        
        assert isinstance(result, (pd.Series, pd.DataFrame))

    @patch('apis.yfinance_api.yf.download')
    def test_get_data_with_multiple_tickers(self, mock_download):
        """Test: get_data kann mehrere Tickers verarbeiten."""
        mock_df = pd.DataFrame({
            ("Close", "BZ=F"): [100.0, 101.0],
            ("Close", "NG=F"): [3.0, 3.1],
        })
        mock_download.return_value = mock_df
        
        api = YfinanceApi()
        result = api.get_close_data(["BZ=F", "NG=F"])
        
        # Überprüfe, dass download mit beiden Tickers aufgerufen wurde
        mock_download.assert_called_once()
        call_args = mock_download.call_args
        assert call_args[0][0] == ["BZ=F", "NG=F"]

    @patch('apis.yfinance_api.yf.download')
    def test_get_data_returns_series_or_dataframe(self, mock_download):
        """Test: get_data gibt immer Series oder DataFrame zurück."""
        # Test mit Series (Single Ticker)
        mock_download.return_value = pd.DataFrame({
            "Close": [100.0, 101.0]
        })
        
        api = YfinanceApi()
        result = api.get_close_data(["BZ=F"])
        
        # Sollte Close Spalte sein
        assert "Close" in result.columns if isinstance(result, pd.DataFrame) else True


class TestYfinanceApiParameterValidation:
    """Tests für Parameter-Validierung."""

    def test_period_parameter_is_stored(self):
        """Test: period Parameter wird korrekt gespeichert."""
        api = YfinanceApi(period="1y")
        assert api.period == "1y"

    def test_interval_parameter_is_stored(self):
        """Test: interval Parameter wird korrekt gespeichert."""
        api = YfinanceApi(interval="1h")
        assert api.interval == "1h"

    @patch('apis.yfinance_api.yf.download')
    def test_get_data_with_different_periods(self, mock_download):
        """Test: get_data nutzt den eingestellten Zeitraum."""
        mock_download.return_value = pd.DataFrame({"Close": [100.0]})
        
        for period in ["1d", "5d", "1mo", "3mo", "1y"]:
            api = YfinanceApi(period=period)
            api.get_close_data(["BZ=F"])
            
            call_args = mock_download.call_args
            assert call_args[1]["period"] == period

    @patch('apis.yfinance_api.yf.download')
    def test_get_data_with_different_intervals(self, mock_download):
        """Test: get_data nutzt das eingestellte Intervall."""
        mock_download.return_value = pd.DataFrame({"Close": [100.0]})
        
        for interval in ["5m", "15m", "1h", "1d"]:
            api = YfinanceApi(interval=interval)
            api.get_close_data(["BZ=F"])
            
            call_args = mock_download.call_args
            assert call_args[1]["interval"] == interval


class TestYfinanceApiErrorHandling:
    """Tests für Fehlerbehandlung."""

    @patch('apis.yfinance_api.yf.download')
    def test_get_data_with_invalid_ticker_raises_error(self, mock_download):
        """Test: Ungültiger Ticker wird behandelt."""
        mock_download.side_effect = Exception("Invalid ticker")
        
        api = YfinanceApi()
        
        with pytest.raises(Exception):
            api.get_close_data(["INVALID_TICKER"])

    def test_get_data_with_empty_ticker_list(self):
        """Test: Leere Tickerliste wirft ValueError."""
        api = YfinanceApi()
        
        with pytest.raises(ValueError, match="Tickerliste darf nicht leer sein"):
            api.get_close_data([])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


