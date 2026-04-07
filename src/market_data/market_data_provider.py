"""MarketDataProvider für Datenbeschaffung und -verarbeitung von yfinance."""

import pandas as pd
from pandas import Series
from typing import Optional

from apis.yfinance_api import YfinanceApi


class MarketDataProvider:
    """Ruft Marktdaten von der API ab, verarbeitet und normalisiert sie."""

    def __init__(self, period: str = "1d", interval: str = "5m"):
        """
        Initialisiert den Provider mit Standard-Parametern.
        
        Args:
            period: Standard-Zeitraum (z.B. "1d", "5d")
            interval: Standard-Intervall (z.B. "5m", "1h")
        """
        self.period = period
        self.interval = interval

    def _create_api_instance(self, period: Optional[str] = None, interval: Optional[str] = None) -> YfinanceApi:
        """Erzeugt eine YfinanceApi-Instanz mit den gegebenen (oder Standard-)Parametern."""
        period = period or self.period
        interval = interval or self.interval
        return YfinanceApi(period=period, interval=interval)

    def fetch_ticker_data(self, ticker: str, period: Optional[str] = None, interval: Optional[str] = None) -> Series:
        """Ruft Rohdaten für einen Ticker ab."""
        api = self._create_api_instance(period, interval)
        return api.get_data([ticker])

    def get_latest_price(self, ticker: str) -> float:
        """Gibt den aktuellsten Preis für einen Ticker zurück."""
        data = self.fetch_ticker_data(ticker)
        return float(data.iloc[-1].item())

    def _normalize_dataframe(self, raw_data) -> pd.DataFrame:
        """
        Normalisiert rohe yfinance-Daten zu einem strukturierten DataFrame.
        Behandelt verschiedene Rückgabeformate (Series, DataFrame, MultiIndex).
        """
        # Series → DataFrame
        if isinstance(raw_data, Series):
            df = raw_data.to_frame(name="Close")
        else:
            # MultiIndex-Spalten flatten: ("Close", "BZ=F") → "Close"
            if isinstance(raw_data.columns, pd.MultiIndex):
                raw_data.columns = raw_data.columns.get_level_values(0)
            df = raw_data.copy()

        # Sicherstellen, dass "Close" vorhanden ist
        if "Close" not in df.columns:
            numeric_cols = df.select_dtypes("number").columns
            if len(numeric_cols) == 0:
                raise ValueError(f"Keine numerischen Spalten in yfinance-Daten. Spalten: {list(df.columns)}")
            df = df.rename(columns={numeric_cols[0]: "Close"})

        return df

    def _remove_nan_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Entfernt NaN-Zeilen (z.B. Marktschlusspausen)."""
        df = df[["Close"]].copy()
        return df.dropna(subset=["Close"])

    def _normalize_timezone(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalisiert Zeitzone zu Europe/Berlin und entfernt tz-Info."""
        if not isinstance(df.index, pd.DatetimeIndex):
            return df

        df = df.copy()
        if pd.api.types.is_datetime64tz_dtype(df.index):
            df.index = df.index.tz_convert("Europe/Berlin").tz_localize(None)

        return df

    def _prepare_ohlc_dataframe(self, raw_data) -> pd.DataFrame:
        """Vorbereitet OHLCV-Daten: Normalisierung → NaN-Entfernung → Zeitzone."""
        df = self._normalize_dataframe(raw_data)
        df = self._remove_nan_values(df)
        
        df.index.name = "Datetime"
        df = df.reset_index()

        df["Datetime"] = pd.to_datetime(df["Datetime"])
        if pd.api.types.is_datetime64tz_dtype(df["Datetime"]):
            df["Datetime"] = df["Datetime"].dt.tz_convert("Europe/Berlin").dt.tz_localize(None)

        df = df.rename(columns={"Close": "Preis (USD)"})
        return df

    def get_ohlc_data(self, ticker: str, period: Optional[str] = None, interval: Optional[str] = None) -> pd.DataFrame:
        """Ruft OHLCV-Daten ab und bereitet sie auf."""
        raw_data = self.fetch_ticker_data(ticker, period=period, interval=interval)
        return self._prepare_ohlc_dataframe(raw_data)

    def calculate_delta_percent(self, df: pd.DataFrame, col: str) -> float:
        """Berechnet prozentuale Veränderung zwischen erstem und letztem Wert."""
        if len(df) < 2:
            return 0.0
        return float((df[col].iloc[-1] - df[col].iloc[0]) / df[col].iloc[0] * 100)

