# --- CÓDIGO DE EMERGENCIA AUTO-REPARABLE ---
try:
    # 1. Listamos TODOS los modelos que tu nueva llave puede ver
    modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # 2. Elegimos el mejor disponible (priorizamos flash, luego pro)
    modelo_a_usar = ""
    for m in modelos:
        if "gemini-1.5-flash" in m:
            modelo_a_usar = m
            break
    if not modelo_a_usar and modelos:
        modelo_a_usar = modelos[0] # Si no hay flash, usa el primero que funcione
    
    if modelo_a_usar:
        model = genai.GenerativeModel(modelo_a_usar)
        st.sidebar.success(f"Cerebro conectado: {modelo_a_usar}")
    else:
        st.error("No se encontraron modelos disponibles para esta API Key.")
        st.stop()
        
except Exception as e:
    st.error(f"Error crítico de conexión: {e}")
    st.stop()

# --- DENTRO DEL BOTÓN DE GENERAR SOLUCIÓN ---
if st.button("GENERAR SOLUCIÓN"):
    # ... (tu código de extraer_conocimiento)
    try:
        # Llamada directa con el modelo detectado
        res = model.generate_content(prompt)
        st.subheader("📋 Diagnóstico")
        st.write(res.text)
        # ... (tu código de guardado en historial)
    except Exception as e:
        st.error(f"El modelo {modelo_a_usar} devolvió un error: {e}")
