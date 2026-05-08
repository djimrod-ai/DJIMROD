import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import feedparser

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Intelligence Hub Editorial Pro", page_icon="📰", layout="wide")

# --- ESTILOS ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- LIBRERÍA de RSS (Toda la inmediatez aquí) ---
RSS_FEEDS = {
    "El País": "https://www.elpais.com/rss/0/latest.xml",
    "El Mundo": "https://www.elmundo.es/rss/estC1.xml",
    "ABC": "https://www.abc.es/rss/noticias.xml",
    "RTVE": "https://www.rtve.es/rss/todas-las-noticias.rss",
    "BBC Mundo": "https://www.bbc.com/mundo/index.xml",
    "EFE": "https://www.efe.com/rss/estatico/todas.xml"
}

# --- LIBRERÍA MAESTRA DE TEMAS ---
all_themes = {
    "🤖 IA: Generativa": "ChatGPT\nClaude\nGemini\nMidjourney\nLLM\nSora\nPrompts",
    "🤖 IA: Ética": "Regulación IA\nDerechos de Autor IA\nSesgos Algorítmicos\nLey de IA UE",
    "🪙 Criptomonedas": "Bitcoin\nEthereum\nSolana\nHalving\nStablecoins",
    "📈 Macroeconomía": "Inflación\nPIB\nRecesión\nBCE\nEuribor",
    "🇺🇸 Política USA": "Elecciones USA\nTrump\nBiden\nCongreso",
    "🇪🇸 Política España": "Gobierno España\nSánchez\nCortes Generales",
    "🌍 Geopolítica": "Rusia\nUcrania\nChina\nOTAN\nIsrael\nGaza",
    "🌱 Medio Ambiente": "Cambio Climático\nEnergía Solar\nCOP28\nCO2",
    "⚽ Deportes": "Champions\nLaLiga\nFichajes\nF1\nTenis",
    "🎮 Gaming y Tech": "PlayStation\nXbox\nNvidia\nApple\nGaming",
}

# --- LÓGICA DE BÚSQUEDA 1: NewsAPI (Búsqueda Global) ---
def obtener_noticias_api(api_key, keywords):
    query = ' OR '.join(keywords)
    today = datetime.now().strftime('%Y-%m-%d')
    url = f"https://newsapi.org/v2/everything?q={query}&language=es&sortBy=publishedAt&from={today}&apiKey={api_key}"
    
    try:
        res = requests.get(url)
        if res.status_code == 200:
            art = res.json().get('articles', [])
            if art: return art, "Hoy (API)"
        
        # Fallback a 48h
        from_date = (datetime.now() - pd.Timedelta(days=2)).strftime('%Y-%m-%d')
        url_rec = f"https://newsapi.org/v2/everything?q={query}&language=es&sortBy=publishedAt&from={from_date}&apiKey={api_key}"
        res_rec = requests.get(url_rec)
        if res_rec.status_code == 200:
            return res_rec.json().get('articles', []), "Últimas 48h (API)"
    except: pass
    return [], "Sin resultados"

# --- LÓGICA DE BÚSQUEDA 2: RSS (Tiempo Real) ---
def obtener_noticias_rss(keywords):
    noticias_reales = []
    for medio, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                if any(word.lower() in entry.title.lower() or word.lower() in entry.summary.lower() for word in keywords):
                    noticias_reales.append({
                        'title': entry.title,
                        'url': entry.link,
                        'source': medio,
                        'publishedAt': entry.published if hasattr(entry, 'published') else "Reciente",
                        'description': entry.summary if hasattr(entry, 'summary') else ""
                    })
        except: pass
    return noticias_reales, "Tiempo Real (RSS)"

# --- SEGURIDAD ---
api_key = st.secrets.get("NEWS_API_KEY", None)
if api_key is None:
    st.error("❌ API Key no configurada.")
    st.stop()

# --- SIDEBAR ---
st.sidebar.title("⚙️ Control Hub")
search_query = st.sidebar.text_input("🔍 Buscar tema (ej. 'IA')")
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
keywords_input = st.sidebar.text_area("Ajuste de palabras clave", value=default_val)
keywords_list = [k.strip() for k in keywords_input.split('\n') if k.strip()]

# --- CUERPO PRINCIPAL ---
st.title("📰 Intelligence Hub Editorial")
st.markdown("Vigilancia de medios híbrida: Global (API) + Instantánea (RSS).")

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
    st.subheader("Buscador de Noticias")
    
    # Selector de modo de búsqueda
    modo = st.radio("Selecciona la fuente de datos:", ["Global (NewsAPI)", "Instantánea (RSS Feeds)"], horizontal=True)
    
    num_results = st.slider("Cantidad de noticias", 5, 50, 20)

    if st.button("🔍 Ejecutar Rastreo"):
        if not keywords_list:
            st.warning("Introduce palabras clave.")
        else:
            with st.spinner('Buscando la información más reciente...'):
                if modo == "Global (NewsAPI)":
                    noticias, periodo = obtener_noticias_api(api_key, keywords_list)
                else:
                    noticias, periodo = obtener_noticias_rss(keywords_list)
                
                if noticias:
                    st.success(f"Capturadas {len(noticias)} noticias. Periodo: {periodo}")
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
                                st.write(f"**{art['source']}** | {art['publishedAt']}")
                                st.write(art['description'])
                            with c2:
                                st.markdown(f"[Leer completo ↗️]({art['url']})")
                            st.markdown("---")
                else:
                    st.error("No se han encontrado noticias recientes para estos temas.")





