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
    .reportview-container .main .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

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

# --- SIDEBAR ---
st.sidebar.title(" Panel de Control")

# SISTEMA DE PRESETS (Mejora de UX)
st.sidebar.subheader(" Sets Rápidos")
presets = {
    "Economía": "Bolsa\nInflación\nBCE\nEuribor",
    "Tecnología": "IA\nChatGPT\nNvidia\nSemicondutores",
    "Política": "Elecciones\nGobierno\nSindicatos\nDiplomacia",
    "Medio Ambiente": "Cambio Climático\nEnergía Solar\nSequía\nReciclaje"
}

selected_preset = st.sidebar.selectbox("Cargar set de temas", ["Seleccionar..."] + list(presets.keys()))

# Input de palabras clave
st.sidebar.subheader(" Temas Personalizados")
default_text = presets[selected_preset] if selected_preset in presets else "Inteligencia Artificial\nEconomía"
keywords_input = st.sidebar.text_area("Temas (uno por línea)", value=default_text)
keywords_list = [k.strip() for k in keywords_input.split('\n') if k.strip()]

st.sidebar.markdown("---")
st.sidebar.caption("v2.0 - Intelligence Hub Editorial")

# --- CUERPO PRINCIPAL ---
st.title("Intelligence Hub Editorial")
st.markdown("Sistemas de monitorización de tendencias y vigilancia de medios en tiempo real.")

# CREACIÓN DE PESTAÑAS (Mejora de Organización)
tab1, tab2 = st.tabs([" Vigilancia de Medios", " Tendencias en X"])

with tab2:
    st.subheader("Explorador de Redes Sociales")
    st.write("Acceso instantáneo a la conversación actual en X (Twitter).")
    
    if keywords_list:
        cols = st.columns(4) # Máximo 4 por fila para mejor legibilidad
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
    
    # Filtro de cantidad de resultados
    num_results = st.slider("Cantidad de noticias a analizar", 5, 50, 20)

    if st.button(" Ejecutar Rastreo de Noticias"):
        if not keywords_list:
            st.warning("Introduce al menos una palabra clave.")
        else:
            with st.spinner('Analizando fuentes globales...'):
                noticias = obtener_noticias(api_key, keywords_list)
                
                if noticias:
                    st.success(f"Se han capturado {len(noticias)} artículos relevantes.")
                    
                    # Procesamiento de datos con Pandas
                    df = pd.DataFrame(noticias)[['title', 'source', 'publishedAt', 'url']]
                    df.columns = ['Título', 'Fuente', 'Fecha', 'Enlace']
                    
                    # Botón de descarga (Mejora de Valor Empresarial)
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label=" Descargar Reporte en CSV",
                        data=csv,
                        file_name=f"reporte_tendencias_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime='text/csv',
                    )
                    
                    # Tabla de resultados
                    st.dataframe(df, use_container_width=True)
                    
                    st.markdown("---")
                    st.subheader("Análisis Detallado")
                    
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
                    st.error("No se encontraron noticias recientes con esos criterios.")
    else:
        st.info("Haz clic en 'Ejecutar Rastreo' para obtener los datos actualizados.")



