from pandas import Series

from apis.yfinance_api import YfinanceApi

BRENT_OIL = "BZ=F"
NATURAL_GAS = "NG=F"
EUR_USD = "USDEUR=X"
api: YfinanceApi = YfinanceApi()


def get_latest_oil_price() -> float:
    oil = api.get_data([BRENT_OIL])
    return __extract_latest_from_ticker(oil)


def get_latest_gas_price() -> float:
    gas = api.get_data([NATURAL_GAS])
    return __extract_latest_from_ticker(gas)


def get_usd_eur() -> float:
    eur = api.get_data([EUR_USD])
    return __extract_latest_from_ticker(eur)


def usd_as_eur(usd: float) -> float:
    rate = get_usd_eur()
    return usd * rate


def __extract_latest_from_ticker(result: Series) -> float:
    # via Index den aktuellsten Closing Preis extrahieren
    return float(result.iloc[-1].item())


if __name__ == "__main__":
    price = usd_as_eur(get_latest_oil_price())
    print(f"Aktueller Brent Öl Preis: {price:.2f} EUR")
