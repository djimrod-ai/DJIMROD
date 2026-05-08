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

# --- LÓGICA de GOOGLE NEWS RSS (Buscador Global) ---
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
                
                source = "la web"
                if " - " in title:
                    parts = title.split(" - ")
                    source = parts[-1]
                    title = " - ".join(parts[:-1])

                todas_las_noticias.append({
                    'title': title,
                    'url': link,
                    'source': source,
                    'publishedAt': date,
                    'description': desc
                })
    except Exception as e:
        st.error(f"Error conectando con Google News: {e}")
        
    return todas_las_noticias

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

# --- SEGURIDAD ---
api_key = st.secrets.get("NEWS_API_KEY", None)
if api_key is None:
    st.error("❌ Error: API Key no configurada en Secrets.")
    st.stop()

# --- LIBRERÍA de TEMAS ---
all_themes = {
    "🤖 IA: Generativa": "ChatGPT\nClaude\nGemini\nMidjourney\nLLM\nSora\nPrompts\nInteligencia Artificial",
    "🪙 Criptomonedas": "Bitcoin\nEthereum\nSolana\nHalving\nStablecoins\nCripto",
    "📈 Macroeconomía": "Inflación\nPIB\nRecesión\nBCE\nEuribor\nEconomía\nBolsa",
    "🌍 Geopolítica": "Rusia\nUcrania\nChina\nOTAN\nIsrael\nGaza\nConflictos",
    "🌱 Medio Ambiente": "Cambio Climático\nEnergía Solar\nCOP28\nCO2\nSostenibilidad",
    "⚽ Deportes": "Champions\nLaLiga\nFichajes\nF1\nTenis\nDeportes",
    "🎮 Gaming y Tech": "PlayStation\nXbox\nNintendo\nSteam\nE-sports\nTecnología",
}

# --- SIDEBAR ---
st.sidebar.title("⚙️ Control Hub")
st.sidebar.success("✅ Buscador Global Activo")
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
st.markdown("Vigilancia de medios: **Buscador Global de Google** + **Sonda de Actualidad**.")

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
                    ["Google News (Súper Búsqueda)", "Global (NewsAPI)"], 
                    index=0, horizontal=True)
    
    # El slider ahora controla la cantidad de datos procesados
    num_results = st.slider("Cantidad de noticias a mostrar", 5, 100, 20)

    if st.button("🔍 Ejecutar Rastreo"):
        if not keywords_list:
            st.warning("Introduce palabras clave.")
        else:
            with st.spinner('Buscando en toda la web...'):
                if modo == "Global (NewsAPI)":
                    noticias_full, periodo = obtener_noticias_api(api_key, keywords_list)
                else:
                    noticias_full = obtener_noticias_google(keywords_list)
                    periodo = "Google News (Toda la Web)"
                
                if noticias_full:
                    # --- CORRECCIÓN CLAVE: Limitamos la lista ANTES de crear el DataFrame ---
                    noticias = noticias_full[:num_results]
                    
                    st.success(f"Resultado: {periodo} ({len(noticias)} noticias mostradas)")
                    
                    # Ahora el DataFrame solo tiene el número de noticias del slider
                    df = pd.DataFrame(noticias)[['title', 'source', 'publishedAt', 'url']]
                    df.columns = ['Título', 'Fuente', 'Fecha', 'Enlace']
                    
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Descargar CSV", data=csv, 
                                     file_name=f"tendencias_{datetime.now().strftime('%Y%m%d')}.csv", mime='text/csv')
                    
                    st.dataframe(df, use_container_width=True)
                    st.markdown("---")
                    st.subheader("📄 Análisis Detallado")
                    
                    # El bucle ya usa la lista limitada
                    for art in noticias:
                        with st.container():
                            st.markdown(f"### [{art['title']}]({art['url']})")
                            st.write(f"**{art['source']}** | {art['publishedAt']}")
                            st.write(art['description'])
                            st.markdown("---")
                else:
                    st.error(f"No se han encontrado noticias hoy mediante {modo}.")
