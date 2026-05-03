import streamlit as st
import os
import pandas as pd
import google.generativeai as genai
from pypdf import PdfReader
from datetime import datetime

# --- 1. SEGURIDAD (SECRETS) ---
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠️ Configura 'GOOGLE_API_KEY' en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# --- 2. CONFIGURACIÓN DE PÁGINA Y LOGIN ---
st.set_page_config(page_title="ConversIA - Synersight", layout="centered")

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

# --- 3. CONEXIÓN AL CEREBRO (AUTO-REPARABLE) ---
try:
    # Listamos modelos disponibles para evitar el error 404
    modelos_visibles = [m.name for m in genai.list_models()]
    # Buscamos el nombre exacto que Google le da al modelo en tu región
    modelo_final = "models/gemini-1.5-flash" if "models/gemini-1.5-flash" in modelos_visibles else modelos_visibles[0]
    model = genai.GenerativeModel(modelo_final)
    st.sidebar.success(f"✅ Motor conectado")
except Exception as error_inicial:
    st.error(f"Error de conexión inicial: {error_inicial}")
    st.stop()

# --- 4. FUNCIONES TÉCNICAS ---
from docx import Document # Añade esta importación arriba del todo

def leer_documentos():
    contexto = ""
    if not os.path.exists("conocimiento"):
        os.makedirs("conocimiento")
    for f in os.listdir("conocimiento"):
        ruta = os.path.join("conocimiento", f)
        try:
            # LECTURA DE PDF
            if f.endswith(".pdf"):
                reader = PdfReader(ruta)
                for page in reader.pages:
                    contexto += page.extract_text()
            
            # LECTURA DE WORD (.docx)
            elif f.endswith(".docx"):
                doc = Document(ruta)
                for para in doc.paragraphs:
                    contexto += para.text + "\n"
            
            # LECTURA DE TXT
            elif f.endswith(".txt"):
                with open(ruta, "r", encoding="utf-8") as file:
                    texto += file.read()
            
            contexto += f"\n--- FIN DE ARCHIVO: {f} ---\n"
        except Exception as e:
            st.error(f"No se pudo leer {f}: {e}")
    return contexto

# --- 5. INTERFAZ DE CHAT ---
st.title("🤖 ConversIA Prototipo")
st.sidebar.write(f"👤 {st.session_state.user}")

pregunta = st.text_area("Describe el síntoma o código de error:", placeholder="Ej: Error preventivo de baterías...")

if st.button("GENERAR SOLUCIÓN"):
    if not pregunta:
        st.warning("Por favor, escribe una consulta.")
    else:
        with st.spinner("Consultando base de conocimiento de Synersight..."):
            ctx = leer_documentos()
            
            prompt = f"""
            Eres un experto técnico senior de Synersight en Valladolid.
            Tu misión es ayudar a técnicos de campo usando SOLO el contexto de abajo.
            
            CONTEXTO DE MANUALES:
            {ctx}
            
            PREGUNTA TÉCNICA:
            {pregunta}
            
            REGLAS:
            1. Si la solución está en los manuales (ej: 'Preventivo del cofre de baterías'), numera los pasos exactamente como aparecen.
            2. Si no lo sabes, di: "Información no disponible. Avisaré a la oficina de Valladolid."
            3. No inventes pasos. Menciona el nombre del archivo de origen.
            """
            
            try:
                res = model.generate_content(prompt)
                st.subheader("📋 Diagnóstico Oficial")
                st.markdown(res.text)
                
                # ARCHIVADO PARA LA OFICINA (CSV)
                log_file = "historial_casos.csv"
                nuevo_registro = pd.DataFrame([{
                    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Técnico": st.session_state.user,
                    "Incidencia": pregunta
                }])
                nuevo_registro.to_csv(log_file, mode='a', header=not os.path.exists(log_file), index=False)
                st.toast("Caso archivado para revisión matinal.")
                
            except Exception as e:
                st.error(f"Error en la consulta: {e}")

if st.sidebar.checkbox("📂 Ver Historial Oficina"):
    if os.path.exists("historial_casos.csv"):
        st.write("Registros acumulados para revisión:")
        st.dataframe(pd.read_csv("historial_casos.csv"))
    else:
        st.write("No hay incidencias registradas hoy.")
