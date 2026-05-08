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
    "🤖 IA: Generativa": "ChatGPT\nClaude\nGemini\nMidjourney\nLLM\nSora\nPrompts",
    "🪙 Criptomonedas": "Bitcoin\nEthereum\nSolana\nHalving\nStablecoins",
    "📈 Macroeconomía": "Inflación\nPIB\nRecesión\nBCE\nEuribor",
    "🌍 Geopolítica": "Rusia\nUcrania\nChina\nOTAN\nIsrael\nGaza",
    "🌱 Medio Ambiente": "Cambio Climático\nEnergía Solar\nCOP28\nCO2",
    "⚽ Deportes": "Champions\nLaLiga\nFichajes\nF1\nTenis",
    "🎮 Gaming y Tech": "PlayStation\nXbox\nNintendo\nSteam\nE-sports",
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

# --- LÓGICA RSS (HÍBRIDA: COINCIDENCIAS + ACTUALIDAD) ---
def obtener_noticias_rss(keywords):
    noticias_estrellas = [] # Coincidencias exactas
    noticias_generales = []   # Todo lo demás
    
    for medio, url in RSS_FEEDS.items():
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                for item in root.findall('.//item'):
                    title = item.find('title').text if item.find('title') is not None else ""
                    link = item.find('link').text if item.find('link') is not None else "#"
                    desc = item.find('description').text if item.find('description') is not None else ""
                    date = item.find('pubDate').text if item.find('pubDate') is not None else "Reciente"
                    
                    noticia = {'title': title, 'url': link, 'source': medio, 'publishedAt': date, 'description': desc}
                    
                    # Si coincide con la palabra clave, va a la lista de prioridad (estrellas)
                    if any(word.lower() in title.lower() or word.lower() in desc.lower() for word in keywords):
                        noticias_estrellas.append(noticia)
                    else:
                        # Si no coincide, va a la lista de actualidad general
                        noticias_generales.append(noticia)
        except: pass
    
    # COMBINAMOS: Primero las estrellas, luego la actualidad general para rellenar
    final_list = noticias_estrellas + noticias_generales
    
    if noticias_estrellas:
        return final_list, f"Híbrido: {len(noticias_estrellas)} coincidencias + Actualidad"
    elif noticias_generales:
        return noticias_generales, "Modo Radar (Actualidad General)"
    else:
        return [], "No se pudo conectar con los feeds"

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
st.markdown("Vigilancia de medios: **Filtro Estricto de Hoy** + **Sonda RSS Híbrida**.")

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
                else:
                    noticias, periodo = obtener_noticias_rss(keywords_list)
                
                if noticias:
                    st.success(f"Resultado: {periodo}")
                    df = pd.DataFrame(noticias)[['title', 'source', 'publishedAt', 'url']]
                    df.columns = ['Título', 'Fuente', 'Fecha', 'Enlace']
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Descargar CSV", data=csv, 
                                     file_name=f"tendencias_{datetime.now().strftime('%Y%m%d')}.csv", mime='text/csv')
                    st.dataframe(df, use_container_width=True)
                    st.markdown("---")
                    st.subheader("📄 Análisis Detallado")
                    for art in noticias[:num_results]:
                        with st.container():
                            st.markdown(f"### [{art['title']}]({art['url']})")
                            st.write(f"**{art['source']}** | {art['publishedAt']}")
                            st.write(art['description'])
                            st.markdown("---")
                else:
                    st.error(f"No se han encontrado noticias hoy mediante {modo}.")
