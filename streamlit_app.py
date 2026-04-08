import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Portafolio Eduardo", layout="wide")

SHEET_ID = "1-fhgPN3WZWLz0JwdQcnzAWXVSJ9Hb124kcvDDooMBtA"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(URL)
    # Limpiamos nombres de columnas por si tienen espacios
    df.columns = [str(c).strip() for c in df.columns]
    return df

st.title("📊 Mi Dashboard de Inversiones")

try:
    data = load_data()
    
    # Identificamos columnas por posición según tu foto
    # A=Categoría(0), B=Ticker(1), C=Cantidad(2), D=Costo(3)
    col_cat = data.columns[0]
    col_ticker = data.columns[1]
    col_cant = data.columns[2]
    col_costo = data.columns[3]

    # Quitamos filas vacías
    data = data.dropna(subset=[col_cant])
    
    cats = sorted([str(c) for c in data[col_cat].unique() if pd.notna(c)])
    tabs = st.tabs(cats + ["Resumen Global"])

    total_mxn = 0

    for i, cat in enumerate(cats):
        with tabs[i]:
            df_cat = data[data[col_cat] == cat]
            for _, row in df_cat.iterrows():
                # Precio actual (usamos el del Excel por defecto)
                try:
                    p_actual = float(row[col_costo])
                except: p_actual = 0
                
                ticker = str(row[col_ticker])
                if ticker and ticker != 'nan' and len(ticker) > 1:
                    try:
                        # Si es crypto o ETF, buscamos precio real
                        t = yf.Ticker(ticker)
                        p_actual = t.history(period="1d")['Close'].iloc[-1]
                    except: pass
                
                valor_total = p_actual * float(row[col_cant])
                total_mxn += valor_total
                
                nombre_mostrar = ticker if ticker != 'nan' else "Inversión"
                st.metric(label=nombre_mostrar, value=f"${valor_total:,.2f}")

    with tabs[-1]:
        st.header("Patrimonio Total")
        st.metric("Total Estimado", f"${total_mxn:,.2f} MXN")

except Exception as e:
    st.error(f"Revisa los títulos de tu Excel. Error: {e}")
