"""
Rohstoff-Dashboard – Streamlit UI
Zeigt aktuelle Brent-Öl und Erdgas-Preise mit historischem Kursverlauf.
Nutzt die bestehenden yfinance-Schnittstellen aus src/.
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ─── Pfad zu src/ hinzufügen ───────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent / "src"))

from apis.yfinance_api import YfinanceApi

# ─── Ticker-Konstanten ─────────────────────────────────────────────────────
TICKER_MAP: dict[str, str] = {
    "Brent Oil (BZ=F)": "BZ=F",
    "Natural Gas (NG=F)": "NG=F",
}

CURRENCY_TICKER = "USDEUR=X"

# Farbpalette
COLOR_PRIMARY = "#E8A838"   # Goldorange – Energie / Rohstoffe
COLOR_ACCENT  = "#E05C2A"   # Terrakotta
COLOR_BG      = "#0E1117"   # Streamlit dark default
COLOR_SURFACE = "#1C2130"
COLOR_TEXT    = "#F0EDE8"
COLOR_MUTED   = "#6B7280"


# ─── Hilfsfunktionen ────────────────────────────────────────────────────────

@st.cache_data(ttl=300)   # 5 Min. Cache, dann neuer API-Call
def fetch_ohlc(ticker: str, period: str = "5d", interval: str = "5m") -> pd.DataFrame:
    """Ruft OHLCV-Daten via yfinance ab und bereitet sie für Plotly auf."""
    api = YfinanceApi(period=period, interval=interval)
    raw = api.get_data([ticker])

    # yfinance liefert je nach Version einen Series oder DataFrame mit ggf. MultiIndex
    if isinstance(raw, pd.DataFrame):
        # MultiIndex-Spalten flatten: ("Close", "BZ=F") → "Close"
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)
        df = raw.copy()
    else:
        # Series → DataFrame
        df = raw.to_frame(name="Close")

    # Sicherstellen, dass "Close" vorhanden ist; sonst erste numerische Spalte nehmen
    if "Close" not in df.columns:
        numeric_cols = df.select_dtypes("number").columns
        if len(numeric_cols) == 0:
            raise ValueError(f"Keine numerischen Spalten in den yfinance-Daten für {ticker}. Spalten: {list(df.columns)}")
        df = df.rename(columns={numeric_cols[0]: "Close"})

    # NaN-Zeilen entfernen (Marktschlusspausen) – BEVOR wir umbenennen
    df = df[["Close"]].copy()
    df = df.dropna(subset=["Close"])

    df.index.name = "Datetime"
    df = df.reset_index()

    # Zeitzone entfernen (Plotly mag tz-naive Timestamps lieber)
    if pd.api.types.is_datetime64tz_dtype(df["Datetime"]):
        df["Datetime"] = df["Datetime"].dt.tz_convert("Europe/Berlin").dt.tz_localize(None)

    # Umbenennen erst NACH dropna
    df = df.rename(columns={"Close": "Preis (USD)"})
    return df


@st.cache_data(ttl=300)
def fetch_eur_rate() -> float:
    """Gibt den aktuellen USD→EUR Kurs zurück."""
    api = YfinanceApi(period="1d", interval="5m")
    series = api.get_data([CURRENCY_TICKER])
    if isinstance(series, pd.DataFrame):
        return float(series.iloc[-1].item())
    return float(series.iloc[-1])


def usd_to_eur(df: pd.DataFrame, rate: float) -> pd.DataFrame:
    """Fügt eine EUR-Preisspalte hinzu."""
    df = df.copy()
    df["Preis (EUR)"] = df["Preis (USD)"] * rate
    return df


def build_chart(
    df: pd.DataFrame,
    label: str,
    currency: str,
    color: str = COLOR_PRIMARY,
) -> go.Figure:
    """Erstellt einen Plotly-Line-Chart mit Bereichsfüllung."""
    price_col = f"Preis ({currency})"

    fig = go.Figure()

    # Bereichsfüllung (Gradient-Effekt)
    fig.add_trace(
        go.Scatter(
            x=df["Datetime"],
            y=df[price_col],
            mode="lines",
            name=label,
            line=dict(color=color, width=2),
            fill="tozeroy",
            fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.12)",
            hovertemplate=(
                "<b>%{x|%d.%m.%Y %H:%M}</b><br>"
                f"{price_col}: %{{y:.2f}}<extra></extra>"
            ),
        )
    )

    # Aktuellen Preis als Marker hervorheben
    latest = df.iloc[-1]
    fig.add_trace(
        go.Scatter(
            x=[latest["Datetime"]],
            y=[latest[price_col]],
            mode="markers",
            marker=dict(color=COLOR_ACCENT, size=10, symbol="circle"),
            name="Aktuell",
            hovertemplate=(
                f"<b>Aktuell</b><br>{price_col}: %{{y:.2f}}<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=COLOR_SURFACE,
        plot_bgcolor=COLOR_SURFACE,
        font=dict(family="'IBM Plex Mono', monospace", color=COLOR_TEXT, size=12),
        title=dict(
            text=f"<b>{label}</b> — letzte 5 Tage (5-min-Intervall)",
            font=dict(size=16, color=COLOR_PRIMARY),
            x=0.02,
        ),
        xaxis=dict(
            title="Datum / Uhrzeit (Berlin)",
            gridcolor="#2A3040",
            linecolor="#2A3040",
            tickformat="%d.%m %H:%M",
        ),
        yaxis=dict(
            title=f"Preis ({currency})",
            gridcolor="#2A3040",
            linecolor="#2A3040",
        ),
        legend=dict(orientation="h", y=-0.18),
        margin=dict(l=10, r=10, t=50, b=10),
        height=420,
    )
    return fig


def delta_percent(df: pd.DataFrame, col: str) -> float:
    """Prozentuale Veränderung: letzter vs. erster Wert im DataFrame."""
    if len(df) < 2:
        return 0.0
    return float((df[col].iloc[-1] - df[col].iloc[0]) / df[col].iloc[0] * 100)


# ─── Seiten-Layout ─────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Rohstoff-Dashboard",
    page_icon="⛽",
    layout="wide",
)

# Globales CSS-Overlay (Schriftart + feine Retouchen)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;500;700&display=swap');

    html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }

    /* Sidebar-Header */
    section[data-testid="stSidebar"] h1 {
        font-family: 'IBM Plex Mono', monospace;
        color: #E8A838;
        font-size: 1.1rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    /* Metriken */
    [data-testid="stMetricValue"] {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 2rem !important;
        color: #E8A838 !important;
    }
    [data-testid="stMetricDelta"] { font-size: 0.9rem !important; }

    /* Trennlinie */
    hr { border-color: #2A3040; }

    /* Spinner */
    .stSpinner > div { border-top-color: #E8A838 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── Sidebar ────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("⛽ Rohstoffe")
    st.markdown("---")

    selected_labels: list[str] = st.multiselect(
        "Rohstoff auswählen",
        options=list(TICKER_MAP.keys()),
        default=list(TICKER_MAP.keys()),
        help="Mehrfachauswahl möglich.",
    )

    currency: str = st.radio(
        "Währung",
        options=["USD", "EUR"],
        index=0,
        horizontal=True,
    )

    st.markdown("---")
    refresh = st.button("🔄  Daten aktualisieren", use_container_width=True)
    if refresh:
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    st.caption("Datenquelle: Yahoo Finance (yfinance)  \nIntervall: 5 min | Zeitraum: 5 Tage")

# ─── Hauptbereich ───────────────────────────────────────────────────────────

st.markdown(
    "<h1 style='font-family:IBM Plex Mono,monospace;color:#E8A838;"
    "font-size:1.6rem;letter-spacing:0.06em;'>ROHSTOFF-DASHBOARD</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color:#6B7280;margin-top:-0.8rem;'>Echtzeit-Marktdaten · IT-Solutions GmbH</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

if not selected_labels:
    st.info("Bitte mindestens einen Rohstoff in der Sidebar auswählen.")
    st.stop()

# EUR-Rate laden (einmal, wird wiederverwendet)
eur_rate: float = 1.0
if currency == "EUR":
    with st.spinner("EUR/USD-Kurs wird geladen …"):
        eur_rate = fetch_eur_rate()

# ─── Metriken-Zeile ─────────────────────────────────────────────────────────

metric_cols = st.columns(len(selected_labels))

dataframes: dict[str, pd.DataFrame] = {}

for col_ui, label in zip(metric_cols, selected_labels):
    ticker = TICKER_MAP[label]
    with st.spinner(f"{label} wird geladen …"):
        df = fetch_ohlc(ticker)

    if currency == "EUR":
        df = usd_to_eur(df, eur_rate)

    dataframes[label] = df

    price_col = f"Preis ({currency})"
    latest_price = df[price_col].iloc[-1]
    delta = delta_percent(df, price_col)

    short_name = label.split(" ")[0] + " " + label.split(" ")[1]  # "Brent Oil"
    col_ui.metric(
        label=short_name,
        value=f"{latest_price:.2f} {currency}",
        delta=f"{delta:+.2f}% (5 Tage)",
    )

st.markdown("---")

# ─── Charts ─────────────────────────────────────────────────────────────────

chart_colors = [COLOR_PRIMARY, "#5BA3D9"]   # Orange / Blau

for (label, df), color in zip(dataframes.items(), chart_colors):
    fig = build_chart(df, label, currency, color)
    st.plotly_chart(fig, use_container_width=True)

# ─── Rohdaten-Tabelle (aufklappbar) ─────────────────────────────────────────

with st.expander("📋  Rohdaten anzeigen"):
    for label, df in dataframes.items():
        st.markdown(f"**{label}**")
        show_cols = ["Datetime", f"Preis ({currency})"]
        st.dataframe(
            df[show_cols].tail(50).sort_values("Datetime", ascending=False),
            use_container_width=True,
            hide_index=True,
        )