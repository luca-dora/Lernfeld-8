# Abfrage über yfinance library
# Vorteil 1: müssen keinen API key managen, was später zu Nervkram mit der build pipeline führen kann
# Vorteil 2: wir bekommen direkt "dataframes", die sich einfach mit pandas verarbeiten lassen, statt mühsam Daten via json zu parsen
import yfinance

from apis import yfinance_api as yf_api
from apis.finance_api import FinanceApi

BRENT_OIL = "BZ=F"
api: FinanceApi = yf_api.YfinanceApi()

def get_oil_price():
    # Holt die Daten für Brent Oil
    oil = api.get_data(BRENT_OIL)

    # TODO noch zu klären ob es einen Zweck gibt die andere Impl zu nutzen
    if not isinstance(oil, yfinance.Ticker):
        raise TypeError("Momentan nur für yFinance implementiert")

    # Holt den neuesten Kurs (1 Tag Historie)
    data = oil.history(period="1d")
    # bis einschließlich des gestrigen closing Kurses (-1)
    return data['Close'].iloc[-1]

if __name__ == "__main__":
    try:
        price = get_oil_price()
        print(f"Aktueller Brent Öl Preis: {price:.2f} USD")
    except Exception as e:
        print(f"Fehler beim Abruf: {e}")