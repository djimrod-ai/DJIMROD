import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import xml.etree.ElementTree as ET

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Intelligence Hub Editorial", page_icon="📰", layout="wide")

# --- ESTILOS ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 20px; font-weight: bold; }
    .match-box { background-color: #d4edda; padding: 10px; border-radius: 10px; border-left: 5px solid #28a745; margin-bottom: 10px; }
    .general-box { background-color: #ffffff; padding: 10px; border-radius: 10px; border-left: 5px solid #6c757d; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- LIBRERÍA de RSS ---
RSS_FEEDS = {
    "El País": "https://www.elpais.com/rss/0/latest.xml",
    "El Mundo": "https://www.elmundo.es/rss/estC1.xml",
    "ABC": "https://www.abc.es/rss/noticias.xml",
    "RTVE": "https://www.rtve.es/rss/todas-las-noticias.rss",
    "BBC Mundo": "https://www.bbc.com/mundo/index.xml",
    "EFE": "https://www.efe.com/rss/estatico/todas.xml",
}

# --- LIBRERÍA MAESTRA de TEMAS ---
all_themes = {
    "🤖 IA: Generativa": "ChatGPT\nClaude\nGemini\nMidjourney\nLLM\nSora\nPrompts\nInteligencia Artificial",
    "🪙 Criptomonedas": "Bitcoin\nEthereum\nSolana\nHalving\nStablecoins\nCripto",
    "📈 Macroeconomía": "Inflación\nPIB\nRecesión\nBCE\nEuribor\nEconomía\nBolsa",
    "🌍 Geopolítica": "Rusia\nUcrania\nChina\nOTAN\nIsrael\nGaza\nConflictos",
    "🌱 Medio Ambiente": "Cambio Climático\nEnergía Solar\nCOP28\nCO2\nSostenibilidad",
    "⚽ Deportes": "Champions\nLaLiga\nFichajes\nF1\nTenis\nDeportes",
    "🎮 Gaming y Tech": "PlayStation\nXbox\nNintendo\nSteam\nE-sports\nTecnología",
}

# --- LÓGICA NewsAPI ---
def obtener_noticias_api(api_key, keywords):
    query = ' OR '.join(keywords)
    today = datetime.now().strftime('%Y-%m-%d')
    url = f"https://newsapi.org/v2/everything?q={query}&language=es&sortBy=publishedAt&from={today}&apiKey={api_key}"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            art = res.json().get('articles', [])
            return art, "Publicadas HOY (API)" if art else "Sin noticias hoy en API"
        return [], f"Error API {res.status_code}"
    except: return [], "Error de conexión"

# --- LÓGICA RSS (SISTEMA DE DOS CUBOS) ---
def obtener_noticias_rss(keywords):
    matches = []    # Cubo 1: Solo coincidencias
    generales = []  # Cubo 2: Todo lo demás
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 SafariP537.36'}
    
    for medio, url in RSS_FEEDS.items():
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                for item in root.findall('.//item'):
                    title = item.find('title').text if item.find('title') is not None else ""
                    link = item.find('link').text if item.find('link') is not None else "#"
                    desc = item.find('description').text if item.find('description') is not None else ""
                    date = item.find('pubDate').text if item.find('pubDate') is not None else "Reciente"
                    
                    noticia = {'title': title, 'url': link, 'source': medio, 'publishedAt': date, 'description': desc}
                    
                    # Filtro estricto de palabras clave
                    if any(word.lower() in title.lower() or word.lower() in desc.lower() for word in keywords):
                        matches.append(noticia)
                    else:
                        generales.append(noticia)
        except: pass
    
    return matches, generales

# --- SEGURIDAD ---
api_key = st.secrets.get("NEWS_API_KEY", None)
if api_key is None:
    st.error("❌ Error: API Key no configurada en Secrets.")
    st.stop()

# --- SIDEBAR ---
st.sidebar.title("⚙️ Control Hub")
st.sidebar.success("✅ Sistema de Inmediatez: ACTIVO")
st.sidebar.markdown("---")
search_query = st.sidebar.text_input("🔍 Buscar tema")
filtered_presets = {k: v for k, v in all_themes.items() if search_query.lower() in k.lower()}
preset_options = list(filtered_presets.keys())

if preset_options:
    selected_preset = st.sidebar.selectbox("Selecciona el set", preset_options)
    if st.sidebar.button("Cargar Temas"):
        st.session_state['current_keywords'] = filtered_presets[selected_preset]
else:
    st.sidebar.warning("No hay sets que coincidan.")

st.sidebar.markdown("---")
default_val = st.session_state.get('current_keywords', "Inteligencia Artificial\nEconomía")
keywords_input = st.sidebar.text_area("Palabras clave", value=default_val)
keywords_list = [k.strip() for k in keywords_input.split('\n') if k.strip()]

# --- CUERPO PRINCIPAL ---
st.title("📰 Intelligence Hub Editorial")
st.markdown("Vigilancia de medios: **Prioridad de Tema** + **Sonda RSS de Actualidad**.")

tab1, tab2 = st.tabs(["🌐 Vigilancia de Medios", "🚀 Tendencias en X"])

with tab2:
    st.subheader("Explorador de Red_Sociales")
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
    st.subheader("Buscador de Noticias Recientes")
    modo = st.radio("Selecciona el motor de búsqueda:", 
                    ["Instantánea (RSS Feeds)", "Global (NewsAPI)"], 
                    index=0, horizontal=True)
    
    num_results = st.slider("Cantidad de noticias", 5, 50, 20)

    if st.button("🔍 Ejecutar Rastreo"):
        if not keywords_list:
            st.warning("Introduce palabras clave.")
        else:
            with st.spinner('Analizando la actualidad...'):
                if modo == "Global (NewsAPI)":
                    noticias, periodo = obtener_noticias_api(api_key, keywords_list)
                    
                    if noticias:
                        st.success(f"Resultado: {periodo}")
                        df = pd.DataFrame(noticias)[['title', 'source', 'publishedAt', 'url']]
                        df.columns = ['Título', 'Fuente', 'Fecha', 'Enlace']
                        st.dataframe(df, use_container_width=True)
                        st.markdown("---")
                        for art in noticias[:num_results]:
                            st.markdown(f"### [{art['title']}]({art['url']})")
                            st.write(f"**{art['source']}** | {art['publishedAt']}")
                            st.write(art['description'])
                            st.markdown("---")
                    else:
                        st.error(f"No se han encontrado noticias hoy mediante {modo}.")
                
                else: # MODO RSS
                    matches, generales = obtener_noticias_rss(keywords_list)
                    
                    # 1. SECCIÓN DE COINCIDENCIAS (PRIORIDAD ABSOLUTA)
                    st.subheader("🎯 COINCIDENCIAS EXACTAS")
                    if matches:
                        st.success(f"Se han encontrado {len(matches)} noticias relacionadas con tus temas.")
                        for art in matches[:num_results]:
                            st.markdown(f"""<div class="match-box">
                                <b>⭐ MATCH ENCONTRADO</b><br>
                                <h3><a href="{art['url']}" target="_blank">{art['title']}</a></h3>
                                <i>{art['source']} | {art['publishedAt']}</i><br>
                                {art['description']}
                                </div>""", unsafe_allow_html=True)
                    else:
                        st.info("No hay noticias que coincidan exactamente con los temas hoy.")

                    st.markdown("---")

                    # 2. SECCIÓN DE ACTUALIDAD GENERAL (RELLENO)
                    st.subheader("🕒 ÚLTIMAS NOTICIAS ( la actualidad general)")
                    if generales:
                        for art in generales[:num_results]:
                            st.markdown(f"""<div class="general-box">
                                <b>🕒 ACTUALIDAD</b><br>
                                <h4><a href="{art['url']}" target="_blank">{art['title']}</a></h4>
                                <i>{art['source']} | {art['publishedAt']}</i><br>
                                {art['description']}
                                </div>""", unsafe_allow_html=True)
                    else:
                        st.write("No hay noticias generales disponibles.")
