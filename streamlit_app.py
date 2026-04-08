import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Portafolio Eduardo", layout="wide")

SHEET_ID = "1-fhgPN3WZWLz0JwdQcnzAWXVSJ9Hb124kcvDDooMBtA"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(URL)
    # Limpieza de nombres de columnas
    df.columns = [str(c).strip() for c in df.columns]
    # Filtramos: Solo filas que tengan un Ticker o que la Cantidad sea un número real
    # Esto ignora las celdas de "13%", "Fecha", etc.
    df = df[pd.to_numeric(df.iloc[:, 2], errors='coerce').notnull()]
    return df

st.title("📊 Mi Dashboard de Inversiones")

try:
    data = load_data()
    
    # Columnas: A=Categoría(0), B=Ticker(1), C=Cantidad(2), D=Costo(3)
    col_cat = data.columns[0]
    col_ticker = data.columns[1]
    col_cant = data.columns[2]
    col_costo = data.columns[3]

    # Convertir a números lo que deba ser número
    data[col_cant] = pd.to_numeric(data[col_cant], errors='coerce')
    data[col_costo] = pd.to_numeric(data[col_costo], errors='coerce')
    
    cats = sorted([str(c) for c in data[col_cat].unique() if pd.notna(c) and len(str(c)) > 1])
    tabs = st.tabs(cats + ["Resumen Global"])

    total_mxn = 0

    for i, cat in enumerate(cats):
        with tabs[i]:
            df_cat = data[data[col_cat] == cat]
            for _, row in df_cat.iterrows():
                p_actual = float(row[col_costo])
                ticker = str(row[col_ticker]).strip()
                
                # Si tiene Ticker (y no es nan), buscamos precio real
                if ticker and ticker.lower() != 'nan' and len(ticker) > 1:
                    try:
                        t = yf.Ticker(ticker)
                        hist = t.history(period="1d")
                        if not hist.empty:
                            p_actual = hist['Close'].iloc[-1]
                    except: pass
                
                valor_total = p_actual * float(row[col_cant])
                total_mxn += valor_total
                
                nombre = ticker if ticker.lower() != 'nan' else "Inversión"
                st.metric(label=f"Activo: {nombre}", value=f"${valor_total:,.2f} MXN")

    with tabs[-1]:
        st.header("Patrimonio Total")
        st.metric("Total Estimado", f"${total_mxn:,.2f} MXN")
        st.info("Nota: Los precios de Criptos y ETFs se actualizan automáticamente.")

except Exception as e:
    st.error(f"Error al procesar los datos: {e}")
