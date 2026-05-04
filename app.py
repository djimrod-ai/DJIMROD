import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Intelligence Hub Editorial", page_icon="📰", layout="wide")

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- LIBRERÍA DE SETS (Expandible) ---
# Aquí puedes añadir cientos de categorías. Al ser un diccionario, es muy eficiente.
ALL_PRESETS = {
    " Economía": "Bolsa\nInflación\nBCE\nEuribor\nFiscalidad\nPIB",
    " Tecnología": "IA\nChatGPT\nNvidia\nSemicondutores\nQuantum Computing\nApple",
    " Política Nacional": "Elecciones\nGobierno\nSindicatos\nParlamento\nRegiones",
    " Política Internacional": "ONU\nOTAN\nGeopolítica\nConflictos\nDiplomacia",
    " Medio Ambiente": "Cambio Climático\nEnergía Solar\nSequía\nReciclaje\nCO2",
    " Salud": "Pandemias\nVacunas\nSalud Mental\nBiotecnología\nOMS",
    " Justicia": "Sentencias\nTribunal Supremo\nLeyes\nDerechos Humanos",
    " Deportes": "Champions\nLaLiga\nOlimpiadas\nFichajes\nTenis",
    " Cultura": "Museos\nCine\nLiteratura\nTeatro\nFestivales",
    " Seguridad": "Ciberseguridad\nInteligencia\nDefensa\nPolicía"
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

# --- SEGURIDAD API KEY ---
api_key = st.secrets.get("NEWS_API_KEY", None)
if api_key is None:
    st.error("❌ Error: API Key no configurada en Secrets.")
    st.stop()

# --- GESTIÓN DE ESTADO (Session State) ---
# Esto permite que la app "recuerde" los sets guardados por el usuario durante la sesión
if 'user_presets' not in st.session_state:
    st.session_state['user_presets'] = {}

# --- SIDEBAR ---
st.sidebar.title(" Panel de Control")

# 1. BUSCADOR DE SETS DINÁMICO
st.sidebar.subheader(" Buscar Set Temático")
search_query = st.sidebar.text_input("Escribe el tema (ej. 'Tecno' o 'Polít')")

# Filtrar la librería basándose en la búsqueda
filtered_presets = {k: v for k, v in ALL_PRESETS.items() if search_query.lower() in k.lower()}
preset_options = list(filtered_presets.keys())

if preset_options:
    selected_preset = st.sidebar.selectbox("Selecciona un set encontrado", preset_options)
    if st.sidebar.button("Cargar Set"):
        st.session_state['current_keywords'] = filtered_presets[selected_preset]
else:
    st.sidebar.warning("No se encontraron sets con ese nombre.")

# 2. GESTIÓN DE PALABRAS CLAVE
st.sidebar.markdown("---")
st.sidebar.subheader(" Ajuste de Temas")

# Si hay un set cargado, lo ponemos como valor por defecto
default_val = st.session_state.get('current_keywords', "Inteligencia Artificial\nEconomía")
keywords_input = st.sidebar.text_area("Palabras clave (una por línea)", value=default_val)
keywords_list = [k.strip() for k in keywords_input.split('\n') if k.strip()]

# 3. GUARDADO de SETS PERSONALIZADOS (Súper útil para el usuario)
st.sidebar.markdown("---")
st.sidebar.subheader(" Guardar Set Actual")
new_set_name = st.sidebar.text_input("Nombre para este grupo")
if st.sidebar.button("Guardar en mi sesión"):
    if new_set_name and keywords_input:
        st.session_state['user_presets'][new_set_name] = keywords_input
        st.sidebar.success(f"Set '{new_set_name}' guardado!")

# Mostrar sets guardados por el usuario en esta sesión
if st.session_state['user_presets']:
    st.sidebar.subheader(" Mis Sets Guardados")
    for name in st.session_state['user_presets'].keys():
        if st.sidebar.button(f"Cargar {name}"):
            st.session_state['current_keywords'] = st.session_state['user_presets'][name]
            st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("v3.0 - Dynamic Intelligence Hub")

# --- CUERPO PRINCIPAL ---
st.title(" Intelligence Hub Editorial")
st.markdown("Sistemas de monitorización de tendencias y vigilancia de medios en tiempo real.")

tab1, tab2 = st.tabs([" Vigilancia de Medios", " Tendencias en X"])

with tab2:
    st.subheader("Explorador de Redes Sociales")
    st.write("Acceso instantáneo a la conversación actual en X (Twitter).")
    if keywords_list:
        cols = st.columns(4)
        for idx, word in enumerate(keywords_list):
            col = cols[idx % 4]
            twitter_url = f"https://twitter.com/search?q={word.replace(' ', '%20')}&f=live"
            with col:
                st.markdown(f"**{word}**")
                st.markdown(f" [Ver en X ]({twitter_url})")
                st.markdown("---")
    else:
        st.info("Añade palabras clave en la barra lateral.")

with tab1:
    st.subheader("Análisis de Medios Digitales")
    num_results = st.slider("Cantidad de noticias a analizar", 5, 50, 20)

    if st.button(" Ejecutar Rastreo de Noticias"):
        if not keywords_list:
            st.warning("Introduce al menos una palabra clave.")
        else:
            with st.spinner('Analizando fuentes globales...'):
                noticias = obtener_noticias(api_key, keywords_list)
                if noticias:
                    st.success(f"Se han capturado {len(noticias)} artículos relevantes.")
                    df = pd.DataFrame(noticias)[['title', 'source', 'publishedAt', 'url']]
                    df.columns = ['Título', 'Fuente', 'Fecha', 'Enlace']
                    
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(" Descargar Reporte en CSV", data=csv, 
                                     file_name=f"reporte_{datetime.now().strftime('%Y%m%d')}.csv", mime='text/csv')
                    
                    st.dataframe(df, use_container_width=True)
                    st.markdown("---")
                    st.subheader(" Análisis Detallado")
                    for art in noticias[:num_results]:
                        with st.container():
                            c1, c2 = st.columns([3, 1])
                            with c1:
                                st.markdown(f"### [{art['title']}]({art['url']})")
                                st.write(f"**{art['source']['name']}** | {art['publishedAt'][:10]}")
                                st.write(art['description'])
                            with c2:
                                st.markdown(f"[Leer completo ]({art['url']})")
                            st.markdown("---")
                else:
                    st.error("No se encontraron noticias recientes.")
    else:
        st.info("Haz clic en 'Ejecutar Rastreo' para obtener los datos actualizados.")




