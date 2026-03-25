import yfinance as yf
from typing_extensions import override

from .finance_api import FinanceApi


class YfinanceApi(FinanceApi):

    @override
    def get_data(self, ticker: str):
        rs = yf.Ticker(ticker)
        return rs
