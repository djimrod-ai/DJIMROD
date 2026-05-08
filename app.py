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

# --- LIBRERÍA de RSS AMPLIADA (Más fuentes = más noticias) ---
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

# --- LÓGICA de BÚSQUEDA GLOBAL ---
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

# --- LÓGICA de BÚSQUEDA RSS (MAXIMIZADA) ---
def obtener_noticias_rss(keywords):
    noticias_coincidentes = []
    todas_las_recientes = []
    
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
                    todas_las_recientes.append(noticia)
                    
                    if any(word.lower() in title.lower() or word.lower() in desc.lower() for word in keywords):
                        noticias_coincidentes.append(noticia)
        except: pass
    
    # Si tenemos muchas coincidencias, las damos todas. 
    # Si tenemos POCAS (menos de 5), mezclamos con las más recientes para rellenar la página.
    if len(noticias_coincidentes) >= 3:
        return noticias_coincidentes, "Tiempo Real (Coincidencias Exactas)"
    else:
        # Combinamos las pocas coincidencias con las noticias generales más frescas
        final_list = noticias_coincidentes + todas_las_recientes[:15]
        # Eliminamos duplicados por URL
        seen = set([n['url'] for n in final_list])
        unique_list = [x for i, x in enumerate(final_list) if i == 0 or x['url'] not in seen[:i]]
        return unique_list, "Modo Radar (Mix: Coincidencias + Actualidad)"

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
st.markdown("Sonda de tiempo real: **Filtro Hoy** + **Súper RSS Expandido**.")

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
            with st.spinner('Analizando fuentes...'):
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
                            c1, c2 = st.columns([3, 1])
                            with c1:
                                st.markdown(f"### [{art['title']}]({art['url']})")
                                st.write(f"**{art['source']}** | {art['publishedAt']}")
                                st.write(art['description'])
                            with c2:
                                st.markdown(f"[Leer completo ↗️]({art['url']})")
                            st.markdown("---")
                else:
                    st.error(f"No se han encontrado noticias hoy mediante {modo}.")

                else:
                    st.error(f"No se han encontrado noticias hoy mediante {modo}.")
