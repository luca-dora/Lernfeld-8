"""Tests für MarketDataProvider."""
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from market_data.market_data_provider import MarketDataProvider


class TestMarketDataProviderDataNormalization:
    """Tests für Datenverarbeitung und Normalisierung."""

    def test_normalize_dataframe_from_series(self):
        """Test: Series wird zu DataFrame konvertiert."""
        provider = MarketDataProvider()
        series = pd.Series([1.5, 2.0, 2.5], name="Close", index=pd.date_range("2024-01-01", periods=3))
        
        result = provider._normalize_dataframe(series)
        
        assert isinstance(result, pd.DataFrame)
        assert "Close" in result.columns
        assert len(result) == 3
        assert result["Close"].iloc[0] == 1.5

    def test_normalize_dataframe_with_multiindex_columns(self):
        """Test: DataFrame mit MultiIndex-Spalten wird flattened."""
        provider = MarketDataProvider()
        
        # Erstelle DataFrame mit MultiIndex-Spalten wie yfinance
        multi_cols = pd.MultiIndex.from_tuples([("Close", "BZ=F"), ("Volume", "BZ=F")])
        df = pd.DataFrame([[100, 5000], [101, 5100]], columns=multi_cols)
        
        result = provider._normalize_dataframe(df)
        
        assert "Close" in result.columns
        assert len(result.columns) == 2
        assert result.columns[0] == "Close"

    def test_normalize_dataframe_handles_missing_close(self):
        """Test: Fehlendes 'Close' wird automatisch zu First numeric column gerenamet."""
        provider = MarketDataProvider()
        df = pd.DataFrame({"Price": [100, 101, 102]})
        
        result = provider._normalize_dataframe(df)
        
        assert "Close" in result.columns
        assert list(result["Close"]) == [100, 101, 102]

    def test_normalize_dataframe_raises_on_no_numeric_columns(self):
        """Test: Fehler wenn keine numerischen Spalten vorhanden."""
        provider = MarketDataProvider()
        df = pd.DataFrame({"Name": ["A", "B", "C"]})
        
        with pytest.raises(ValueError, match="Keine numerischen Spalten"):
            provider._normalize_dataframe(df)

    def test_remove_nan_values_removes_nulls(self):
        """Test: NaN-Zeilen werden entfernt."""
        provider = MarketDataProvider()
        df = pd.DataFrame({
            "Close": [100.0, np.nan, 102.0, np.nan, 104.0]
        })
        
        result = provider._remove_nan_values(df)
        
        assert len(result) == 3
        assert list(result["Close"]) == [100.0, 102.0, 104.0]
        assert not result["Close"].isna().any()

    def test_remove_nan_values_keeps_only_close_column(self):
        """Test: _remove_nan_values behält nur Close-Spalte."""
        provider = MarketDataProvider()
        df = pd.DataFrame({
            "Close": [100.0, 101.0],
            "Volume": [1000, 2000],
            "Open": [99.0, 100.0]
        })
        
        result = provider._remove_nan_values(df)
        
        assert list(result.columns) == ["Close"]

    def test_normalize_timezone_no_datetime_index(self):
        """Test: Non-datetime Index wird unverändert zurückgegeben."""
        provider = MarketDataProvider()
        df = pd.DataFrame({"Close": [100.0, 101.0]}, index=[0, 1])
        
        result = provider._normalize_timezone(df)
        
        pd.testing.assert_frame_equal(result, df)

    def test_normalize_timezone_removes_tz_info(self):
        """Test: Zeitzone wird zu Europe/Berlin konvertiert und tz-Info entfernt."""
        provider = MarketDataProvider()
        
        # Erstelle DataFrame mit UTC timezone
        index = pd.date_range("2024-01-01", periods=3, tz="UTC")
        df = pd.DataFrame({"Close": [100.0, 101.0, 102.0]}, index=index)
        
        result = provider._normalize_timezone(df)
        
        assert result.index.tz is None  # Timezone entfernt
        assert result.index[0].hour == 1  # UTC+1 (Winter-Zeit)

    def test_calculate_delta_percent_basic(self):
        """Test: Prozentuale Veränderung wird korrekt berechnet."""
        provider = MarketDataProvider()
        df = pd.DataFrame({
            "Price": [100.0, 105.0, 110.0]
        })
        
        delta = provider.calculate_delta_percent(df, "Price")
        
        # (110 - 100) / 100 * 100 = 10%
        assert delta == pytest.approx(10.0)

    def test_calculate_delta_percent_negative_change(self):
        """Test: Negative Veränderung wird korrekt berechnet."""
        provider = MarketDataProvider()
        df = pd.DataFrame({
            "Price": [100.0, 80.0, 60.0]
        })
        
        delta = provider.calculate_delta_percent(df, "Price")
        
        # (60 - 100) / 100 * 100 = -40%
        assert delta == pytest.approx(-40.0)

    def test_calculate_delta_percent_empty_dataframe(self):
        """Test: Leerer oder zu kurzer DataFrame gibt 0 zurück."""
        provider = MarketDataProvider()
        df = pd.DataFrame({"Price": [100.0]})
        
        delta = provider.calculate_delta_percent(df, "Price")
        
        assert delta == 0.0

    def test_calculate_delta_percent_same_values(self):
        """Test: Gleiche First und Last Wert geben 0% zurück."""
        provider = MarketDataProvider()
        df = pd.DataFrame({
            "Price": [100.0, 100.0, 100.0]
        })
        
        delta = provider.calculate_delta_percent(df, "Price")
        
        assert delta == 0.0


