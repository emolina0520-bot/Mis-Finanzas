import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Portafolio Eduardo", layout="wide")

# [span_2](start_span)Conexión con tu hoja analizada[span_2](end_span)
SHEET_ID = "1-fhgPN3WZWLz0JwdQcnzAWXVSJ9Hb124kcvDDooMBtA"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(URL)
    # [span_3](start_span)Limpiamos nombres de columnas quitando espacios[span_3](end_span)
    df.columns = [str(c).strip() for c in df.columns]
    # FILTRO CLAVE: Solo procesamos filas donde 'Cantidad' sea un número real
    # [span_4](start_span)Esto ignora tus notas de "Inversión inicial", "Tasa", etc. al final de la hoja[span_4](end_span)
    df['Cantidad'] = pd.to_numeric(df['Cantidad'], errors='coerce')
    df = df.dropna(subset=['Cantidad'])
    return df

st.title("📊 Mi Dashboard de Inversiones")

try:
    data = load_data()
    
    # [span_5](start_span)Obtenemos tipo de cambio actual USD/MXN para tus ETFs[span_5](end_span)
    try:
        usd_mxn = yf.Ticker("MXN=X").history(period="1d")['Close'].iloc[-1]
    except:
        usd_mxn = 17.50 # Valor de respaldo si falla la conexión

    total_patrimonio_mxn = 0
    categorias = [c for c in data['Categoría'].unique() if pd.notna(c)]
    tabs = st.tabs(categorias + ["Resumen Global"])

    for i, cat in enumerate(categorias):
        with tabs[i]:
            df_cat = data[data['Categoría'] == cat]
            for _, row in df_cat.iterrows():
                # [span_6](start_span)Limpiamos el costo por si tiene comas como el '83,685.65' de tu Pax Gold[span_6](end_span)
                costo_raw = str(row['Costo Promedio']).replace(',', '').replace('$', '')
                precio_base = pd.to_numeric(costo_raw, errors='coerce')
                
                ticker = str(row['Ticker']).strip()
                es_usd = str(row['Moneda']).strip().upper() == "USD"
                
                # Si tiene Ticker y no es NU, buscamos precio en vivo
                if ticker and ticker.lower() != 'nan' and len(ticker) > 2 and cat != "Sofipo":
                    try:
                        t = yf.Ticker(ticker)
                        precio_base = t.history(period="1d")['Close'].iloc[-1]
                    except: pass
                
                # [span_7](start_span)Convertimos a pesos si es USD[span_7](end_span)
                if es_usd:
                    valor_mxn = precio_base * usd_mxn * row['Cantidad']
                else:
                    valor_mxn = precio_base * row['Cantidad']
                
                total_patrimonio_mxn += valor_mxn
                st.metric(label=row['Activo'], value=f"${valor_mxn:,.2f} MXN")

    with tabs[-1]:
        st.header("Patrimonio Total Actualizado")
        st.metric("Total (MXN)", f"${total_patrimonio_mxn:,.2f}")
        st.caption(f"Tipo de cambio: $1 USD = ${usd_mxn:.2f} MXN")

except Exception as e:
    st.error(f"Configuración lista. Dale a 'Rerun' en el menú de la app. Detalle: {e}")
