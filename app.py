import os; os.chdir(os.path.dirname(os.path.abspath(__file__)))
import os
import shutil
from datetime import datetime
import streamlit as st

# ==========================================
# 1. CONFIGURACIÓN E IDIOMAS (Tu motor i18n)
# ==========================================
st.set_page_config(page_title="Tidy - Organizador Inteligente", page_icon="📁", layout="centered")

# Traducciones integradas para que no falle ningún archivo externo
TRADUCCIONES = {
    "Español": {
        "titulo": "📁 Tidy",
        "subtitulo": "Organiza tus archivos académicos y profesionales en segundos",
        "nota_privacidad": "🔒 Proceso 100% local. Tus archivos nunca salen de tu ordenador.",
        "config_titulo": "⚙️ Configuración de Asignaturas / Tópicos",
        "config_ayuda": "Define las palabras clave que debe buscar Tidy en los nombres de tus archivos para clasificarlos.",
        "lbl_ruta": "📂 Pega la ruta de la carpeta que quieres organizar:",
        "placeholder_ruta": "Ejemplo: C:/Usuarios/TuNombre/Descargas",
        "lbl_idioma": "Idioma / Language",
        "btn_analizar": "🔍 Analizar Carpeta",
        "btn_organizar": "🚀 Organizar Archivos Ahora",
        "error_ruta": "La ruta especificada no existe. Por favor, revísala.",
        "error_vacio": "No se encontraron archivos sueltos para organizar en esta carpeta.",
        "exito": "¡Organización completada con éxito! 🎉",
        "resumen_analisis": "📋 Archivos detectados listos para ordenar:",
        "col_archivo": "Archivo",
        "col_destino": "Carpeta Destino (Asignatura/Formato/Fecha)",
    },
    "English": {
        "titulo": "📁 Tidy",
        "subtitulo": "Organize your school and professional files in seconds",
        "nota_privacidad": "🔒 100% local process. Your files never leave your computer.",
        "config_titulo": "⚙️ Subjects / Topics Settings",
        "config_ayuda": "Define the keywords Tidy should look for in file names to classify them.",
        "lbl_ruta": "📂 Paste the folder path you want to organize:",
        "placeholder_ruta": "Example: C:/Users/YourName/Downloads",
        "lbl_idioma": "Idioma / Language",
        "btn_analizar": "🔍 Scan Folder",
        "btn_organizar": "🚀 Organize Files Now",
        "error_ruta": "The specified path does not exist. Please check it.",
        "error_vacio": "No loose files found to organize in this folder.",
        "exito": "Organization completed successfully! 🎉",
        "resumen_analisis": "📋 Files detected ready to organize:",
        "col_archivo": "File",
        "col_destino": "Destination Folder (Subject/Format/Date)",
    }
}

# Selector de idioma en la barra lateral
idioma = st.sidebar.selectbox("Idioma", ["Español", "English"])
t = TRADUCCIONES[idioma]

# ==========================================
# 2. INTERFAZ VISUAL (Estilo Tidy)
# ==========================================
st.title(t["titulo"])
st.subheader(t["subtitulo"])
st.caption(t["nota_privacidad"])

st.write("---")

# Panel de Asignaturas y Palabras Clave (Búsqueda flexible)
st.markdown(f"### {t['config_titulo']}")
st.caption(t["config_ayuda"])

# El usuario puede definir aquí sus asignaturas y qué palabras clave usar
if 'config_asignaturas' not in st.session_state:
    st.session_state.config_asignaturas = {
        "Matemáticas": ["mat", "calculo", "algebra", "mates"],
        "Historia": ["hist", "contemporanea", "siglo"],
        "Programación": ["python", "code", "script", "js", "html"],
        "Trabajo / Proyectos": ["factura", "entrega", "final", "informe"]
    }

