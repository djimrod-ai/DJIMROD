import subprocess
import sys

# --- PARCHE DE EMERGENCIA PARA LIBRERÍAS ---
# Esto instala feedparser automáticamente si la nube de Streamlit no lo hace
try:
    import feedparser
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "feedparser"])
    import feedparser

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import feedparser # <--- Esto es lo que dará error si el requirements.txt no funciona

# ... el resto del código sigue igual ...


# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Intelligence Hub Editorial Pro", page_icon="📰", layout="wide")

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 20px; }
    .news-card {
        padding: 15px;
        border-radius: 10px;
        background-color: white;
        border-left: 5px solid #1DA1F2;
        margin-bottom: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- LIBRERÍA DE RSS (Tiempos reales: 0 lag) ---
RSS_FEEDS = {
    "El País": "https://www.elpais.com/rss/0/latest.xml",
    "El Mundo": "https://www.elmundo.es/rss/estC1.xml",
    "ABC": "https://www.abc.es/rss/noticias.xml",
    "RTVE": "https://www.rtve.es/rss/todas-las-noticias.rss",
    "BBC Mundo": "https://www.bbc.com/mundo/index.xml",
    "EFE": "https://www.efe.com/rss/estatico/todas.xml"
}

# --- LIBRERÍA MAESTRA DE TEMAS (Categorías optimizadas) ---
all_themes = {
    "🤖 IA: Generativa": "ChatGPT\nClaude\nGemini\nMidjourney\nLLM\nSora\nPrompts",
    "🤖 IA: Ética": "Regulación IA\nDerechos de Autor IA\nSesgos Algorítmicos\nLey de IA UE",
    "💻 Computación Cuántica": "Quantum Computing\nQubits\nCriptografía Cuántica\nSupercomputadoras",
    "🌐 Web3 y Blockchain": "Ethereum\nSmart Contracts\nDeFi\nDAO\nWeb3",
    "🪙 Criptomonedas: Bitcoin": "Bitcoin\nHalving\nSatoshi\nMinería BTC",
    "🪙 Criptomonedas: Altcoins": "Solana\nCardano\nPolkadot\nStablecoins",
    "📱 Hardware y Chips": "Nvidia\nTSMC\nApple Silicon\nSemicondutores\nARM",
    "🚀 Carrera Espacial": "SpaceX\nNASA\nArtemis\nStarlink\nMarte\nJames Webb",
    "🛡️ Ciberseguridad": "Ransomware\nZero Day\nPhishing\nPentesting\nSoberanía Digital",
    "🕶️ Metaverso y VR": "Vision Pro\nOculus\nRealidad Aumentada\nVR Gaming",
    "📈 Macroeconomía": "Inflación\nPIB\nRecesión\nBancos Centrales\nDeflación",
    "🇪🇺 Economía Europea": "BCE\nEuribor\nEurozona\nPolíticas Fiscales UE",
    "🇺🇸 Economía USA": "FED\nWall Street\nS&P 500\nNasdaq\nDeuda USA",
    "🛢️ Energía": "Petróleo\nGas Natural\nLitio\nCobalto\nOro",
    "🏢 Startups": "Unicornios\nSaaS\nSeed Funding\nSérie A\nScaleups",
    "🇺🇸 Política USA": "Elecciones USA\nTrump\nBiden\nCongreso",
    "🇪🇸 Política España": "Gobierno España\nSánchez\nCortes Generales",
    "🌍 Geopolítica": "Rusia\nUcrania\nChina\nOTAN\nIsrael\nGaza",
    "🌱 Medio Ambiente": "Cambio Climático\nEnergía Solar\nCOP28\nCO2",
    "⚽ Deportes": "Champions\nLaLiga\nFichajes\nF1\nTenis",
    "🎮 Gaming y Tech": "PlayStation\nXbox\nNintendo\nSteam\nE-sports",
}

# --- LÓGICA de BÚSQUEDA GLOBAL (SISTEMA EN CASCADA) ---
def obtener_noticias_api(api_key, keywords):
    query = ' OR '.join(keywords)
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Intento 1: Solo HOY
    url_hoy = f"https://newsapi.org/v2/everything?q={query}&language=es&sortBy=publishedAt&from={today}&apiKey={api_key}"
    try:
        res = requests.get(url_hoy)
        if res.status_code == 200:
            art = res.json().get('articles', [])
            if art: return art, "Hoy (API)"
        
        # Intento 2: Últimas 48h
        from_date = (datetime.now() - pd.Timedelta(days=2)).strftime('%Y-%m-%d')
        url_rec = f"https://newsapi.org/v2/everything?q={query}&language=es&sortBy=publishedAt&from={from_date}&apiKey={api_key}"
        res_rec = requests.get(url_rec)
        if res_rec.status_code == 200:
            return res_rec.json().get('articles', []), "Últimas 48h (API)"
            
        # Intento 3: Histórico relevante
        url_gen = f"https://newsapi.org/v2/everything?q={query}&language=es&sortBy=relevancy&apiKey={api_key}"
        res_gen = requests.get(url_gen)
        if res_gen.status_code == 200:
            return res_gen.json().get('articles', []), "Histórico Relevante (API)"
    except: pass
    return [], "Sin resultados"

# --- LÓGICA DE BÚSQUEDA RSS (TIEMPO REAL) ---
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
    st.error("❌ Error: API Key no configurada en Secrets.")
    st.stop()

# --- SIDEBAR ---
st.sidebar.title("⚙️ Control Hub")
search_query = st.sidebar.text_input("🔍 Buscar tema (ej. 'IA', 'Bolsa')")
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

st.sidebar.caption("v7.5 - Final Enterprise Edition")

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
    modo = st.radio("Selecciona la fuente de datos:", ["Global (NewsAPI)", "Instantánea (RSS Feeds)"], horizontal=True)
    num_results = st.slider("Cantidad de noticias a mostrar", 5, 50, 20)

    if st.button("🔍 Ejecutar Rastreo"):
        if not keywords_list:
            st.warning("Introduce palabras clave.")
        else:
            with st.spinner('Analizando fuentes...'):
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
                                     file_name=f"tendencias_{datetime.now().strftime('%Y%m%d')}.csv", mime='text/csv')
                    
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
                    st.error("No se encontraron noticias recientes para estos temas.")




