import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from market_data import (
    TICKER_MAP,
    MarketDataProvider,
    CommodityPriceProvider,
    CurrencyConverter,
)

commodity_provider = CommodityPriceProvider()
currency_converter = CurrencyConverter()

def build_chart(df: pd.DataFrame, label: str, currency: str) -> go.Figure:
    price_col = f"Preis ({currency})"
    
    # Einheit für Y-Achse Label basierend auf Rohstoff-Namen bestimmen
    einheit = ""
    if "Brent" in label or "Oil" in label or "Öl" in label:
        einheit = " / Barrel"
    elif "Gas" in label:
        einheit = " / MMBtu"

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["Datetime"],
            y=df[price_col],
            mode="lines",
            name=label,
            fill="tozeroy",
            hovertemplate=(
                "<b>%{x|%d.%m.%Y %H:%M}</b><br>"
                f"{price_col}: %{{y:.2f}}<extra></extra>"
            ),
        )
    )

    latest = df.iloc[-1]
    fig.add_trace(
        go.Scatter(
            x=[latest["Datetime"]],
            y=[latest[price_col]],
            mode="markers",
            marker=dict(size=10, symbol="circle"),
            name="Aktuell",
            hovertemplate=(
                f"<b>Aktuell</b><br>{price_col}: %{{y:.2f}}<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        template="plotly_dark",
        title=dict(
            text=f"<b>{label}</b> — letzte 5 Tage (5-min-Intervall)",
            x=0.02,
        ),
        xaxis=dict(
            title="Datum / Uhrzeit (Berlin)",
            tickformat="%d.%m %H:%M",
        ),
        yaxis=dict(title=f"Preis ({currency}{einheit})"),
        legend=dict(orientation="h", y=-0.18),
        margin=dict(l=10, r=10, t=50, b=10),
        height=420,
    )
    return fig


st.set_page_config(
    page_title="Rohstoff-Dashboard",
    page_icon="⛽",
    layout="wide",
)

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
    refresh = st.button("🔄  Daten aktualisieren", width="stretch")
    if refresh:
        st.cache_data.clear()
        st.rerun()

    # --- ALARM-EINSTELLUNGEN ---
    st.markdown("---")
    st.subheader("⏰ Preisalarm")
    
    alarm_active = st.checkbox("Alarm aktivieren")
    if alarm_active and selected_labels:
        alarm_asset = st.selectbox("Welcher Rohstoff?", options=selected_labels)
        alarm_condition = st.radio("Bedingung", options=["Größer als (>)", "Kleiner als (<)"], horizontal=True)
        alarm_threshold = st.number_input(f"Schwellenwert ({currency})", value=80.0, step=1.0)
    else:
        alarm_asset, alarm_condition, alarm_threshold = None, None, None

    st.markdown("---")
    st.caption("Datenquelle: Yahoo Finance (yfinance)  \nIntervall: 5 min | Zeitraum: 5 Tage")

st.title("Rohstoff-Dashboard")
st.caption("Echtzeit-Marktdaten · IT-Solutions GmbH")
st.markdown("---")

if not selected_labels:
    st.info("Bitte mindestens einen Rohstoff in der Sidebar auswählen.")
    st.stop()

eur_rate: float = 1.0
if currency == "EUR":
    with st.spinner("EUR/USD-Kurs wird geladen …"):
        eur_rate = currency_converter.get_exchange_rate("USD", "EUR")

metric_cols = st.columns(len(selected_labels))
dataframes: dict[str, pd.DataFrame] = {}

for col_ui, label in zip(metric_cols, selected_labels):
    ticker = TICKER_MAP[label]
    with st.spinner(f"{label} wird geladen …"):
        provider = MarketDataProvider(period="5d", interval="5m")
        df = provider.get_ohlc_data(ticker)

    if currency == "EUR":
        df = currency_converter.add_target_currency(df, "Preis (USD)", "USD", "EUR")

    dataframes[label] = df

    price_col = f"Preis ({currency})"
    latest_price = df[price_col].iloc[-1]
    delta = provider.calculate_delta_percent(df, price_col)

    # --- ALARM-PRÜFUNG ---
    is_triggered = False
    if alarm_active and label == alarm_asset:
        if "Größer" in alarm_condition and latest_price > alarm_threshold:
            is_triggered = True
        elif "Kleiner" in alarm_condition and latest_price < alarm_threshold:
            is_triggered = True

    # Hinweis einblenden, wenn der Alarm ausgelöst wird
    if is_triggered:
        st.error(f"🚨 ALARM: {label} hat die Grenze von {alarm_threshold} {currency} durchbrochen! (Aktueller Preis: {latest_price:.2f} {currency})")
        
        # HIER KÖNNTE SPÄTER DER E-MAIL VERSAND REIN

    short_name = " ".join(label.split()[:2])
    col_ui.metric(
        label=short_name,
        value=f"{latest_price:.2f} {currency}",
        delta=f"{delta:+.2f}% (5 Tage)",
    )

st.markdown("---")

for label, df in dataframes.items():
    fig = build_chart(df, label, currency)
    st.plotly_chart(fig, width="stretch")

with st.expander("📋  Rohdaten anzeigen"):
    for label, df in dataframes.items():
        st.markdown(f"**{label}**")
        show_cols =["Datetime", f"Preis ({currency})"]
        st.dataframe(
            df[show_cols].tail(50).sort_values("Datetime", ascending=False),
            width="stretch",
            hide_index=True,
        )