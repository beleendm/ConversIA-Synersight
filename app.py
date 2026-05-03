import streamlit as st
import os
import pandas as pd
import google.generativeai as genai
from pypdf import PdfReader
from datetime import datetime


# =========================================================
# 1. CONFIGURACIÓN Y SEGURIDAD
# =========================================================

# NO pongas la llave aquí. La leeremos de los secretos de Streamlit.
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except KeyError:
    st.error("❌ No se encontró la API Key. Configura 'GOOGLE_API_KEY' en los Secrets de Streamlit.")
    st.stop()
# Configuración de página
st.set_page_config(page_title="ConversIA - Synersight Support", layout="centered")

# Estilo visual empresarial
st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; }
    .stButton>button { width: 100%; background-color: #004a99; color: white; border-radius: 10px; height: 3em; font-weight: bold; }
    .stTextInput>div>div>input { border-radius: 10px; }
    .report-box { padding: 15px; border-radius: 10px; background-color: #e9ecef; border-left: 5px solid #004a99; }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE LOGIN SENCILLO ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

def login():
    st.title("🔐 Acceso ConversIA")
    st.write("Introduzca sus credenciales de Synersight")
    user = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        # En producción, usar una base de datos real. Aquí validamos datos básicos.
        if (user == "admin" and password == "synersight2026") or (user == "tecnico" and password == "agv2026"):
            st.session_state.autenticado = True
            st.session_state.usuario = user
            st.rerun()
        else:
            st.error("Credenciales incorrectas")

# =========================================================
# 2. FUNCIONES DE PROCESAMIENTO DE DATOS
# =========================================================

def extraer_texto_conocimiento(carpeta="conocimiento"):
    """Lee PDFs y TXTs de la carpeta y los une en un contexto."""
    contexto_total = ""
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)
        return ""
    
    for archivo in os.listdir(carpeta):
        ruta = os.path.join(carpeta, archivo)
        try:
            if archivo.endswith(".pdf"):
                reader = PdfReader(ruta)
                texto_pdf = ""
                for page in reader.pages:
                    texto_pdf += page.extract_text()
                contexto_total += f"\n[FUENTE: {archivo}]\n{texto_pdf}\n"
            elif archivo.endswith(".txt"):
                with open(ruta, "r", encoding="utf-8") as f:
                    contexto_total += f"\n[FUENTE: {archivo}]\n{f.read()}\n"
        except Exception as e:
            print(f"Error leyendo {archivo}: {e}")
    return contexto_total

def guardar_en_historial(pregunta, respuesta, usuario):
    """Archiva la consulta para que la oficina la vea por la mañana."""
    archivo_log = "historial_consultas.csv"
    nueva_fila = {
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Usuario": usuario,
        "Consulta": pregunta,
        "Respuesta_IA": respuesta[:200] + "...", # Guardamos un resumen
        "Estatus": "Pendiente de revisión Oficina"
    }
    df = pd.DataFrame([nueva_fila])
    if not os.path.isfile(archivo_log):
        df.to_csv(archivo_log, index=False, encoding='utf-8')
    else:
        df.to_csv(archivo_log, mode='a', header=False, index=False, encoding='utf-8')

# =========================================================
# 3. INTERFAZ PRINCIPAL DEL ASISTENTE
# =========================================================

if not st.session_state.autenticado:
    login()
else:
    # Sidebar con información técnica
    with st.sidebar:
        st.image("https://www.synersight.es/wp-content/uploads/2021/05/logo-synersight.png", width=150) # Logo genérico o el tuyo
        st.markdown(f"**Usuario:** {st.session_state.usuario}")
        if st.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📄 Archivos Indexados")
        docs = os.listdir("conocimiento")
        for d in docs:
            st.caption(f"✅ {d}")
        
        st.markdown("---")
        if st.checkbox("Ver Historial (Oficina)"):
            if os.path.exists("historial_consultas.csv"):
                st.dataframe(pd.read_csv("historial_consultas.csv"))
            else:
                st.write("No hay registros aún.")

    # Pantalla de Chat
    st.title("🤖 ConversIA Prototipo")
    st.info(f"Hola {st.session_state.usuario}. El sistema está listo para consultar manuales y el historial de averías de Synersight.")

    pregunta = st.text_area("💬 Describe la incidencia o el código de error:", placeholder="Ej: Error 212 en motor de tracción...", height=100)

    if st.button("GENERAR DIAGNÓSTICO"):
        if not pregunta:
            st.warning("⚠️ Por favor, introduce una pregunta.")
        else:
            with st.spinner("Buscando en documentos internos de Synersight..."):
                # 1. Extraer conocimiento
                contexto = extraer_texto_conocimiento()
                
                if not contexto:
                    st.error("La carpeta 'conocimiento' está vacía. Sube archivos a GitHub.")
                else:
                    # 2. Configurar el modelo (Temperatura 0 para máxima fidelidad)
                    model = genai.GenerativeModel('models/gemini-1.5-flash')
                    
                    # 3. El Prompt restrictivo 100% fiel
                    prompt_instrucciones = f"""
                    ERES: Un Ingeniero Senior de Soporte de Synersight (Valladolid).
                    TU MISIÓN: Ayudar a un técnico de campo a resolver una avería usando SOLO documentos internos.
                    
                    DOCUMENTACIÓN INTERNA DISPONIBLE:
                    {contexto}
                    
                    CONSULTA DEL TÉCNICO:
                    {pregunta}
                    
                    REGLAS DE ORO (ESTRICTAS):
                    1. Si la solución NO ESTÁ en la documentación proporcionada, di: "Lo siento, este caso no aparece en los manuales internos. He registrado la incidencia para que el equipo de oficina la revise a las 07:00 AM."
                    2. NO uses conocimiento externo o general.
                    3. Si encuentras la solución, indica siempre de qué archivo la has sacado (ej: 'Según el Manual_AGV.pdf...').
                    4. Divide la respuesta en: 'Diagnóstico' y 'Pasos a seguir'.
                    """
                    
                    try:
                        response = model.generate_content(prompt_instrucciones, generation_config={"temperature": 0.0})
                        respuesta_final = response.text
                        
                        # Mostrar resultado
                        st.markdown("### 📋 Resultado del Análisis")
                        st.markdown(respuesta_final)
                        
                        # 4. Archivar automáticamente para la oficina
                        guardar_en_historial(pregunta, respuesta_final, st.session_state.usuario)
                        st.toast("Consulta archivada para revisión de oficina.")
                        
                    except Exception as e:
                        st.error(f"Error de conexión con el motor de IA: {e}")

    st.markdown("---")
    st.caption("🔒 Este sistema utiliza información confidencial de Synersight. Queda prohibida su divulgación.")
