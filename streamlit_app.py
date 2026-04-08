import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Portafolio Eduardo", layout="wide")

# Conexión a tu Google Sheets
SHEET_ID = "1-fhgPN3WZWLz0JwdQcnzAWXVSJ9Hb124kcvDDooMBtA"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(URL)
    # Limpiamos nombres de columnas
    df.columns = [str(c).strip() for c in df.columns]
    # Filtro: Solo filas con cantidad numérica (ignora notas de abajo)
    df['Cantidad'] = pd.to_numeric(df['Cantidad'], errors='coerce')
    df = df.dropna(subset=['Cantidad'])
    return df

st.title("📊 Mi Dashboard de Inversiones")

try:
    data = load_data()
    # Precio del dólar hoy
    usd_mxn = yf.Ticker("MXN=X").history(period="1d")['Close'].iloc[-1]
    
    total_patrimonio = 0
    # Obtenemos las categorías reales (Cripto, ETF, Sofipo)
    # Según tu Excel, la columna A se llama "Activo" o "Categoría" dependiendo de la versión
    # Vamos a usar la posición 0 para no fallar
    col_cat_nombre = data.columns[0] 
    categorias = [c for c in data[col_cat_nombre].unique() if pd.notna(c)]
    
    # Creamos las pestañas ordenadas
    tabs = st.tabs(categorias + ["Resumen Global"])

    for i, cat in enumerate(categorias):
        with tabs[i]:
            st.subheader(f"Detalle de {cat}")
            df_cat = data[data[col_cat_nombre] == cat]
            
            for _, row in df_cat.iterrows():
                ticker = str(row['Ticker']).strip()
                cantidad = float(row['Cantidad'])
                # Precio base del Excel
                costo_raw = str(row['Costo Promedio']).replace(',','').replace('$','')
                p_final = pd.to_numeric(costo_raw, errors='coerce')

                # Si tiene ticker y no es Nu, buscamos en la bolsa
                if ticker and ticker.lower() != 'nan' and len(ticker) > 2:
                    try:
                        t = yf.Ticker(ticker)
                        p_final = t.history(period="1d")['Close'].iloc[-1]
                    except: pass
                
                # Conversión de divisas
                # Si es un ETF gringo o el ticker termina en -USD, multiplicamos por tipo de cambio
                if ticker in ["VOO", "QQQ", "SMH", "SPMO"] or "-USD" in ticker.upper():
                    valor_mxn = (cantidad * p_final) * usd_mxn
                else:
                    valor_mxn = cantidad * p_final
                
                total_patrimonio += valor_mxn
                # Mostramos el activo individual
                nombre_mostrar = row['Activo'] if 'Activo' in data.columns else ticker
                st.metric(label=nombre_mostrar, value=f"${valor_mxn:,.2f} MXN")

    with tabs[-1]:
        st.header("Patrimonio Total")
        st.metric("Total Acumulado", f"${total_patrimonio:,.2f} MXN")
        st.info(f"Dólar actualizado: ${usd_mxn:.2f} MXN")

except Exception as e:
    st.error(f"Ordenando categorías... dale Rerun en la app. (Info: {e})")
