import http.client
import os
from dotenv import load_dotenv

RAPID_API = "apidojo-yahoo-finance-v1.p.rapidapi.com"
PATH = "/stock/v2/get-timeseries?symbol=IBM&region=US"

class Yahoo_Api:

    def __init__(self, path, api=RAPID_API):
        self.api = api
        self.path = path

    def callApi(self):
        load_dotenv()
        conn = http.client.HTTPSConnection(self.api)

        headers = {
            'x-rapidapi-key': os.getenv("RAPIDAPI_KEY"),
            'x-rapidapi-host': RAPID_API,
            'Content-Type': "application/json"
        }

        conn.request("GET", self.path, headers=headers)

        res = conn.getresponse()
        data = res.read()

        print(data.decode("utf-8"))


Yahoo_Api(PATH).callApi()