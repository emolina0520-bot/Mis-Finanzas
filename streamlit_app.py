import streamlit as st
import pandas as pd
import yfinance as yf

# Configuración de la página
st.set_page_config(page_title="Mi Portafolio Eduardo", layout="wide")

# Conexión con tu Google Sheets
SHEET_ID = "1-fhgPN3WZWLz0JwdQcnzAWXVSJ9Hb124kcvDDooMBtA"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

def load_data():
    df = pd.read_csv(URL)
    return df

st.title("📊 Mi Dashboard de Inversiones")

try:
    data = load_data()
    
    # Separación por categorías
    categorias = data['Categoría'].unique()
    tabs = st.tabs(list(categorias) + ["Resumen Global"])

    total_patrimonio = 0

    for i, cat in enumerate(categorias):
        with tabs[i]:
            st.header(f"Sección {cat}")
            df_cat = data[data['Categoría'] == cat]
            
            for index, row in df_cat.iterrows():
                # Obtener precio en tiempo real si tiene Ticker
                precio_actual = 0
                if pd.notna(row['Ticker']) and row['Ticker'] != 'NA':
                    ticker = yf.Ticker(row['Ticker'])
                    precio_actual = ticker.history(period="1d")['Close'].iloc[-1]
                else:
                    precio_actual = row['Costo_Promedio'] # Para NU o montos fijos

                rendimiento = (precio_actual - row['Costo_Promedio']) / row['Costo_Promedio'] * 100
                total_activo = precio_actual * row['Cantidad']
                total_patrimonio += total_activo

                # Lógica de color para Alerta
                color = "inverse" if precio_actual <= row['Precio_Alerta'] else "normal"
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.metric(label=row['Activo'], value=f"${total_activo:,.2f} {row['Moneda']}", delta=f"{rendimiento:.2f}%")
                with col2:
                    if precio_actual <= row['Precio_Alerta']:
                        st.error("🚨 ¡ALERTA!")

    with tabs[-1]:
        st.header("Patrimonio Total")
        st.subheader(f"Total Estimado: ${total_patrimonio:,.2f} MXN")
        st.info("Este total es una suma aproximada de tus activos en pesos y dólares.")

except Exception as e:
    st.error(f"Hubo un error al leer los datos. Revisa que tu hoja de Google sea pública. Error: {e}")
