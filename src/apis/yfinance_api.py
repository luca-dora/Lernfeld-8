import yfinance as yf
from pandas import Series, DataFrame


class YfinanceApi:
    """Wrapper für yfinance-Api"""

    def __init__(self, period: str = "5d", interval: str = "5m"):
        """
        Initialisiert die YfinanceApi.
        
        Args:
            period: Zeitraum (z.B. "5d", "1mo")
            interval: Daten-Intervall (z.B. "5m", "1h")
        """
        self.period = period
        self.interval = interval

    def get_close_data(self, tickers: list[str]) -> Series:
        """
        Ruft Daten für eine oder mehrere Tickers ab.
        
        Args:
            tickers: Liste von Ticker-Symbolen
            
        Returns:
            Series oder DataFrame mit Close-Spalte
            
        Raises:
            ValueError: Wenn Tickerliste leer ist
            KeyError: Wenn Close-Spalte nicht in Daten vorhanden
        """
        if not tickers:
            raise ValueError("Tickerliste darf nicht leer sein")
        
        data: DataFrame = yf.download(tickers, period=self.period, interval=self.interval, progress=False)

        if "Close" not in data.columns:
            raise KeyError("'Close' Spalte nicht in yfinance-Daten gefunden")

        return data['Close']
