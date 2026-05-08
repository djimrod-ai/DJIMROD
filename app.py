import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import xml.etree.ElementTree as ET

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Intelligence Hub Editorial", page_icon="📰", layout="wide")

# --- CSS PERSONALIZADO (EL SECRETO DE LA INTERFAZ) ---
st.markdown("""
    <style>
    /* Fondo general y fuente */
    .main { background-color: #f0f2f6; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* Estilo de las tarjetas de noticias */
    .news-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border-left: 6px solid #1E3A8A;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .news-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    /* Etiquetas de fuente y fecha */
    .source-tag {
        background-color: #E0E7FF;
        color: #4338CA;
        padding: 2px 10px;
        border-radius: 10px;
        font-size: 0.8rem;
        font-weight: bold;
        text-transform: uppercase;
    }
    .date-tag {
        color: #6B7280;
        font-size: 0.8rem;
        margin-left: 10px;
    }
    
    /* Botones personalizados */
    .stButton>button {
        background-color: #1E3A8A !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        transition: all 0.3s !important;
    }
    .stButton>button:hover {
        background-color: #3B82F6 !important;
        transform: scale(1.02);
    }
    
    /* Títulos estilizados */
    .main-title {
        color: #1E3A8A;
        font-weight: 800;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE DATOS (Sigue siendo la misma potencia) ---
RSS_FEEDS = {
    "El País": "https://www.elpais.com/rss/0/latest.xml",
    "El Mundo": "https://www.elmundo.es/rss/estC1.xml",
    "ABC": "https://www.abc.es/rss/noticias.xml",
    "RTVE": "https://www.rtve.es/rss/todas-las-noticias.rss",
    "BBC Mundo": "https://www.bbc.com/mundo/index.xml",
    "EFE": "https://www.efe.com/rss/estatico/todas.xml",
}

all_themes = {
    "🤖 IA: Generativa": "ChatGPT\nClaude\nGemini\nMidjourney\nLLM\nSora\nPrompts\nInteligencia Artificial",
    "🪙 Criptomonedas": "Bitcoin\nEthereum\nSolana\nHalving\nStablecoins\nCripto",
    "📈 Macroeconomía": "Inflación\nPIB\nRecesión\nBCE\nEuribor\nEconomía\nBolsa",
    "🌍 Geopolítica": "Rusia\nUcrania\nChina\nOTAN\nIsrael\nGaza\nConflictos",
    "🌱 Medio Ambiente": "Cambio Climático\nEnergía Solar\nCOP28\nCO2\nSostenibilidad",
    "⚽ Deportes": "Champions\nLaLiga\nFichajes\nF1\nTenis\nDeportes",
    "🎮 Gaming y Tech": "PlayStation\nXbox\nNintendo\nSteam\nE-sports\nTecnología",
}

def obtener_noticias_google(keywords):
    todas_las_noticias = []
    query = ' OR '.join(keywords).replace(' ', '+')
    url = f"https://news.google.com/rss/search?q={query}&hl=es-ES&gl=ES&ceid=ES:es"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            for item in root.findall('.//item'):
                title = item.find('title').text if item.find('title') is not None else "Sin título"
                link = item.find('link').text if item.find('link') is not None else "#"
                date = item.find('pubDate').text if item.find('pubDate') is not None else "Reciente"
                desc = item.find('description').text if item.find('description') is not None else "Sin descripción"
                source = " la web"
                if " - " in title:
                    parts = title.split(" - ")
                    source = parts[-1]
                    title = " - ".join(parts[:-1])
                todas_las_noticias.append({'title': title, 'url': link, 'source': source, 'publishedAt': date, 'description': desc})
    except: pass
    return todas_las_noticias

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

# --- SEGURIDAD ---
api_key = st.secrets.get("NEWS_API_KEY", None)
if api_key is None:
    st.error("❌ API Key no configurada en Secrets.")
    st.stop()

# --- SIDEBAR ---
st.sidebar.markdown("<h2 style='color: #1E3A8A;'>⚙️ Panel de Control</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")
search_query = st.sidebar.text_input("🔍 Buscar tema maestro")
filtered_presets = {k: v for k, vL in all_themes.items() if search_query.lower() in k.lower()}
preset_options = list(filtered_presets.keys())

if preset_options:
    selected_preset = st.sidebar.selectbox("Selecciona un Set", preset_options)
    if st.sidebar.button("Cargar Temas"):
        st.session_state['current_keywords'] = filtered_presets[selected_preset]
else:
    st.sidebar.warning("No hay sets que coincidan.")

st.sidebar.markdown("---")
default_val = st.session_state.get('current_keywords', "Inteligencia Artificial\nEconomía")
keywords_input = st.sidebar.text_area("Ajuste manual de palabras clave", value=default_val)
keywords_list = [k.strip() for k in keywords_input.split('\n') if k.strip()]

# --- CUERPO PRINCIPAL ---
st.markdown("<h1 class='main-title'>📰 Intelligence Hub Editorial</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #6B7280; margin-bottom: 30px;'>Vigilancia de medios la más avanzada: Datos Globales + Inmediatez de Redes</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🌐 Vigilancia de Medios", "🚀 Tendencias en X"])

with tab2:
    st.subheader("Explorador de Redes Sociales")
    if keywords_list:
        cols = st.columns(4)
        for idx, word in enumerate(keywords_list):
            col = cols[idx % 4]
            twitter_url = f"https://twitter.com/search?q={word.replace(' ', '%20')}&f=live"
            with col:
                st.markdown(f"""
                    <div style="background-color:white; padding:15px; border-radius:15px; border: 1px solid #E5E7EB; text-align:center; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
                        <b style="color:#1E3A8A;">{word}</b><br>
                        <a href="{twitter_url}" target="_blank" style="text-decoration:none; color:#1DA1F2; font-weight:bold;">Ver en X ↗️</a>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("Añade palabras clave en la barra lateral.")

with tab1:
    col_config1, col_config2 = st.columns([2, 1])
    with col_config1:
        modo = st.radio("Motor de Búsqueda:", ["Google News (Súper Búsqueda)", "Global (NewsAPI)"], index=0, horizontal=True)
    with col_config2:
        num_results = st.slider("Cantidad de noticias", 5, 100, 20)

    if st.button("🔍 Ejecutar Rastreo de Inteligencia"):
        if not keywords_list:
            st.warning("Introduce palabras clave.")
        else:
            with st.spinner('Procesando datos globales...'):
                if modo == "Global (NewsAPI)":
                    noticias_full, periodo = obtener_noticias_api(api_key, keywords_list)
                else:
                    noticias_full = obtener_noticias_google(keywords_list)
                    periodo = "Google News (Toda la Web)"
                
                if noticias_full:
                    noticias = noticias_full[:num_results]
                    
                    # --- DASHBOARD DE MÉTRICAS ---
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Noticias Encontradas", len(noticias))
                    m2.metric("Fuentes", len(set([n['source'] for n in noticias])))
                    m3.metric("Estado", "Actualizado")
                    
                    st.markdown("---")
                    
                    # Descarga de CSV
                    df = pd.DataFrame(noticias)[['title', 'source', 'publishedAt', 'url']]
                    df.columns = ['Título', 'Fuente', 'Fecha', 'Enlace']
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Descargar Reporte CSV", data=csv, 
                                     file_name=f"reporte_{datetime.now().strftime('%Y%m%d')}.csv", mime='text/csv')
                    
                    st.dataframe(df, use_container_width=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # --- RENDERIZADO DE TARJETAS PREMIUM ---
                    st.subheader("📄 Análisis Detallado")
                    for art in noticias:
                        st.markdown(f"""
                            <div class="news-card">
                                <span class="source-tag">{art['source']}</span>
                                <span class="date-tag">{art['publishedAt']}</span>
                                <h3 style="margin-top:10px;">
                                    <a href="{art['url']}" target="_blank" style="text-decoration:none; color:#1E3A8A;">{art['title']}</a>
                                </h3>
                                <p style="color:#4B5563; line-height:1.6;">{art['description']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.error(f"No se encontraron noticias mediante {modo}.")
