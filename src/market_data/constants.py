"""Konstanten für die yfinance-Abfrage."""

BRENT_OIL = "BZ=F"
NATURAL_GAS = "NG=F"
EUR_USD = "USDEUR=X"

TICKER_MAP: dict[str, str] = {
    "Brent Oil (BZ=F)": BRENT_OIL,
    "Natural Gas (NG=F)": NATURAL_GAS,
}

