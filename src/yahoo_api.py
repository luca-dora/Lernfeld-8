import http.client
import os
from dotenv import load_dotenv

load_dotenv()

conn = http.client.HTTPSConnection("apidojo-yahoo-finance-v1.p.rapidapi.com")

headers = {
    'x-rapidapi-key': os.getenv("RAPIDAPI_KEY"),
    'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com",
    'Content-Type': "application/json"
}

conn.request("GET", "/stock/v2/get-timeseries?symbol=IBM&region=US", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))