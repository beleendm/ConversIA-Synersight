import streamlit as st
import os
import pandas as pd
import google.generativeai as genai
from pypdf import PdfReader
from datetime import datetime

# --- CONFIGURACIÓN DE SEGURIDAD ---
try:
    # Leemos la API Key desde los Secrets de Streamlit
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("❌ Error de configuración: Verifica la API Key en los Secrets de Streamlit.")
    st.stop()

# --- ESTILO SYNERSIGHT ---
st.set_page_config(page_title="ConversIA Enterprise", layout="centered")
st.markdown("<style>.stButton>button { background-color: #004a99; color: white; }</style>", unsafe_allow_html=True)

# --- LOGIN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔐 Acceso ConversIA")
    user = st.text_input("Usuario")
    pw = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if (user == "admin" and pw == "synersight2026") or (user == "tecnico" and pw == "agv2026"):
            st.session_state.autenticado = True
            st.session_state.usuario = user
            st.rerun()
        else:
            st.error("Credenciales incorrectas")
    st.stop()

# --- FUNCIONES RAG ---
def extraer_conocimiento():
    contexto = ""
    if not os.path.exists("conocimiento"):
        os.makedirs("conocimiento")
    for arc in os.listdir("conocimiento"):
        ruta = os.path.join("conocimiento", arc)
        try:
            if arc.endswith(".pdf"):
                lector = PdfReader(ruta)
                for pag in lector.pages:
                    contexto += pag.extract_text()
            elif arc.endswith(".txt"):
                with open(ruta, "r", encoding="utf-8") as f:
                    contexto += f.read()
            contexto += f"\n[Fuente: {arc}]\n"
        except: pass
    return contexto

# --- INTERFAZ DE CHAT ---
st.title("🤖 ConversIA - Synersight")
with st.sidebar:
    st.write(f"👤 Usuario: {st.session_state.usuario}")
    if st.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

pregunta = st.text_area("Describa la incidencia técnica:", placeholder="Ej: Fallo en el cofre de baterías...")

if st.button("GENERAR SOLUCIÓN"):
    if not pregunta:
        st.warning("Escriba una pregunta.")
    else:
        with st.spinner("Consultando manuales internos..."):
            contexto = extraer_conocimiento()
            # Usamos el modelo 'gemini-1.5-flash' que es el más rápido y moderno
            model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
            
            prompt = f"Eres un experto de Synersight. Usa SOLO este contexto: {contexto}. Pregunta: {pregunta}. Si no lo sabes, di que avisarás a la oficina de Valladolid."
            
            try:
                # Quitamos la configuración de temperatura compleja para evitar fallos
                res = model.generate_content(prompt)
                st.subheader("📋 Diagnóstico Oficial")
                st.write(res.text)
                
                # Guardar historial
                log = pd.DataFrame([{"Fecha": datetime.now(), "User": st.session_state.usuario, "Pregunta": pregunta}])
                log.to_csv("historial.csv", mode='a', header=not os.path.exists("historial.csv"), index=False)
                st.toast("Incidencia registrada para la oficina.")
            except Exception as e:
                st.error(f"Error técnico: {e}")
