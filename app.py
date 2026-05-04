import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Intelligence Hub Editorial Max", page_icon="📰", layout="wide")

# --- ESTILOS ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- LIBRERÍA MAESTRA DE TEMAS (Expandida) ---
# He organizado esto por categorías para que sea la base de datos de la app
all_themes = {
    # --- TECNOLOGÍA Y FUTURO ---
    "🤖 IA: Generativa": "ChatGPT\nClaude\nGemini\nMidjourney\nLLM\nPrompts",
    "🤖 IA: Ética y Regulación": "Regulación IA\nDerechos de Autor IA\nSesgos Algorítmicos\nLey de IA UE",
    "💻 Computación Cuántica": "Quantum Computing\nQubits\nCriptografía Cuántica\nSupercomputadoras",
    "🌐 Web3 y Blockchain": "Ethereum\nSmart Contracts\nDeFi\nDAO\nWeb3",
    "🪙 Criptomonedas: Bitcoin": "Bitcoin\nHalving\nSatoshi\nMinería BTC",
    "🪙 Criptomonedas: Altcoins": "Solana\nCardano\nPolkadot\nStablecoins",
    "📱 Hardware y Chips": "Nvidia\nTSMC\nApple Silicon\nSemicondutores\nARM",
    "🚀 Carrera Espacial": "SpaceX\nNASA\nArtemis\nStarlink\nMarte\nJames Webb",
    "🛡️ Ciberseguridad": "Ransomware\nZero Day\nPhishing\nPentesting\nSoberanía Digital",
    "🕶️ Metaverso y VR": "Vision Pro\nOculus\nRealidad Aumentada\nVR Gaming",

    # --- ECONOMÍA Y FINANZAS ---
    "📈 Macroeconomía": "Inflación\nPIB\nRecesión\nBancos Centrales\nDeflación",
    "🇪🇺 Economía Europea": "BCE\nEuribor\nEurozona\nPolíticas Fiscales UE",
    "🇺🇸 Economía USA": "FED\nWall Street\nS&P 500\nNasdaq\nDeuda USA",
    "🛢️ Energía y Materias Primas": "Petróleo\nGas Natural\nLitio\nCobalto\nOro",
    "🏢 Startups y Venture Capital": "Unicornios\nSaaS\nSeed Funding\nSérie A\nScaleups",
    "🛒 E-commerce y Retail": "Amazon\nShopify\nLogística\nDropshipping\nOmnicanalidad",
    "🏦 Fintech": "Neobancos\nPagos Digitales\nOpen Banking\nInsurtech",
    "🌾 Agroeconomía": "Precios Cereales\nSostenibilidad Agrícola\nFertilizantes",

    # --- POLÍTICA Y GEOPOLÍTICA ---
    "🇺🇸 Política Estados Unidos": "Elecciones USA\nCongreso\nCasa Blanca\nDemócratas\nRepublicanos",
    "🇪🇺 Política Unión Europea": "Parlamento Europeo\nComisión Europea\nTratados UE\nSchengen",
    "🇪🇸 Política España": "Gobierno España\nCortes Generales\nComunidades Autónomas",
    "🌏 Geopolítica Asia": "China\nTaiwán\nCorea del Norte\nJapón\nASEAN",
    "🌍 Geopolítica Medio Oriente": "Israel\nIrán\nArabia Saudí\nConflicto Gaza\nPetrodólares",
    "🇷🇺 Geopolítica Rusia": "Rusia\nUcrania\nOTAN\nSanciones Económicas",
    "🇺🇳 Organismos Internacionales": "ONU\nFMI\nBanco Mundial\nOMS\n Interpol",
    "⚖️ Derechos Humanos": "Amnistía Internacional\nLibertad de Expresión\nRefugiados",

    # --- CIENCIA Y SALUD ---
    "🧬 Genética y Biotecnología": "CRISPR\nEdición Genética\nClonación\nSintéticos",
    "🧠 Neurociencia": "Cerebro\nSinapsis\nInterfaz Cerebro-Computadora\nNeuralink",
    "💊 Farmacéutica": "Vacunas\nAntisense\nEnsayos Clíníncos\nFDA",
    "🏥 Salud Mental": "Ansiedad\nDepresión\nBurnout\nPsicología Moderna",
    "🦠 Epidemiología": "Virus\nZoonosis\nSistemas de Vigilancia Sanitaria",
    "🔭 Astrofísica": "Agujeros Negros\nExoplanetas\nMateria Oscura\nBig Bang",

    # --- MEDIO AMBIENTE ---
    "🌡️ Cambio Climático": "Calentamiento Global\nAcuerdo de París\nCOP28\nEmisiones CO2",
    "☀️ Energías Renovables": "Hidrógeno Verde\nSolar\nEólica\nFusión Nuclear",
    "🌊 Oceanografía": "Acidificación Océanos\nCorales\nPlásticos Marinos",
    "🌲 Biodiversidad": "Deforestación\nEspecies en Peligro\nRewilding",

    # --- DEPORTES Y CULTURA ---
    "⚽ Fútbol": "Champions League\nLaLiga\nPremier League\nFichajes\nMundial",
    "🏎️ Motor": "Fórmula 1\nFerrari\nRed Bull\nMotoGP",
    "🎾 Tenis y Otros": "ATP\nWTA\nOlimpiadas\nNBA\nNFL",
    "🎬 Cine y Streaming": "Netflix\nOscars\nDisney+\nBox Office\nCine Independiente",
    "🎮 Gaming": "PlayStation\nXbox\nNintendo\nSteam\nE-sports",
    "🎨 Arte y Literatura": "Museos\nNovela Gráfica\nSaaS Art\nSotheby's",
}

