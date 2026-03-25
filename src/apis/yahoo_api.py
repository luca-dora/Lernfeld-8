import http.client
import os
from dotenv import load_dotenv
from typing_extensions import override

from .finance_api import FinanceApi

RAPID_API = "apidojo-yahoo-finance-v1.p.rapidapi.com"
PATH = "/stock/v2/get-timeseries?symbol=IBM&region=US"

class YahooApi(FinanceApi):
    def __init__(self, api: str = RAPID_API):
        self.api = api

    @override
    def get_data(self, path: str):
        load_dotenv()
        conn = http.client.HTTPSConnection(self.api)

        headers = {
            'x-rapidapi-key': os.getenv("RAPIDAPI_KEY"),
            'x-rapidapi-host': RAPID_API,
            'Content-Type': "application/json"
        }

        conn.request("GET", path, headers=headers)

        res = conn.getresponse()
        data = res.read()

        return data.decode("utf-8")
