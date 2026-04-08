import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Portafolio Eduardo", layout="wide")

# Tu ID de hoja
SHEET_ID = "1-fhgPN3WZWLz0JwdQcnzAWXVSJ9Hb124kcvDDooMBtA"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=300) 
def load_data():
    df = pd.read_csv(URL)
    # Limpiamos las categorías para que siempre sean texto y no den error
    df['Categoría'] = df['Categoría'].fillna('Otros').astype(str)
    return df

st.title("📊 Mi Dashboard de Inversiones")

try:
    data = load_data()
    # Filtramos para que solo use categorías con texto real
    cats = sorted([c for c in data['Categoría'].unique() if len(c) > 1])
    
    tabs = st.tabs(cats + ["Resumen Global"])

    total_patrimonio = 0

    for i, cat in enumerate(cats):
        with tabs[i]:
            st.subheader(f"Activos en {cat}")
            df_cat = data[data['Categoría'] == cat]
            
            for _, row in df_cat.iterrows():
                # Si es NU o efectivo, usamos el costo promedio (cantidad)
                precio_actual = row['Costo_Promedio']
                
                # Si tiene Ticker, buscamos el precio real
                if pd.notna(row['Ticker']) and len(str(row['Ticker'])) > 1:
                    try:
                        t = yf.Ticker(str(row['Ticker']))
                        precio_actual = t.history(period="1d")['Close'].iloc[-1]
                    except:
                        pass
                
                valor_total = precio_actual * row['Cantidad']
                total_patrimonio += valor_total
                
                st.metric(label=row['Activo'], value=f"${valor_total:,.2f} {row['Moneda']}")

    with tabs[-1]:
        st.header("Estado General")
        st.metric("Patrimonio Total Estimado", f"${total_patrimonio:,.2f} MXN")

except Exception as e:
    st.error(f"Casi listo. Revisa tu Excel: {e}")
