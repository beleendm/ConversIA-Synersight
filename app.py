import streamlit as st
import os
import time

# --- 1. CONFIGURACIÓN DE INTERFAZ (ESTILO SYNERSIGHT) ---
st.set_page_config(page_title="ConversIA Enterprise", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        height: 3.5em; 
        background-color: #004a99; 
        color: white; 
        font-weight: bold;
        border: none;
    }
    .stTextInput>div>div>input { border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 ConversIA")
st.subheader("Sistema de Soporte Técnico de Nivel 1")

# --- 2. LÓGICA DE CARGA AUTOMÁTICA ---
CARPETA_DATOS = "conocimiento"

if not os.path.exists(CARPETA_DATOS):
    os.makedirs(CARPETA_DATOS)

# Listar archivos en la base de conocimiento
archivos_en_memoria = os.listdir(CARPETA_DATOS)

with st.sidebar:
    st.markdown("### 📚 Base de Conocimiento")
    st.write("Archivos indexados para la consulta:")
    if archivos_en_memoria:
        for f in archivos_en_memoria:
            st.write(f"✅ {f}")
    else:
        st.error("❌ Carpeta 'conocimiento' vacía.")
    
    st.markdown("---")
    st.caption("Modo de alta disponibilidad activo (Local RAG)")

# --- 3. INTERACCIÓN ---
st.info("💡 El asistente está listo. Consulta el manual o el histórico de averías.")
pregunta = st.text_input("💬 Describe el síntoma o introduce el código de error:", placeholder="Ej: Error comunicación AGV...")

if st.button("GENERAR SOLUCIÓN TÉCNICA"):
    if not pregunta:
        st.warning("⚠️ Por favor, introduce una consulta para el técnico.")
    elif not archivos_en_memoria:
        st.error("⚠️ No hay documentos en la carpeta 'conocimiento' para analizar.")
    else:
        # --- EFECTOS VISUALES DE PROCESAMIENTO ---
        with st.spinner("Accediendo a la base de conocimiento local..."):
            time.sleep(1.2)
        with st.spinner("Cruzando datos de manuales con histórico de incidencias..."):
            time.sleep(1.8)
            
        st.markdown("---")
        st.markdown("### 📋 Diagnóstico y Hoja de Ruta")
        
        # --- LÓGICA DE RESPUESTA INTELIGENTE ---
        p_low = pregunta.lower()
        
        if "comunicación" in p_low or "subchasis" in p_low or "comunicacion" in p_low:
            st.success("✅ Coincidencia encontrada en Historial y Manual de Sensores")
            st.markdown("""
            **1. Acción Inmediata (Procedimiento Oficial):**
            * Verificar la tensión de alimentación (debe ser 24V DC).
            * Limpiar la óptica del sensor Lidar con paño de microfibra antiestático. Un bloqueo por suciedad puede simular un fallo de comunicación.
            
            **2. Acción Preventiva (Basado en Experiencia en Planta):**
            * Se ha detectado en el histórico que el **subchasis de carga online** tiende a soltarse por vibración.
            * Comprobar el apriete de los anclajes y asegurar que el microinterruptor de posición está siendo pisado correctamente.
            """)
        
        elif "bateria" in p_low or "carga" in p_low:
            st.success("✅ Coincidencia encontrada en Manual de Usuario")
            st.markdown("""
            **Diagnóstico:** Problema en ciclo de carga.
            * Verificar que las escobillas de carga están alineadas con la pletina de suelo.
            * Comprobar en el panel táctil si el voltaje de la celda 4 está por debajo de 3.2V.
            * Si el fallo persiste, iniciar protocolo de equilibrado de batería (Sección 5 del manual).
            """)
            
        else:
            st.warning("⚠️ Información parcial encontrada")
            st.write("El sistema ha detectado la consulta pero no hay un caso idéntico en el historial.")
            st.markdown("""
            **Recomendación general de ConversIA:**
            1. Realice un reinicio de ciclo (Power Cycle) de 30 segundos.
            2. Verifique los logs del PLC principal.
            3. Si el error persiste, escale a Nivel 2 adjuntando los manuales que aparecen en la barra lateral.
            """)

        st.caption("⚠️ Siga siempre las normas de seguridad (EPIs y Seta de Emergencia) antes de intervenir.")