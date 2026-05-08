import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- SISTEMA DE IMPORTACIÓN CON DIAGNÓSTICO ---
try:
    import feedparser
    RSS_AVAILABLE = True
except ImportError:
    RSS_AVAILABLE = False

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Intelligence Hub Pro: Diagnóstico", page_icon="📰", layout="wide")

# --- ESTILOS ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 20px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- LIBRERÍA de RSS (URLs actualizadas) ---
RSS_FEEDS = {
    "El País": "https://www.elpais.com/rss/0/latest.xml",
    "El Mundo": "https://www.elmundo.es/rss/estC1.xml",
    "ABC": "https://www.abc.es/rss/noticias.xml",
    "RTVE": "https://www.rtve.es/rss/todas-las-noticias.rss",
    "BBC Mundo": "https://www.bbc.com/mundo/index.xml",
}

# --- LIBRERÍA MAESTRA de TEMAS ---
all_themes = {
    "🤖 IA: Generativa": "ChatGPT\nClaude\nGemini\nMidjourney\nLLM\nSora\nPrompts",
    "🪙 Criptomonedas": "Bitcoin\nEthereum\nSolana\nHalving\nStablecoins",
    "📈 Macroeconomía": "Inflación\nPIB\nRecesión\nBCE\nEuribor",
    "🌍 Geopolítica": "Rusia\nUcrania\nChina\nOTAN\nIsrael\nGaza",
    "⚽ Deportes": "Champions\nLaLiga\nFichajes\nF1\nTenis",
    "🎮 Gaming y Tech": "PlayStation\nXbox\nNvidia\nApple\nGaming",
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
            if art: return art, "Publicadas HOY (API)"
            return [], "Sin noticias hoy en API"
        return [], f"Error API {res.status_code}"
    except: return [], "Error de conexión"

# --- LÓGICA RSS CON DIAGNÓSTICO ---
def obtener_noticias_rss(keywords):
    if not RSS_AVAILABLE:
        return [], "ERROR: Librería feedparser NO instalada"
        
    noticias_coincidentes = []
    todas_las_recientes = [] 
    feeds_fallidos = 0
    
    for medio, url in RSS_FEEDS.items():
        try:
            # Añadimos un 'User-Agent' para que el periódico no crea que somos un bot malicioso
            feed = feedparser.parse(url)
            if not feed.entries:
                feeds_fallidos += 1
                continue
                
            for entry in feed.entries:
                noticia = {
                    'title': entry.title,
                    'url': entry.link,
                    'source': medio,
                    'publishedAt': entry.published if hasattr(entry, 'published') else "Reciente",
                    'description': entry.summary if hasattr(entry, 'summary') else ""
                }
                todas_las_recientes.append(noticia)
                if any(word.lower() in entry.title.lower() or word.lower() in entry.summary.lower() for word in keywords):
                    noticias_coincidentes.append(noticia)
        except:
            feeds_fallidos += 1
    
    if feeds_fallidos == len(RSS_FEEDS):
        return [], "ERROR: Todos los periódicos bloquearon la conexión"

    if noticias_coincidentes:
        return noticias_coincidentes, "Tiempo Real (Coincidencias)"
    else:
        return todas_las_recientes[:20], "Modo Radar (Últimas generales)"

# --- SEGURIDAD ---
api_key = st.secrets.get("NEWS_API_KEY", None)
if api_key is None:
    st.error("❌ Error: API Key de NewsAPI no configurada en Secrets.")
    st.stop()

# --- SIDEBAR ---
st.sidebar.title("⚙️ Control Hub")

# CHEQUEO DE SALUD (Diagnóstico en vivo)
st.sidebar.subheader("🩺 Estado del Sistema")
if RSS_AVAILABLE:
    st.sidebar.success("✅ Motor RSS: Activo")
else:
    st.sidebar.error("❌ Motor RSS: Desactivado (Falta librería)")

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
st.markdown("Vigilancia de medios: **Filtro Estricto de Hoy** + **Sonda RSS**.")

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
            with st.spinner('Consultando servidores...'):
                if modo == "Global (NewsAPI)":
                    noticias, periodo = obtener_noticias_api(api_key, keywords_list)
                else:
                    noticias, periodo = obtener_noticias_rss(keywords_list)
                
                if noticias:
                    st.success(f"Resultado: {periodo}")
                    df = pd.DataFrame(noticias)[['title', 'source', 'publishedAt', 'url']]
                    df.columns = ['Título', 'Fuente', 'Fecha', 'Enlace']
                    st.dataframe(df, use_container_width=True)
                    
                    st.markdown("---")
                    st.subheader("📄 Análisis Detallado")
                    for art in noticias[:num_results]:
                        with st.container():
                            c1, c2 = st.columns([3, 1])
                            with c1:
                                st.markdown(f"### [{art['title']}]({art['url']})")
                                st.write(f"**{art['source']}** | {art['publishedAt']}")
                                st.write(art['description'])
                            with c2:
                                st.markdown(f"[Leer completo ↗️]({art['url']})")
                            st.markdown("---")
                else:
                    # AQUÍ ESTÁ LA CLAVE: ahora el mensaje de error te dirá EXACTAMENTE qué pasó
                    st.error(f"❌ {periodo}")
