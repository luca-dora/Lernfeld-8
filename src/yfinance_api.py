import yfinance as yf

class YfinanceApi:
    def __init__(self, ticker):
        self.ticker = ticker

    def call_api(self):
        rs = yf.Ticker(self.ticker)
        return rs
