import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Monitor de Tendencias Editorial", page_icon="📰", layout="wide")

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stAlert {
        border-radius: 10px;
    }
    .social-link {
        display: inline-block;
        padding: 5px 10px;
        background-color: #1DA1F2;
        color: white !important;
        border-radius: 15px;
        text-decoration: none;
        font-weight: bold;
        font-size: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE BÚSQUEDA (NewsAPI) ---
def obtener_noticias(api_key, keywords):
    # Unimos las palabras clave con ' OR ' para que la API busque cualquiera de ellas
    query = ' OR '.join(keywords)
    url = f"https://newsapi.org/v2/everything?q={query}&language=es&sortBy=publishedAt&apiKey={api_key}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get('articles', [])
        else:
            st.error(f"Error en la API: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return []

# --- INTERFAZ DE USUARIO (UI) ---

# 1. Gestión de Seguridad de la API Key
try:
    # Intentamos obtener la llave de los secretos de Streamlit Cloud
    api_key = st.secrets.get("NEWS_API_KEY", None)
    if api_key is None:
        st.error(" Error de configuración: No se encontró 'NEWS_API_KEY' en los secretos del servidor.")
        st.stop()
except Exception as e:
    st.error(f"Error crítico al acceder a los secretos: {e}")
    st.stop()

# 2. Sidebar (Barra lateral)
st.sidebar.title(" Configuración")
st.sidebar.markdown("---")
st.sidebar.info("Este monitor utiliza NewsAPI y enlaces dinámicos de X.")

# Selector de palabras clave
st.sidebar.subheader(" Palabras Clave")
keywords_input = st.sidebar.text_area(
    "Introduce los temas (uno por línea)", 
    "Inteligencia Artificial\nEconomía\nElecciones\nClima"
)
keywords_list = [k.strip() for k in keywords_input.split('\n') if k.strip()]

# 3. Título Principal
st.title("📰 Monitor de Tendencias Editoriales")
st.markdown("Herramienta de inteligencia de contenidos para rastrear noticias y redes sociales en tiempo real.")

# 4. SECCIÓN DE REDES SOCIALES (ACCESO RÁPIDO A X/TWITTER)
st.markdown("---")
st.subheader(" Explorador de Redes Sociales")
st.write("Haz clic en los temas para ver lo más reciente en X (Twitter) en tiempo real.")

if keywords_list:
    # Creamos columnas dinámicamente según el número de palabras clave (máximo 5 por fila)
    cols = st.columns(5 if len(keywords_list) >= 5 else len(keywords_list))
    
    for idx, word in enumerate(keywords_list):
        col = cols[idx % len(cols)]
        # Generamos la URL de Twitter con el filtro 'f=live' para ver lo más reciente
        twitter_url = f"https://twitter.com/search?q={word.replace(' ', '%20')}&f=live"
        with col:
            # Usamos un botón de Streamlit que redirige a la URL
            st.markdown(f"**{word}**")
            st.markdown(f" [Ver en X ]({twitter_url})")
else:
    st.info("Introduce palabras clave en la barra lateral para generar los accesos directos a X.")

st.markdown("---")

# 5. SECCIÓN DE NOTICIAS WEB (NEWSAPI)
st.subheader(" Vigilancia de Medios Digitales")
st.write("Búsqueda automatizada en agencias de noticias y periódicos web.")

# Botón de búsqueda
if st.button(" Buscar Tendencias Actuales"):
    if not keywords_list:
        st.warning("Por favor, introduce al menos una palabra clave en la barra lateral.")
    else:
        with st.spinner('Rastreando la web...'):
            noticias = obtener_noticias(api_key, keywords_list)
            
            if noticias:
                st.success(f"Se han encontrado {len(noticias)} noticias relevantes.")
                
                # DataFrame de resumen
                df = pd.DataFrame(noticias)[['title', 'source', 'publishedAt', 'url']]
                df.columns = ['Título', 'Fuente', 'Fecha', 'Enlace']
                st.dataframe(df, use_container_width=True)
                
                st.markdown("---")
                st.subheader(" Detalle de las noticias")
                
                # Tarjetas de noticias
                for art in noticias[:10]:
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"### [{art['title']}]({art['url']})")
                            st.write(f"**Fuente:** {art['source']['name']} | **Fecha:** {art['publishedAt'][:10]}")
                            st.write(art['description'])
                        with col2:
                            st.markdown(f"[Leer noticia completa]({art['url']})")
                        st.markdown("---")
            else:
                st.error("No se encontraron noticias con esos criterios.")

else:
    st.info("Haz clic en el botón de búsqueda para analizar los medios digitales.")


