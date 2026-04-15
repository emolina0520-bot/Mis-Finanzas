import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Portafolio Eduardo", layout="wide")

SHEET_ID = "1-fhgPN3WZWLz0JwdQcnzAWXVSJ9Hb124kcvDDooMBtA"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(URL)
    # Limpiamos nombres de columnas quitando espacios
    df.columns = [str(c).strip() for c in df.columns]
    # Filtro: Solo filas donde 'Cantidad' sea un número real
    df['Cantidad'] = pd.to_numeric(df['Cantidad'], errors='coerce')
    df = df.dropna(subset=['Cantidad'])
    return df

st.title("📊 Mi Dashboard de Inversiones")

try:
    data = load_data()
    # Obtenemos tipo de cambio real
    usd_mxn = yf.Ticker("MXN=X").history(period="1d")['Close'].iloc[-1]
    
    total_patrimonio_mxn = 0
    
    # USAMOS TU COLUMNA 'Categoría' (Columna F)
    col_cat = 'Categoría' if 'Categoría' in data.columns else data.columns[5]
    
    # Ordenamos las categorías para que Cripto salga primero
    categorias = sorted([c for c in data[col_cat].unique() if pd.notna(c)])
    tabs = st.tabs(categorias + ["Resumen Global"])

    for i, cat in enumerate(categorias):
        with tabs[i]:
            st.subheader(f"Activos en {cat}")
            df_cat = data[data[col_cat] == cat]
            
            for _, row in df_cat.iterrows():
                ticker = str(row['Ticker']).strip()
                cantidad = float(row['Cantidad'])
                # Limpiamos el costo (por las comas)
                costo_raw = str(row['Costo Promedio']).replace(',', '').replace('$', '')
                p_base = pd.to_numeric(costo_raw, errors='coerce')
                
                # Si tiene Ticker y NO es Sofipo, buscamos precio real
                if ticker and ticker.lower() != 'nan' and len(ticker) > 2 and cat != "Sofipo":
                    try:
                        t = yf.Ticker(ticker)
                        hist = t.history(period="1d")
                        if not hist.empty:
                            p_base = hist['Close'].iloc[-1]
                    except: 
                        pass
                
                # --- LÓGICA DE CONVERSIÓN CORREGIDA ---
                # Detectamos la moneda desde tu columna 'Moneda' (Columna H)
                moneda = str(row['Moneda']).strip().upper() if 'Moneda' in data.columns else "MXN"
                
                # Si la moneda es USD o el ticker es de cripto (-USD), convertimos
                if moneda == "USD" or "-USD" in ticker.upper():
                    valor_mxn = (cantidad * p_base) * usd_mxn
                else:
                    valor_mxn = cantidad * p_base
                # ---------------------------------------
                
                total_patrimonio_mxn += valor_mxn
                st.metric(label=row['Activo'], value=f"${valor_mxn:,.2f} MXN")

    with tabs[-1]:
        st.header("Patrimonio Total")
        st.metric("Total Acumulado", f"${total_patrimonio_mxn:,.2f} MXN")
        st.write(f"Dólar: ${usd_mxn:.2f} MXN")

except Exception as e:
    st.error(f"Casi listo. Dale a Rerun en la app. (Info: {e})")