class TestMarketDataProviderInitialization:
    """Tests für Initialisierung und Konfiguration."""

    def test_initialization_with_defaults(self):
        """Test: Default-Parameter werden gesetzt."""
        provider = MarketDataProvider()
        
        assert provider.period == "1d"
        assert provider.interval == "5m"

    def test_initialization_with_custom_params(self):
        """Test: Benutzerdefinierte Parameter werden gesetzt."""
        provider = MarketDataProvider(period="5d", interval="1h")
        
        assert provider.period == "5d"
        assert provider.interval == "1h"

    @patch('market_data.market_data_provider.YfinanceApi')
    def test_create_api_instance_uses_provider_defaults(self, mock_api_class):
        """Test: API-Instanz nutzt Provider-Defaults wenn nicht überschrieben."""
        provider = MarketDataProvider(period="3d", interval="15m")
        
        provider._create_api_instance()
        
        mock_api_class.assert_called_once_with(period="3d", interval="15m")

    @patch('market_data.market_data_provider.YfinanceApi')
    def test_create_api_instance_with_override(self, mock_api_class):
        """Test: Überschreibungs-Parameter werden verwendet."""
        provider = MarketDataProvider(period="1d", interval="5m")
        
        provider._create_api_instance(period="7d", interval="1d")
        
        mock_api_class.assert_called_once_with(period="7d", interval="1d")


class TestMarketDataProviderWithMockedAPI:
    """Tests mit gemockter API."""

    @patch('market_data.market_data_provider.YfinanceApi')
    def test_fetch_ticker_data_returns_series(self, mock_api_class):
        """Test: fetch_ticker_data gibt eine Series zurück."""
        mock_api = MagicMock()
        mock_series = pd.Series([100.0, 101.0, 102.0])
        mock_api.get_data.return_value = mock_series
        mock_api_class.return_value = mock_api
        
        provider = MarketDataProvider()
        result = provider.fetch_ticker_data("BZ=F")
        
        assert isinstance(result, pd.Series)
        mock_api.get_data.assert_called_once_with(["BZ=F"])

    @patch('market_data.market_data_provider.YfinanceApi')
    def test_get_latest_price_extracts_last_value(self, mock_api_class):
        """Test: get_latest_price gibt den letzten Wert zurück."""
        mock_api = MagicMock()
        mock_series = pd.Series([100.0, 101.0, 102.5])
        mock_api.get_data.return_value = mock_series
        mock_api_class.return_value = mock_api
        
        provider = MarketDataProvider()
        price = provider.get_latest_price("BZ=F")
        
        assert price == pytest.approx(102.5)

    @patch('market_data.market_data_provider.YfinanceApi')
    def test_get_ohlc_data_returns_prepared_dataframe(self, mock_api_class):
        """Test: get_ohlc_data gibt präparierten DataFrame zurück."""
        mock_api = MagicMock()
        
        # Simuliere Series von yfinance
        index = pd.date_range("2024-01-01", periods=3, tz="UTC")
        mock_series = pd.Series([100.0, 101.0, 102.0], index=index)
        mock_api.get_data.return_value = mock_series
        mock_api_class.return_value = mock_api
        
        provider = MarketDataProvider()
        result = provider.get_ohlc_data("BZ=F")
        
        assert isinstance(result, pd.DataFrame)
        assert "Datetime" in result.columns
        assert "Preis (USD)" in result.columns
        assert len(result) == 3

    @patch('market_data.market_data_provider.YfinanceApi')
    def test_get_ohlc_data_with_custom_period(self, mock_api_class):
        """Test: get_ohlc_data respektiert custom period/interval."""
        mock_api = MagicMock()
        mock_series = pd.Series([100.0])
        mock_api.get_data.return_value = mock_series
        mock_api_class.return_value = mock_api
        
        provider = MarketDataProvider()
        provider.get_ohlc_data("BZ=F", period="1mo", interval="1d")
        
        # Überprüfe, dass API mit benutzerdefinierten Parametern erstellt wurde
        assert mock_api_class.call_args[1]["period"] == "1mo"
        assert mock_api_class.call_args[1]["interval"] == "1d"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

