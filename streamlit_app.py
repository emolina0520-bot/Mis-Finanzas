import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

st.set_page_config(page_title="Portafolio Eduardo", layout="wide")

SHEET_ID = "1-fhgPN3WZWLz0JwdQcnzAWXVSJ9Hb124kcvDDooMBtA"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(URL)
    df.columns = [str(c).strip() for c in df.columns]
    df['Cantidad'] = pd.to_numeric(df['Cantidad'], errors='coerce')
    df = df.dropna(subset=['Cantidad'])
    return df

st.title("📊 Mi Dashboard de Inversiones")

try:
    data = load_data()
    # Obtenemos tipo de cambio real
    usd_mxn = yf.Ticker("MXN=X").history(period="1d")['Close'].iloc[-1]
    
    # Lista para guardar los valores calculados y graficar después
    valores_calculados = []
    total_patrimonio_mxn = 0
    
    # Identificar columnas
    col_cat = 'Categoría' if 'Categoría' in data.columns else data.columns[5]
    
    # --- PROCESAMIENTO DE DATOS ---
    for _, row in data.iterrows():
        ticker = str(row['Ticker']).strip()
        cantidad = float(row['Cantidad'])
        costo_raw = str(row['Costo Promedio']).replace(',', '').replace('$', '')
        p_base = pd.to_numeric(costo_raw, errors='coerce')
        cat = str(row[col_cat])
        
        # Buscar precio real si no es Sofipo
        if ticker and ticker.lower() != 'nan' and len(ticker) > 2 and cat != "Sofipo":
            try:
                t = yf.Ticker(ticker)
                hist = t.history(period="1d")
                if not hist.empty:
                    p_base = hist['Close'].iloc[-1]
            except: pass
        
        # Lógica de conversión basada en columna 'Moneda'
        moneda = str(row['Moneda']).strip().upper() if 'Moneda' in data.columns else "MXN"
        if moneda == "USD" or "-USD" in ticker.upper():
            valor_mxn = (cantidad * p_base) * usd_mxn
        else:
            valor_mxn = cantidad * p_base
        
        total_patrimonio_mxn += valor_mxn
        
        # Guardamos para las gráficas
        valores_calculados.append({
            'Activo': row['Activo'],
            'Categoría': cat,
            'Valor_MXN': valor_mxn
        })

    df_final = pd.DataFrame(valores_calculados)

    # --- DISEÑO DE TABS ---
    categorias = sorted(df_final['Categoría'].unique())
    tabs = st.tabs(categorias + ["📊 Gráficas y Resumen"])

    # Tabs de activos individuales
    for i, cat in enumerate(categorias):
        with tabs[i]:
            st.subheader(f"Activos en {cat}")
            df_cat = df_final[df_final['Categoría'] == cat]
            
            # Mostrar métricas en columnas para que no ocupen tanto espacio hacia abajo
            cols = st.columns(3)
            for idx, row_fig in enumerate(df_cat.itertuples()):
                cols[idx % 3].metric(label=row_fig.Activo, value=f"${row_fig.Valor_MXN:,.2f} MXN")

    # Tab de Gráficas y Resumen Global
    with tabs[-1]:
        st.header("Resumen General")
        
        c1, c2 = st.columns(2)
        c1.metric("Patrimonio Total", f"${total_patrimonio_mxn:,.2f} MXN")
        c2.write(f"**Tipo de Cambio:** 1 USD = ${usd_mxn:.2f} MXN")
        
        st.divider()
        
        graf_col1, graf_col2 = st.columns(2)
        
        with graf_col1:
            st.subheader("Distribución por Categoría")
            fig_pie = px.pie(df_final, values='Valor_MXN', names='Categoría', 
                             hole=0.4, color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with graf_col2:
            st.subheader("Top Activos")
            # Ordenamos para que la barra más grande salga arriba
            df_sorted = df_final.sort_values(by='Valor_MXN', ascending=True)
            fig_bar = px.bar(df_sorted, x='Valor_MXN', y='Activo', orientation='h',
                             color='Categoría', text_auto='.2s')
            st.plotly_chart(fig_bar, use_container_width=True)

except Exception as e:
    st.error(f"Error al cargar datos: {e}")
