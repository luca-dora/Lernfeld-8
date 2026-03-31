import yfinance as yf
from pandas import Series


class YfinanceApi:
    def __init__(self, period: str = "5d", interval: str = "5m"):
        self.period = period
        self.interval = interval

    def get_data(self, tickers: list[str]) -> Series:
        data = yf.download(tickers, period=self.period, interval=self.interval)

        # nur die Spalte 'Close' benötigt
        return data['Close']
