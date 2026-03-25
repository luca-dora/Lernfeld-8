# Abfrage über yfinance library
# Vorteil 1: müssen keinen API key managen, was später zu Nervkram mit der build pipeline führen kann
# Vorteil 2: wir bekommen direkt "dataframes", die sich einfach mit pandas verarbeiten lassen, statt mühsam Daten via json zu parsen
import yfinance

from apis import yfinance_api as yf_api
from apis.finance_api import FinanceApi

BRENT_OIL = "BZ=F"
NATURAL_GAS = "NG=F"
EUR_USD = "USDEUR=X"
api: FinanceApi = yf_api.YfinanceApi()

def get_oil_price():
    oil = api.get_data(BRENT_OIL)
    return __extract_last_from_ticker(oil)

def get_gas_price():
    gas = api.get_data(NATURAL_GAS)
    return __extract_last_from_ticker(gas)

def get_usd_eur():
    eur = api.get_data(EUR_USD)
    return __extract_last_from_ticker(eur)

def usd_as_eur(usd: float):
    rate = get_usd_eur()
    return usd * rate

def __check_is_ticker__(result):
    # TODO noch zu klären ob es einen Zweck gibt die andere Impl zu nutzen
    if not isinstance(result, yfinance.Ticker):
        raise TypeError("Momentan nur für yFinance implementiert")

def __extract_last_from_ticker(result):
    __check_is_ticker__(result)

    # Holt den neuesten Kurs (1 Tag Historie)
    data = result.history(period="1d")
    # bis einschließlich des gestrigen closing Kurses (-1)
    return data['Close'].iloc[-1]

if __name__ == "__main__":
    try:
        price = usd_as_eur(get_oil_price())
        print(f"Aktueller Brent Öl Preis: {price:.2f} USD")
    except Exception as e:
        print(f"Fehler beim Abruf: {e}")