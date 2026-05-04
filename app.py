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
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE BÚSQUEDA ---
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

# Sidebar (Barra lateral)
st.sidebar.title(" Configuración")
api_key = st.secrets["NEWS_API_KEY"]
st.sidebar.markdown("---")
st.sidebar.info("Consigue tu API Key gratis en [newsapi.org](https://newsapi.org/)")

# Selector de palabras clave
st.sidebar.subheader(" Palabras Clave")
keywords_input = st.sidebar.text_area(
    "Introduce los temas (uno por línea)", 
    "Inteligencia Artificial\nEconomía\nElecciones\nClima"
)
keywords_list = [k.strip() for k in keywords_input.split('\n') if k.strip()]

# Título Principal
st.title(" Monitor de Tendencias Editoriales")
st.markdown("Esta herramienta rastrea las noticias más recientes basadas en los temas de interés del periódico.")

# Botón de búsqueda
if st.button(" Buscar Tendencias Actuales"):
    if not api_key:
        st.warning("Por favor, introduce la API Key en la barra lateral.")
    elif not keywords_list:
        st.warning("Por favor, introduce al menos una palabra clave.")
    else:
        with st.spinner('Rastreando la web...'):
            noticias = obtener_noticias(api_key, keywords_list)
            
            if noticias:
                st.success(f"Se han encontrado {len(noticias)} noticias relevantes.")
                
                # Creamos un DataFrame para mostrar un resumen rápido
                df = pd.DataFrame(noticias)[['title', 'source', 'publishedAt', 'url']]
                df.columns = ['Título', 'Fuente', 'Fecha', 'Enlace']
                
                # Mostramos la tabla resumida
                st.subheader(" Resumen de hallazgos")
                st.dataframe(df, use_container_width=True)
                
                st.markdown("---")
                st.subheader(" Detalle de las noticias")
                
                # Mostramos las noticias como "Tarjetas"
                for art in noticias[:10]: # Limitamos a las 10 mejores para no saturar
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"### [{art['title']}]({art['url']})")
                            st.write(f"**Fuente:** {art['source']['name']} | **Fecha:** {art['publishedAt'][:10]}")
                            st.write(art['description'])
                        with col2:
                            st.markdown(f"[Leer noticia completa ↗]({art['url']})")
                        st.markdown("---")
            else:
                st.error("No se encontraron noticias con esos criterios.")

else:
    st.info("Haz clic en el botón de búsqueda para analizar las tendencias.")
