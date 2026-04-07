"""CommodityPriceProvider für Rohstoffpreise."""

import pandas as pd

from .market_data_provider import MarketDataProvider
from .constants import BRENT_OIL, NATURAL_GAS


class CommodityPriceProvider(MarketDataProvider):
    """Spezialisiert auf Rohstoffpreise."""

    def __init__(self, period="1d", interval="5m"):
        super().__init__(period=period, interval=interval)

    def get_oil_price(self) -> float:
        """Gibt den aktuellen Brent Öl Preis (USD) zurück."""
        return self.get_latest_price(BRENT_OIL)

    def get_gas_price(self) -> float:
        """Gibt den aktuellen Natural Gas Preis (USD) zurück."""
        return self.get_latest_price(NATURAL_GAS)

    def get_oil_ohlc(self) -> pd.DataFrame:
        """Gibt OHLCV-Daten für Brent Öl zurück."""
        return self.get_ohlc_data(BRENT_OIL)

    def get_gas_ohlc(self) -> pd.DataFrame:
        """Gibt OHLCV-Daten für Natural Gas zurück."""
        return self.get_ohlc_data(NATURAL_GAS)

