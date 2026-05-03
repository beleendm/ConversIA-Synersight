import streamlit as st
import os
import pandas as pd
import google.generativeai as genai
from pypdf import PdfReader
from datetime import datetime

# --- CONFIGURACIÓN DE SEGURIDAD ---
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ Configura 'GOOGLE_API_KEY' en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- ESTILO Y LOGIN ---
st.set_page_config(page_title="ConversIA Synersight", layout="centered")

if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Acceso ConversIA")
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if (u == "admin" and p == "synersight2026") or (u == "tecnico" and p == "agv2026"):
            st.session_state.auth = True
            st.session_state.user = u
            st.rerun()
        else:
            st.error("Credenciales incorrectas")
    st.stop()

# --- FUNCIONES ---
def leer_conocimiento():
    texto = ""
    if not os.path.exists("conocimiento"):
        os.makedirs("conocimiento")
    for f in os.listdir("conocimiento"):
        path = os.path.join("conocimiento", f)
        try:
            if f.endswith(".pdf"):
                reader = PdfReader(path)
                for page in reader.pages:
                    texto += page.extract_text()
            elif f.endswith(".txt"):
                with open(path, "r", encoding="utf-8") as file:
                    texto += file.read()
            texto += f"\n--- FIN DE ARCHIVO: {f} ---\n"
        except: pass
    return texto

# --- INTERFAZ ---
st.title("🤖 ConversIA - Soporte Synersight")
st.sidebar.write(f"👤 {st.session_state.user}")

query = st.text_area("Describe el síntoma o código de error:")

if st.button("GENERAR SOLUCIÓN"):
    if not query:
        st.warning("Introduce una consulta.")
    else:
        with st.spinner("Buscando en manuales..."):
            ctx = leer_conocimiento()
            # USAMOS EL MODELO MÁS ESTABLE
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"Eres experto de Synersight. Usa SOLO este texto: {ctx}. Pregunta: {query}. Si no lo sabes, di que no aparece en manuales."
            
            try:
                res = model.generate_content(prompt)
                st.subheader("📋 Diagnóstico")
                st.write(res.text)
                
                # Registro para oficina
                log_file = "historial.csv"
                nuevo_log = pd.DataFrame([{"Fecha": datetime.now(), "Técnico": st.session_state.user, "Fallo": query}])
                nuevo_log.to_csv(log_file, mode='a', header=not os.path.exists(log_file), index=False)
                st.toast("✅ Registrado para la oficina")
            except Exception as e:
                st.error(f"Error del motor: {e}")

if st.sidebar.checkbox("Ver registros oficina"):
    if os.path.exists("historial.csv"):
        st.dataframe(pd.read_csv("historial.csv"))
