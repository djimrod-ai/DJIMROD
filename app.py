import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Editorial Intelligence Hub", page_icon="📰", layout="wide")

# --- CONFIGURACIÓN GOOGLE SHEETS ---
# Nombre de tu hoja de cálculo exacta
SHEET_NAME = "Nombre de tu Hoja de Calculo Aqui" 

def conectar_google_sheets():
    # Usamos los secretos de Streamlit para la autenticación
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(creds)
    return client.open(SHEET_NAME).get_worksheet(0)

# --- LÓGICA DE BÚSQUEDA ---
def obtener_noticias(api_key, keywords):
    query = ' OR '.join(keywords)
    url = f"https://newsapi.org/v2/everything?q={query}&language=es&sortBy=publishedAt&apiKey={api_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get('articles', [])
        return []
    except Exception:
        return []

# --- SEGURIDAD ---
api_key = st.secrets.get("NEWS_API_KEY", None)
if api_key is None:
    st.error("❌ Error: API Key de NewsAPI no configurada.")
    st.stop()

# --- GESTIÓN DE SETS (Google Sheets) ---
try:
    sheet = conectar_google_sheets()
    # Leer todos los datos de la hoja
    data = sheet.get_all_records()
    # Convertir la lista de diccionarios en un diccionario de {Nombre: Keywords}
    all_presets = {row['Set Name']: row['Keywords'] for row in data}
except Exception as e:
    st.error(f"Error conectando con Google Sheets: {e}")
    all_presets = {"Error": "No se pudo cargar la base de datos"}

# --- SIDEBAR ---
st.sidebar.title("⚙️ Control Hub")

# 1. BUSCADOR DINÁMICO
st.sidebar.subheader("🔍 Buscar Set Temático")
search_query = st.sidebar.text_input("Buscar tema (ej. 'Tecno')")
filtered_presets = {k: v for k, v in all_presets.items() if search_query.lower() in k.lower()}
preset_options = list(filtered_presets.keys())

if preset_options:
    selected_preset = st.sidebar.selectbox("Selecciona un set", preset_options)
    if st.sidebar.button("Cargar Set"):
        st.session_state['current_keywords'] = filtered_presets[selected_preset]
else:
    st.sidebar.warning("No se encontraron sets.")

# 2. AJUSTE de TEMAS
st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Ajuste de Temas")
default_val = st.session_state.get('current_keywords', "Inteligencia Artificial\nEconomía")
keywords_input = st.sidebar.text_area("Palabras clave (una por línea)", value=default_val)
keywords_list = [k.strip() for k in keywords_input.split('\n') if k.strip()]

# 3. GUARDADO PERMANENTE EN NUBE
st.sidebar.markdown("---")
st.sidebar.subheader("☁️ Guardar en la Nube")
new_set_name = st.sidebar.text_input("Nombre del nuevo set")
if st.sidebar.button("Guardar en Google Sheets"):
    if new_set_name and keywords_input:
        try:
            # Añadir una fila nueva al final de la hoja
            sheet.append_row([new_set_name, keywords_input])
            st.sidebar.success(f"Set '{new_set_name}' guardado en la nube!")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error al guardar: {e}")

st.sidebar.caption("v5.0 - Enterprise Cloud Hub")

# --- CUERPO PRINCIPAL ---
st.title("📰 Intelligence Hub Editorial")
st.markdown("Sistema de inteligencia de contenidos con base de datos persistente en la nube.")

tab1, tab2 = st.tabs(["🌐 Vigilancia de Medios", "🚀 Tendencias en X"])

with tab2:
    st.subheader("Explorador de Redes Sociales")
    if keywords_list:
        cols = st.columns(4)
        for idx, word in enumerate(keywords_list):
            col = cols[idx % 4]
            twitter_url = f"https://twitter.com/search?q={word.replace(' ', '%20')}&f=live"
            with col:
                st.markdown(f"**{word}**")
                st.markdown(f"🔗 [Ver en X ↗️]({twitter_url})")
                st.markdown("---")

with tab1:
    st.subheader("Análisis de Medios Digitales")
    num_results = st.slider("Cantidad de noticias", 5, 50, 20)

    if st.button("🔍 Ejecutar Rastreo de Noticias"):
        if not keywords_list:
            st.warning("Introduce palabras clave.")
        else:
            with st.spinner('Analizando...'):
                noticias = obtener_noticias(api_key, keywords_list)
                if noticias:
                    st.success(f"Capturadas {len(noticias)} noticias.")
                    df = pd.DataFrame(noticias)[['title', 'source', 'publishedAt', 'url']]
                    df.columns = ['Título', 'Fuente', 'Fecha', 'Enlace']
                    
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Descargar CSV", data=csv, 
                                     file_name=f"reporte_{datetime.now().strftime('%Y%m%d')}.csv", mime='text/csv')
                    
                    st.dataframe(df, use_container_width=True)
                    st.markdown("---")
                    st.subheader("📄 Análisis Detallado")
                    for art in noticias[:num_results]:
                        with st.container():
                            c1, c2 = st.columns([3, 1])
                            with c1:
                                st.markdown(f"### [{art['title']}]({art['url']})")
                                st.write(f"**{art['source']['name']}** | {art['publishedAt'][:10]}")
                                st.write(art['description'])
                            with c2:
                                st.markdown(f"[Leer completo ↗️]({art['url']})")
                            st.markdown("---")
                else:
                    st.error("No se encontraron noticias.")





