"""Tests für CommodityPriceProvider."""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pandas as pd
import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from market_data import CommodityPriceProvider
from market_data.constants import BRENT_OIL, NATURAL_GAS


class TestCommodityPriceProviderInitialization:
    """Tests für Initialisierung von CommodityPriceProvider."""

    def test_inherits_from_market_data_provider(self):
        """Test: CommodityPriceProvider erbt von MarketDataProvider."""
        from market_data import MarketDataProvider
        provider = CommodityPriceProvider()
        
        assert isinstance(provider, MarketDataProvider)


class TestCommodityPriceProviderMethods:
    """Tests für Commodity-Preis-Methoden."""

    @patch('market_data.market_data_provider.YfinanceApi')
    def test_get_oil_price_returns_float(self, mock_api_class):
        """Test: get_oil_price gibt float zurück."""
        mock_api = MagicMock()
        mock_series = pd.Series([100.5])
        mock_api.get_close_data.return_value = mock_series
        mock_api_class.return_value = mock_api
        
        provider = CommodityPriceProvider()
        price = provider.get_oil_price()
        
        assert isinstance(price, float)
        assert price == pytest.approx(100.5)

    @patch('market_data.market_data_provider.YfinanceApi')
    def test_get_oil_price_uses_brent_ticker(self, mock_api_class):
        """Test: get_oil_price nutzt BRENT_OIL ticker."""
        mock_api = MagicMock()
        mock_series = pd.Series([100.0])
        mock_api.get_close_data.return_value = mock_series
        mock_api_class.return_value = mock_api
        
        provider = CommodityPriceProvider()
        provider.get_oil_price()
        
        # Überprüfe, dass BRENT_OIL ticker verwendet wurde
        mock_api.get_close_data.assert_called_with([BRENT_OIL])

    @patch('market_data.market_data_provider.YfinanceApi')
    def test_get_gas_price_returns_float(self, mock_api_class):
        """Test: get_gas_price gibt float zurück."""
        mock_api = MagicMock()
        mock_series = pd.Series([3.5])
        mock_api.get_close_data.return_value = mock_series
        mock_api_class.return_value = mock_api
        
        provider = CommodityPriceProvider()
        price = provider.get_gas_price()
        
        assert isinstance(price, float)
        assert price == pytest.approx(3.5)

    @patch('market_data.market_data_provider.YfinanceApi')
    def test_get_gas_price_uses_natural_gas_ticker(self, mock_api_class):
        """Test: get_gas_price nutzt NATURAL_GAS ticker."""
        mock_api = MagicMock()
        mock_series = pd.Series([3.0])
        mock_api.get_close_data.return_value = mock_series
        mock_api_class.return_value = mock_api
        
        provider = CommodityPriceProvider()
        provider.get_gas_price()
        
        # Überprüfe, dass NATURAL_GAS ticker verwendet wurde
        mock_api.get_close_data.assert_called_with([NATURAL_GAS])

    @patch('market_data.market_data_provider.YfinanceApi')
    def test_get_oil_ohlc_returns_dataframe(self, mock_api_class):
        """Test: get_oil_ohlc gibt DataFrame zurück."""
        mock_api = MagicMock()
        index = pd.date_range("2024-01-01", periods=2, tz="UTC")
        mock_series = pd.Series([100.0, 101.0], index=index)
        mock_api.get_close_data.return_value = mock_series
        mock_api_class.return_value = mock_api
        
        provider = CommodityPriceProvider(period="5d")
        result = provider.get_oil_ohlc()
        
        assert isinstance(result, pd.DataFrame)
        assert "Datetime" in result.columns
        assert "Preis (USD)" in result.columns

    @patch('market_data.market_data_provider.YfinanceApi')
    def test_get_oil_ohlc_uses_brent_ticker(self, mock_api_class):
        """Test: get_oil_ohlc nutzt BRENT_OIL ticker."""
        mock_api = MagicMock()
        index = pd.date_range("2024-01-01", periods=1, tz="UTC")
        mock_series = pd.Series([100.0], index=index)
        mock_api.get_close_data.return_value = mock_series
        mock_api_class.return_value = mock_api
        
        provider = CommodityPriceProvider()
        provider.get_oil_ohlc()
        
        # Überprüfe, dass BRENT_OIL ticker verwendet wurde
        mock_api.get_close_data.assert_called_with([BRENT_OIL])

    @patch('market_data.market_data_provider.YfinanceApi')
    def test_get_gas_ohlc_returns_dataframe(self, mock_api_class):
        """Test: get_gas_ohlc gibt DataFrame zurück."""
        mock_api = MagicMock()
        index = pd.date_range("2024-01-01", periods=2, tz="UTC")
        mock_series = pd.Series([3.0, 3.1], index=index)
        mock_api.get_close_data.return_value = mock_series
        mock_api_class.return_value = mock_api
        
        provider = CommodityPriceProvider(period="1mo")
        result = provider.get_gas_ohlc()
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

    @patch('market_data.market_data_provider.YfinanceApi')
    def test_get_gas_ohlc_uses_natural_gas_ticker(self, mock_api_class):
        """Test: get_gas_ohlc nutzt NATURAL_GAS ticker."""
        mock_api = MagicMock()
        index = pd.date_range("2024-01-01", periods=1, tz="UTC")
        mock_series = pd.Series([3.0], index=index)
        mock_api.get_close_data.return_value = mock_series
        mock_api_class.return_value = mock_api
        
        provider = CommodityPriceProvider()
        provider.get_gas_ohlc()
        
        # Überprüfe, dass NATURAL_GAS ticker verwendet wurde
        mock_api.get_close_data.assert_called_with([NATURAL_GAS])


class TestCommodityPriceProviderIntegration:
    """Integrationstests mit mehreren Methoden."""

    @patch('market_data.market_data_provider.YfinanceApi')
    def test_both_prices_can_be_fetched(self, mock_api_class):
        """Test: Beide Preise können nacheinander abgerufen werden."""
        mock_api = MagicMock()
        oil_series = pd.Series([100.0])
        gas_series = pd.Series([3.0])
        
        # Verschiedene Rückgabewerte für verschiedene Aufrufe
        mock_api.get_close_data.side_effect = [oil_series, gas_series]
        mock_api_class.return_value = mock_api
        
        provider = CommodityPriceProvider()
        oil_price = provider.get_oil_price()
        gas_price = provider.get_gas_price()
        
        assert oil_price == pytest.approx(100.0)
        assert gas_price == pytest.approx(3.0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

