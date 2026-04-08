"""CurrencyConverter für Währungskonvertierung."""

import pandas as pd

from .market_data_provider import MarketDataProvider


class CurrencyConverter(MarketDataProvider):
    """Spezialisiert auf Währungskonvertierung."""

    def __init__(self):
        super().__init__(period="1d", interval="5m")

    def get_exchange_rate(self, source: str = "USD", target: str = "EUR") -> float:
        """
        Gibt den Wechselkurs zurück (Standard: USD→EUR).
        
        Args:
            source: Quellwährung (Standard: "USD")
            target: Zielwährung (Standard: "EUR")
        
        Returns:
            Wechselkurs
        """
        ticker: str = f"{source}{target}=X"
        return self.get_latest_price(ticker)

    def convert_amount(self, amount: float, source: str = "USD", target: str = "EUR") -> float:
        """
        Konvertiert einen Betrag von einer Währung in eine andere.
        
        Args:
            amount: Zu konvertierender Betrag
            source: Quellwährung (Standard: "USD")
            target: Zielwährung (Standard: "EUR")
        
        Returns:
            Konvertierter Betrag
        """
        rate = self.get_exchange_rate(source, target)
        return amount * rate

    def add_target_currency(self, df: pd.DataFrame, source_col: str = "Preis (USD)", 
                          source: str = "USD", target: str = "EUR") -> pd.DataFrame:
        """
        Fügt eine Spalte mit konvertierter Währung hinzu.
        
        Args:
            df: DataFrame mit Quellwährung-Spalte
            source_col: Name der Quellwährung-Spalte
            source: Quellwährung
            target: Zielwährung
        
        Returns:
            DataFrame mit zusätzlicher Spalte für Zielwährung
        """
        df = df.copy()
        rate = self.get_exchange_rate(source, target)
        target_col = f"Preis ({target})"
        df[target_col] = df[source_col] * rate
        return df