# Mostrar la configuración en formato de tabla editable
config_actual = st.session_state.config_asignaturas
nuevas_asignaturas = {}
for asig, palabras in config_actual.items():
    texto_palabras = st.text_input(f"Palabras clave para **{asig}**:", ", ".join(palabras))
    nuevas_asignaturas[asig] = [p.strip().lower() for p in texto_palabras.split(",") if p.strip()]

st.session_state.config_asignaturas = nuevas_asignaturas

st.write("---")

# Input para la ruta de la carpeta
ruta_carpeta = st.text_input(t["lbl_ruta"], placeholder=t["placeholder_ruta"])

# ==========================================
# 3. LÓGICA DEL ALGORITMO (Clasificación)
# ==========================================
def clasificar_archivo(nombre_archivo, ruta_completa):
    nombre_minusculas = nombre_archivo.lower()
    ext = os.path.splitext(nombre_archivo)[1].lower().replace(".", "")
    
    # 1. Determinar Asignatura por palabras clave (Búsqueda Flexible)
    carpeta_asignatura = "Otros"
    for asig, palabras in st.session_state.config_asignaturas.items():
        if any(palabra in nombre_minusculas for palabra in palabras):
            carpeta_asignatura = asig
            break
            
    # 2. Determinar Formato
    formatos = {
        "pdf": "PDFs", "docx": "Documentos", "xlsx": "Documentos", "txt": "Documentos",
        "jpg": "Imágenes", "jpeg": "Imágenes", "png": "Imágenes",
        "zip": "Comprimidos", "rar": "Comprimidos", "mp4": "Videos", "mp3": "Audio"
    }
    carpeta_formato = formatos.get(ext, f"Formatos_{ext.upper()}" if ext else "Sin_Extension")
    
    # 3. Determinar Fecha (Año-Mes)
    try:
        timestamp = os.path.getmtime(ruta_completa)
        fecha = datetime.fromtimestamp(timestamp)
        carpeta_fecha = fecha.strftime("%Y-%m")
    except:
        carpeta_fecha = "Sin_Fecha"
        
    # Retorna la ruta triple junta: Asignatura/Formato/Fecha
    return os.path.join(carpeta_asignatura, carpeta_formato, carpeta_fecha)


# ==========================================
# 4. BOTONES DE ACCIÓN (Escanear y Mover)
# ==========================================
if ruta_carpeta:
    if not os.path.exists(ruta_carpeta):
        st.error(t["error_ruta"])
    else:
        # Analizar archivos válidos
        todos_los_elementos = os.listdir(ruta_carpeta)
        archivos_validos = []
        
        for item in todos_los_elementos:
            ruta_item = os.path.join(ruta_carpeta, item)
            # Solo listamos archivos sueltos (no tocamos carpetas existentes)
            if os.path.isfile(ruta_item) and not item.startswith('.'):
                archivos_validos.append(item)
                
        if not archivos_validos:
            st.info(t["error_vacio"])
        else:
            # Crear previsualización del árbol
            st.markdown(f"#### {t['resumen_analisis']}")
            
            tabla_previa = []
            for arc in archivos_validos:
                destino = clasificar_archivo(arc, os.path.join(ruta_carpeta, arc))
                tabla_previa.append({t["col_archivo"]: arc, t["col_destino"]: destino})
                
            st.table(tabla_previa)
            
            # Botón definitivo para mover los archivos físicamente
            if st.button(t["btn_organizar"], type="primary"):
                with st.spinner("Tidy está trabajando..."):
                    for arc in archivos_validos:
                        ruta_origen = os.path.join(ruta_carpeta, arc)
                        subruta_destino = clasificar_archivo(arc, ruta_origen)
                        
                        # Crear las carpetas físicas si no existen
                        carpeta_final_completa = os.path.join(ruta_carpeta, subruta_destino)
                        os.makedirs(carpeta_final_completa, exist_ok=True)
                        
                        # Mover el archivo real
                        ruta_destino_completa = os.path.join(carpeta_final_completa, arc)
                        shutil.move(ruta_origen, ruta_destino_completa)
                        
                st.success(t["exito"])
                st.balloons()
