import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Intelligence Hub Editorial", page_icon="📰", layout="wide")

# ARCHIVO DE PERSISTENCIA
DB_FILE = "user_sets.json"

# --- FUNCIONES DE PERSISTENCIA (Cargar y Guardar en disco) ---
def load_all_presets():
    """Carga la librería base y los sets guardados por usuarios en la máquina"""
    # Librería base (la que ya teníamos)
    base_presets = {
        "📈 Economía": "Bolsa\nInflación\nBCE\nEuribor\nFiscalidad\nPIB",
        "🤖 Tecnología": "IA\nChatGPT\nNvidia\nSemicondutores\nQuantum Computing\nApple",
        "🌍 Política Nacional": "Elecciones\nGobierno\nSindicatos\nParlamento\nRegiones",
        "🗺️ Política Internacional": "ONU\nOTAN\nGeopolítica\nConflictos\nDiplomacia",
        "🌱 Medio Ambiente": "Cambio Climático\nEnergía Solar\nSequía\nReciclaje\nCO2",
        "🏥 Salud": "Pandemias\nVacunas\nSalud Mental\nBiotecnología\nOMS",
        "⚖️ Justicia": "Sentencias\nTribunal Supremo\nLeyes\nDerechos Humanos",
        "⚽ Deportes": "Champions\nLaLiga\nOlimpiadas\nFichajes\nTenis",
        "🎨 Cultura": "Museos\nCine\nLiteratura\nTeatro\nFestivales",
        "🛡️ Seguridad": "Ciberseguridad\nInteligencia\nDefensa\nPolicía"
    }
    
    # Cargar sets personalizados desde el archivo JSON si existe
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            user_data = json.load(f)
            base_presets.update(user_data) # Fusionar base con personalizados
            
    return base_presets

def save_new_preset(name, keywords):
    """Guarda un nuevo set en el archivo JSON permanentemente"""
    data = {}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    
    data[name] = keywords
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

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

# --- SEGURIDAD API KEY ---
api_key = st.secrets.get("NEWS_API_KEY", None)
if api_key is None:
    st.error("❌ Error: API Key no configurada en Secrets.")
    st.stop()

# Cargar todos los sets al iniciar
all_available_presets = load_all_presets()

# --- SIDEBAR ---
st.sidebar.title("⚙️ Panel de Control")

# 1. BUSCADOR DE SETS DINÁMICO
st.sidebar.subheader("🔍 Buscar Set Temático")
search_query = st.sidebar.text_input("Buscar tema (ej. 'Tecno')")

# Filtrar la librería basándose en la búsqueda
filtered_presets = {k: v for k, v in all_available_presets.items() if search_query.lower() in k.lower()}
preset_options = list(filtered_presets.keys())

if preset_options:
    selected_preset = st.sidebar.selectbox("Selecciona un set", preset_options)
    if st.sidebar.button("Cargar Set"):
        st.session_state['current_keywords'] = filtered_presets[selected_preset]
else:
    st.sidebar.warning("No se encontraron sets.")

# 2. GESTIÓN DE PALABRAS CLAVE
st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Ajuste de Temas")
default_val = st.session_state.get('current_keywords', "Inteligencia Artificial\nEconomía")
keywords_input = st.sidebar.text_area("Palabras clave (una por línea)", value=default_val)
keywords_list = [k.strip() for k in keywords_input.split('\n') if k.strip()]

# 3. CREACIÓN DE SETS PERMANENTES (La mejora solicitada)
st.sidebar.markdown("---")
st.sidebar.subheader("💾 Crear Set Permanente")
new_set_name = st.sidebar.text_input("Nombre del nuevo set")
if st.sidebar.button("Guardar en Disco"):
    if new_set_name and keywords_input:
        save_new_preset(new_set_name, keywords_input)
        st.sidebar.success(f"Set '{new_set_name}' guardado permanentemente!")
        # Forzamos la recarga de la librería para que aparezca el nuevo set
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("v4.0 - Permanent Intelligence Hub")

# --- CUERPO PRINCIPAL (Sigue igual que la versión anterior) ---
st.title("📰 Intelligence Hub Editorial")
st.markdown("Sistemas de monitorización de tendencias y vigilancia de medios en tiempo real.")

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
                    st.success(f"Se han capturado {len(noticias)} artículos.")
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






