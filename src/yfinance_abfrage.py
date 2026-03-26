from apis.yfinance_api import YfinanceApi
from apis.finance_api import FinanceApi

# Konstanten
BRENT_OIL = "BZ=F"
NATURAL_GAS = "NG=F"
USD_EUR = "USDEUR=X"  # 1 USD = X EUR

# API initialisieren
api: FinanceApi = YfinanceApi()

def get_current_prices_in_eur():
    """Holt die aktuellen Kurse und rechnet sie in EUR um."""
    tickers = [BRENT_OIL, NATURAL_GAS, USD_EUR]
    
    # 1. Daten holen (gibt via yf.download einen gebündelten pandas DataFrame zurück)
    df = api.get_data(tickers, period="1d")
    
    # 2. via Index die letzte Zeile (den aktuellsten Closing Preis) extrahieren
    latest = df.iloc[-1]
    
    # 3. EUR Umrechnung: Rohstoff-Preis * Wechselkurs
    oil_eur = latest[BRENT_OIL] * latest[USD_EUR]
    gas_eur = latest[NATURAL_GAS] * latest[USD_EUR]
    
    return oil_eur, gas_eur

# der folgende Block: sorgt dafür, dass der Code darin nur läuft, wenn die Datei direkt angesprochen wird
# wird diese Datei hier lediglich importiert, wird der Block nicht ausgeführt 
# = keine unnötigen API calls & spam von Werten in die Konsole
if __name__ == "__main__":
    try:
        oil_price, gas_price = get_current_prices_in_eur()
        print(f"Aktueller Brent Öl Preis: {oil_price:.2f} EUR")
        print(f"Aktueller Gas Preis: {gas_price:.2f} EUR")
    except Exception as e:
        print(f"Fehler beim Abruf: {e}")