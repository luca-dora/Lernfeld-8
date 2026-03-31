import yfinance as yf
from pandas import Series
from typing_extensions import override

from .finance_api import FinanceApi


class YfinanceApi(FinanceApi):

    @override
    def get_data(self, tickers: list[str], period: str = "5d", interval: str = "5m") -> Series:
        data = yf.download(tickers, period=period, interval=interval)

        # nur die Spalte 'Close' benötigt
        return data['Close']
