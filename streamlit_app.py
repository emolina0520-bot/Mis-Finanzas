import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Portafolio Eduardo", layout="wide")

# Tu ID de hoja actualizado
SHEET_ID = "1-fhgPN3WZWLz0JwdQcnzAWXVSJ9Hb124kcvDDooMBtA"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=600) # Esto evita que Google te bloquee (guarda los datos 10 min)
def load_data():
    df = pd.read_csv(URL)
    # Limpieza: Convertir categorías a texto y quitar vacíos
    df['Categoría'] = df['Categoría'].astype(str).replace('nan', 'Sin Categoría')
    return df

st.title("📊 Mi Dashboard de Inversiones")

try:
    data = load_data()
    cats = [str(c) for c in data['Categoría'].unique() if c]
    tabs = st.tabs(cats + ["Resumen Global"])

    total_patrimonio = 0

    for i, cat in enumerate(cats):
        with tabs[i]:
            df_cat = data[data['Categoría'] == cat]
            for _, row in df_cat.iterrows():
                precio_actual = row['Costo_Promedio']
                # Intentar buscar precio real si hay Ticker
                if pd.notna(row['Ticker']) and str(row['Ticker']) != 'nan':
                    try:
                        t = yf.Ticker(str(row['Ticker']))
                        precio_actual = t.history(period="1d")['Close'].iloc[-1]
                    except: pass
                
                valor_total = precio_actual * row['Cantidad']
                total_patrimonio += valor_total
                
                st.metric(label=row['Activo'], value=f"${valor_total:,.2f} {row['Moneda']}")

    with tabs[-1]:
        st.metric("Patrimonio Total Estimado", f"${total_patrimonio:,.2f} MXN")

except Exception as e:
    st.error(f"Error técnico: {e}. Revisa que las columnas de tu Excel tengan los nombres correctos.")