# --- LÓGICA DE BÚSQUEDA ---
def obtener_noticias(api_key, keywords):
    query = ' OR '.join(keywords)
    url = f"https://newsapi.org/v2/everything?q={query}&language=es&sortBy=publishedAt&apiKey={api_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get('articles', [])
        return []
    except Exception:
        return []

# --- SEGURIDAD ---
api_key = st.secrets.get("NEWS_API_KEY", None)
if api_key is None:
    st.error("❌ Error: API Key no configurada en Secrets.")
    st.stop()

# --- SIDEBAR ---
st.sidebar.title("⚙️ Control Hub")

# BUSCADOR DINÁMICO DE TEMAS
st.sidebar.subheader("🔍 Buscador de Temas")
search_query = st.sidebar.text_input("Escribe el tema (ej. 'IA', 'Bolsa', 'Sora')")

# Filtrado inteligente de la librería
filtered_presets = {k: v for k, v in all_themes.items() if search_query.lower() in k.lower()}
preset_options = list(filtered_presets.keys())

if preset_options:
    selected_preset = st.sidebar.selectbox("Selecciona el set", preset_options)
    if st.sidebar.button("Cargar Temas"):
        st.session_state['current_keywords'] = filtered_presets[selected_preset]
else:
    st.sidebar.warning("No hay sets que coincidan.")

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Ajuste Manual")
default_val = st.session_state.get('current_keywords', "Inteligencia Artificial\nEconomía")
keywords_input = st.sidebar.text_area("Palabras clave", value=default_val)
keywords_list = [k.strip() for k in keywords_input.split('\n') if k.strip()]

st.sidebar.caption("v6.0 - Maximalist Intelligence Hub")

# --- CUERPO PRINCIPAL ---
st.title("📰 Intelligence Hub Editorial")
st.markdown("Acceso masivo a tendencias globales y vigilancia de medios.")

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
    st.subheader("Análisis de Medios Digitales")
    num_results = st.slider("Cantidad de noticias", 5, 50, 20)

    if st.button("🔍 Ejecutar Rastreo"):
        if not keywords_list:
            st.warning("Introduce palabras clave.")
        else:
            with st.spinner('Analizando fuentes globales...'):
                noticias = obtener_noticias(api_key, keywords_list)
                if noticias:
                    st.success(f"Capturadas {len(noticias)} noticias.")
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
                                st.write(f"**{art['source']['name']}** | {art['publishedAt'][:10]}")
                                st.write(art['description'])
                            with c2:
                                st.markdown(f"[Leer completo ↗️]({art['url']})")
                            st.markdown("---")
                else:
                    st.error("No se encontraron noticias.")







