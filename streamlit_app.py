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
    # Limpieza extrema: solo filas donde la columna Cantidad sea un número
    df = df[pd.to_numeric(df.iloc[:, 2], errors='coerce').notnull()]
    return df

st.title("📊 Mi Dashboard de Inversiones")

try:
    data = load_data()
    
    # Mapeo de columnas por posición
    col_cat = data.columns[0]
    col_ticker = data.columns[1]
    col_cant = data.columns[2]
    col_costo = data.columns[3]

    total_patrimonio = 0

    # Agrupamos por categoría
    cats = [c for c in data[col_cat].unique() if pd.notna(c)]
    tabs = st.tabs(cats + ["Resumen Global"])

    for i, cat in enumerate(cats):
        with tabs[i]:
            df_cat = data[data[col_cat] == cat]
            for _, row in df_cat.iterrows():
                try:
                    # Convertir a número puro
                    cantidad = float(row[col_cant])
                    costo = float(row[col_costo])
                    ticker = str(row[col_ticker]).strip()
                    
                    precio_final = costo
                    
                    # Si hay ticker válido, buscar precio real
                    if ticker and ticker.lower() != 'nan' and len(ticker) > 1:
                        try:
                            t = yf.Ticker(ticker)
                            hist = t.history(period="1d")
                            if not hist.empty:
                                precio_final = hist['Close'].iloc[-1]
                        except: pass
                    
                    subtotal = cantidad * precio_final
                    total_patrimonio += subtotal
                    
                    label_nombre = ticker if ticker.lower() != 'nan' else "Efectivo/Nu"
                    st.metric(label=label_nombre, value=f"${subtotal:,.2f} MXN")
                except:
                    continue # Si una fila falla, se la salta y no rompe la app

    with tabs[-1]:
        st.header("Patrimonio Total")
        # Aquí forzamos que si no hay nada, muestre 0 y no NAN
        display_total = total_patrimonio if total_patrimonio > 0 else 0
        st.metric("Total Estimado", f"${display_total:,.2f} MXN")
        st.success(f"Dashboard actualizado al: {pd.Timestamp.now().strftime('%d/%m/%Y')}")

except Exception as e:
    st.error(f"Error de formato: {e}. Asegúrate de que las celdas de Cantidad y Costo solo tengan números.")
