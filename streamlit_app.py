import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Portafolio Eduardo", layout="wide")

SHEET_ID = "1-fhgPN3WZWLz0JwdQcnzAWXVSJ9Hb124kcvDDooMBtA"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(URL)
    df.columns = [str(c).strip() for c in df.columns]
    # Filtro: Solo filas con cantidad numérica
    df = df[pd.to_numeric(df.iloc[:, 2], errors='coerce').notnull()]
    return df

st.title("📊 Mi Dashboard de Inversiones")

try:
    data = load_data()
    col_cat = data.columns[0]
    col_ticker = data.columns[1]
    col_cant = data.columns[2]
    col_costo = data.columns[3]

    # Intentamos obtener el tipo de cambio USD/MXN real
    try:
        usd_mxn = yf.Ticker("MXN=X").history(period="1d")['Close'].iloc[-1]
    except:
        usd_mxn = 17.0  # Valor de respaldo

    total_patrimonio_mxn = 0
    cats = [c for c in data[col_cat].unique() if pd.notna(c)]
    tabs = st.tabs(cats + ["Resumen Global"])

    for i, cat in enumerate(cats):
        with tabs[i]:
            df_cat = data[data[col_cat] == cat]
            for _, row in df_cat.iterrows():
                cantidad = float(row[col_cant])
                costo_excel = float(row[col_costo])
                ticker = str(row[col_ticker]).strip()
                
                # REGLA DE ORO: Si no hay ticker o es nan, es pesos (Efectivo/Nu)
                if not ticker or ticker.lower() == 'nan' or len(ticker) < 2:
                    precio_final = costo_excel
                    moneda = "MXN"
                else:
                    # Si hay ticker, buscamos precio en Yahoo (Dólares)
                    try:
                        t = yf.Ticker(ticker)
                        precio_final = t.history(period="1d")['Close'].iloc[-1]
                        precio_final = precio_final * usd_mxn # Convertimos a pesos
                        moneda = "USD (Convertido)"
                    except:
                        precio_final = costo_excel
                        moneda = "MXN"

                subtotal = cantidad * precio_final
                total_patrimonio_mxn += subtotal
                
                nombre = ticker if ticker.lower() != 'nan' else "Inversión"
                st.metric(label=nombre, value=f"${subtotal:,.2f} MXN", help=f"Originalmente en {moneda}")

    with tabs[-1]:
        st.header("Patrimonio Total")
        st.metric("Total en Pesos", f"${total_patrimonio_mxn:,.2f} MXN")
        st.write(f"Tipo de cambio usado: $1 USD = ${usd_mxn:.2f} MXN")

except Exception as e:
    st.error(f"Error: {e}")
