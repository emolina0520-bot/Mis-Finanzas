import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Portafolio Eduardo", layout="wide")

SHEET_ID = "1-fhgPN3WZWLz0JwdQcnzAWXVSJ9Hb124kcvDDooMBtA"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(URL)
    df.columns = [str(c).strip() for c in df.columns]
    df['Cantidad'] = pd.to_numeric(df['Cantidad'], errors='coerce')
    return df.dropna(subset=['Cantidad'])

st.title("📊 Mi Dashboard de Inversiones")

try:
    data = load_data()
    # Obtenemos tipo de cambio real para los ETFs (VOO, QQQ)
    usd_mxn = yf.Ticker("MXN=X").history(period="1d")['Close'].iloc[-1]
    
    total_patrimonio = 0
    # Categorías automáticas
    cats = [c for c in data.iloc[:, 0].unique() if pd.notna(c)]
    tabs = st.tabs(cats + ["Resumen Global"])

    for i, cat in enumerate(cats):
        with tabs[i]:
            df_cat = data[data.iloc[:, 0] == cat]
            for _, row in df_cat.iterrows():
                ticker = str(row['Ticker']).strip()
                cantidad = float(row['Cantidad'])
                # Precio base por si no hay internet
                p_final = pd.to_numeric(str(row.iloc[3]).replace(',',''), errors='coerce')

                if ticker and ticker.lower() != 'nan':
                    try:
                        t = yf.Ticker(ticker)
                        # Buscamos el precio más actual
                        p_final = t.history(period="1d")['Close'].iloc[-1]
                    except: pass
                
                # REGLA MAESTRA DE CONVERSIÓN:
                # Si el activo es un ETF de USA, convertimos de USD a MXN
                if ticker in ["VOO", "QQQ", "SMH", "SPMO"]:
                    valor_mxn = (cantidad * p_final) * usd_mxn
                # Si es Cripto (PAXG, ETH, SOL), Yahoo nos da el precio en USD, convertimos a MXN
                elif "-USD" in ticker.upper():
                    valor_mxn = (cantidad * p_final) * usd_mxn
                # Para lo demás (como Nu), usamos el valor directo en pesos
                else:
                    valor_mxn = cantidad * p_final
                
                total_patrimonio += valor_mxn
                st.metric(label=f"{row.iloc[0]}", value=f"${valor_mxn:,.2f} MXN")

    with tabs[-1]:
        st.header("Patrimonio Total")
        st.metric("Total Acumulado", f"${total_patrimonio:,.2f} MXN")
        st.info(f"Dólar usado: ${usd_mxn:.2f} MXN")

except Exception as e:
    st.error(f"Actualizando sistema... dale Rerun. (Error: {e})")
