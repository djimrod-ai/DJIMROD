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
    .match-tag { background-color: #d4edda; color: #155724; padding: 2px 8px; border-radius: 5px; font-size: 12px; font-weight: bold; }
    .general-tag { background-color: #e2e3e5; color: #383d41; padding: 2px 8px;C border-radius: 5px; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- LIBRERÍA DE RSS AMPLIADA (Máxima cobertura) ---
RSS_FEEDS = {
    "El País": "https://www.elpais.com/rss/0/latest.xml",
    "El Mundo": "https://www.elmundo.es/rss/estC1.xml",
    "ABC": "https://www.abc.es/rss/noticias.xml",
    "RTVE": "https://www.rtve.es/rss/todas-las-noticias.rss",
    "BBC Mundo": "https://www.bbc.com/mundo/index.xml",
    "EFE": "https://www.efe.com/rss/estatico/todas.xml",
    "La Vanguardia": "https://www.lavanguardia.com/rss/ultima-hora",
    "El Confidencial": "https://www.elconfidencial.com/rss",
}

# --- LIBRERÍA MAESTRA de TEMAS (Súper Optimizada) ---
all_themes = {
    "🤖 IA: Generativa": "ChatGPT\nClaude\nGemini\nSora\nIA\nInteligencia Artificial\nAlgoritmo",
    "🪙 Criptomonedas": "Bitcoin\nEthereum\nCripto\nBlockchain\nBtc\nHalving",
    "📈 Economía": "Bolsa\nInflación\nBCE\nEuribor\nEconomía\nPIB\nFinanzas",
    "🌍 Geopolítica": "Rusia\nUcrania\nChina\nOTAN\nIsrael\nGaza\nGuerra\nConflicto",
    "🌱 Medio Ambiente": "Clima\nSolar\nCO2\nSostenibilidad\nEcología\nMedio Ambiente",
    "⚽ Deportes": "Champions\nLaLiga\nFichajes\nF1\nDeportes\nFútbol",
    "🎮 Gaming y Tech": "PlayStation\nXbox\nNvidia\nApple\nTecnología\nGaming",
}

# --- LÓGICA NewsAPI (ESTRICTA) ---
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

# --- LÓGICA RSS (SÚPER-SENSIBLE) ---
def obtener_noticias_rss(keywords):
    noticias_finales = []
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
                    
                    # BUSCADA SENSIBLE: Convertimos todo a minúsculas para evitar fallos
                    texto_analizar = (title + " " + desc).lower()
                    es_match = any(word.lower() in texto_analizar for word in keywords)
                    
                    tipo = "⭐ MATCH" if es_match else "🕒 ACTUALIDAD"
                    noticia = {'title': title, 'url': link, 'source': medio, 'publishedAt': date, 'description': desc, 'tipo': tipo}
                    noticias_finales.append(noticia)
        except: pass
    
    # Ordenamos para que los MATCH estén siempre arriba
    noticias_finales.sort(key=lambda x: x['tipo'], reverse=True)
    
    if noticias_finales:
        return noticias_finales, "Tiempo Real (Híbrido)"
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
                    st.dataframe(df, use_container_width=True)
                    st.markdown("---")
                    st.subheader("📄 Análisis Detallado")
                    for art in noticias[:num_results]:
                        with st.container():
                            tipo = art.get('tipo', 'API')
                            # Etiqueta visual
                            tag = f'<span class="match-label">{tipo}</span>' if "MATCH" in tipo else f'<span class="general-label">{tipo}</span>'
                            st.markdown(tag, unsafe_allow_html=True)
                            st.markdown(f"### [{art['title']}]({art['url']})")
                            st.write(f"**{art['source']}** | {art['publishedAt']}")
                            st.write(art['description'])
                            st.markdown("---")
                else:
                    st.error(f"No se han encontrado noticias hoy mediante {modo}.")



