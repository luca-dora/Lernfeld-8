import yfinance as yf
import pandas as pd
from typing_extensions import override

from .finance_api import FinanceApi

class YfinanceApi(FinanceApi):

    @override
    def get_data(self, tickers: list[str], period: str = "5d") -> pd.DataFrame:
        # yf.download holt alle Ticker gleichzeitig als Tabelle
        # interval="5m" gibt uns wie gewollt Datenpunkte alle 5 Minuten
        data = yf.download(tickers, period=period, interval="5m")
        
        # Wir brauchen für einen Liniengraphen nur die Spalte "Close" = der finale Preis eines 5m Intervalls
        return data['Close']
    

# Abfrage über yfinance library
# Vorteil 1: müssen keinen API key managen, was später zu Nervkram mit der build pipeline führen kann
# Vorteil 2: wir bekommen direkt "dataframes", die sich einfach mit pandas verarbeiten lassen, statt mühsam Daten via json zu parsen