import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import xml.etree.ElementTree as ET

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Intelligence Hub Editorial Max", page_icon="📰", layout="wide")

# --- ESTILOS CSS PREMIUM ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stButton>button { width: 100%; border-radius: 12px; font-weight: bold; background-color: #1E3A8A !important; color: white !important; }
    .news-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border-left: 6px solid #1E3A8A;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
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
    .main-title {
        color: #1E3A8A;
        font-weight: 800;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LIBRERÍA DE RSS EXPANDIDA (Fuentes Españolas y Globales) ---
RSS_FEEDS = {
    "El País": "https://www.elpais.com/rss/0/latest.xml",
    "El Mundo": "https://www.elmundo.es/rss/estC1.xml",
    "ABC": "https://www.abc.es/rss/noticias.xml",
    "RTVE": "https://www.rtve.es/rss/todas-las-noticias.rss",
    "BBC Mundo": "https://www.bbc.com/mundo/index.xml",
    "EFE": "https://www.efe.com/rss/estatico/todas.xml",
    "La Vanguardia": "https://www.lavanguardia.com/rss/ultima-hora",
    "El Confidencial": "https://www.elconfidencial.com/rss",
    "El Español": "https://www.elespanol.com/rss/",
    "Diario de Sevilla": "https://www.diariodesevilla.es/rss/noticias.xml", # Intento de acceso directo
}

# --- LIBRERÍA MAESTRA DE TEMAS (SÚPER EXPANDIDA) ---
all_themes = {
    # TECNOLOGÍA E IA
    "🤖 IA y Futuro": "ChatGPT\nClaude\nGemini\nSora\nIA\nInteligencia Artificial\nAlgoritmos\nRobótica",
    "💻 Tecnología y Chips": "Nvidia\nApple\nSemicondutores\nHardware\nSoftware\nComputación Cuántica",
    "🪙 Cripto y Web3": "Bitcoin\nEthereum\nBlockchain\nSolana\nCripto\nDeFi",
    "🛡️ Ciberseguridad": "Hacking\nPhishing\nPrivacidad\nSoberanía Digital\nMalware",
    
    # ECONOMÍA Y NEGOCIOS
    "📈 Macroeconomía": "Inflación\nPIB\nRecesión\nBCE\nEuribor\nEconomía\nBolsa\nFinanzas",
    "🏢 Empresas y Startups": "Unicornios\nSaaS\nInversión\nEmprendimiento\nS&P500\nNasdaq",
    "🛒 Comercio y Retail": "Amazon\nE-commerce\nConsumo\nLogística\nRetail",
    
    # POLÍTICA Y GEOPOLÍTICA
    "🌍 Geopolítica Global": "Rusia\nUcrania\nChina\nOTAN\nIsrael\nGaza\nEEUU\nConflictos",
    "🇪🇸 Política España": "Sánchez\nCortes Generales\nGobierno\nAutonomías\nElecciones",
    "🇺🇸 Política USA": "Trump\nBiden\nCongreso\nCasa Blanca\nDemócratas\nRepublicanos",
    "🇺🇳 Diplomacia y ONU": "Naciones Unidas\nFMI\nBanco Mundial\nTratados\nDerechos Humanos",
    
    # SOCIEDAD Y CULTURA
    "👥 Sociedad y Actualidad": "Huelgas\nSindicatos\n Pensiones\nEducación\nSalud Pública",
    "⚖️ Justicia y Leyes": "Tribunal Supremo\nSentencias\nLeyes\nJusticia\nConstitución",
    "🎨 Cultura y Ocio": "Cine\nLiteratura\nTeatro\nArte\nFestivales\nstreaming",
    "🏥 Salud y Ciencia": "Vacunas\nBiotecnología\nOMS\nCáncer\nMedicina\nGenética",
    
    # MEDIO AMBIENTE
    "🌱 Ecología y Clima": "Cambio Climático\nEnergía Solar\nCOP28\nCO2\nSostenibilidad\nSequía",
    
    # DEPORTES
    "⚽ Fútbol": "Champions\nLaLiga\nPremier League\nFichajes\nReal Madrid\nBarça",
    "🏎️ Motor y Otros": "Fórmula 1\nFerrari\nRed Bull\nTenis\nOlimpiadas\nNBA",
}

# --- LÓGICA de BÚSQUEDA GLOBAL (Google News) ---
def obtener_noticias_google(keywords):
    todas_las_noticias = []
    # Unimos las keywords para una búsqueda masiva
    query = ' OR '.join(keywords).replace(' ', '+')
    # Buscamos en Google News ( la fuente más completa de la web)
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
    st.error("❌ API Key no configurada en Secrets.")
    st.stop()

# --- SIDEBAR ---
st.sidebar.markdown("<h2 style='color: #1E3A8A;'>⚙️ Control Hub</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")
search_query = st.sidebar.text_input("🔍 Buscar tema maestro")
filtered_presets = {k: v for k, v in all_themes.items() if search_query.lower() in k.lower()}
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
st.markdown("<p style='text-align: center; color: #6B7280; margin-bottom: 30px;'>Vigilancia de medios de alta precisión: Google News + NewsAPI + Redes Sociales</p>", unsafe_allow_html=True)

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

with tab1:
    col_config1, col_config2 = st.columns([2, 1])
    with col_config1:
        modo = st.radio("Motor de Búsqueda:", ["Google News (Búsqueda Global)", "Global (NewsAPI)"], index=0, horizontal=True)
    with col_config2:
        num_results = st.slider("Cantidad de noticias", 5, 100, 20)

    if st.button("🔍 Ejecutar Rastreo de Inteligencia"):
        if not keywords_list:
            st.warning("Introduce palabras clave.")
        else:
            with st.spinner('Escaneando la red de medios...'):
                if modo == "Global (NewsAPI)":
                    noticias_full, periodo = obtener_noticias_api(api_key, keywords_list)
                else:
                    noticias_full = obtener_noticias_google(keywords_list)
                    periodo = "Google News (Búsqueda Global)"
                
                if noticias_full:
                    noticias = noticias_full[:num_results]
                    
                    # --- DASHBOARD DE MÉTRICAS ---
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Noticias Encontradas", len(noticias))
                    m2.metric("Fuentes Únicas", len(set([n['source'] for n in noticias])))
                    m3.metric("Estado", "Sincronizado")
                    
                    st.markdown("---")
                    
                    df = pd.DataFrame(noticias)[['title', 'source', 'publishedAt', 'url']]
                    df.columns = ['Título', 'Fuente', 'Fecha', 'Enlace']
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Descargar Reporte CSV", data=csv, 
                                     file_name=f"reporte_{datetime.now().strftime('%Y%m%d')}.csv", mime='text/csv')
                    st.dataframe(df, use_container_width=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    
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
                    st.error(f"No se han encontrado noticias mediante {modo}.")
