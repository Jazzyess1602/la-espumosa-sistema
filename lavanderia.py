import streamlit as st
import urllib.parse
import base64

# Configuración de pantalla completa estilo Software comercial de Escritorio
st.set_page_config(
    page_title="La Espumosa Express", 
    page_icon="🧼", 
    layout="wide"
)

# --- FUNCIÓN CONVERTIDORA PARA TU MASCOTA LOCAL ---
def obtener_base64(ruta):
    try:
        with open(ruta, "rb") as file:
            return base64.b64encode(file.read()).decode()
    except FileNotFoundError:
        return ""

gato_b64 = obtener_base64("gato.png")

# --- MAQUETACIÓN VISUAL CON CSS ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stApp { background-color: #ffffff; }
    
    /* Bloque Izquierdo Azul Eléctrico */
    .bloque-azul-corporativo {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        padding: 40px;
        border-radius: 20px;
        min-height: 440px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 0 10px 30px rgba(2, 132, 199, 0.15);
        text-align: center;
    }
    .titulo-empresa {
        color: #ffffff !important;
        font-size: 2.6rem;
        font-weight: 900;
        margin-bottom: 0px;
        font-family: 'Arial Rounded MT Bold', sans-serif;
    }
    .sub-empresa {
        color: #bae6fd !important;
        font-size: 1.1rem;
        font-weight: bold;
        letter-spacing: 4px;
        margin-top: 0px;
        margin-bottom: 30px;
        text-transform: uppercase;
    }
    .gato-centrado {
        max-width: 220px;
        height: auto;
        filter: drop-shadow(0 15px 20px rgba(0,0,0,0.2));
    }
    
    /* Bloque Derecho de Formulario Moderno */
    .bloque-derecho-login {
        padding: 10px 40px;
    }
    
    /* Estilo de los campos de texto */
    .stTextInput>div>div>input {
        border-radius: 10px !important;
        border: 1px solid #cbd5e1 !important;
        height: 45px !important;
    }
    
    /* Botón Ovalado de Ingreso */
    .stButton>button {
        width: 100%;
        border-radius: 50px;
        height: 3.6em;
        font-weight: 800;
        background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%);
        color: white !important;
        border: none;
        font-size: 1rem;
        letter-spacing: 0.5px;
        box-shadow: 0 8px 20px rgba(2, 132, 199, 0.25);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
    }
    </style>
""", unsafe_allow_html=True)

if "autenticado" not in st.session_state: st.session_state.autenticado = False

# =========================================================
# CONTROL DE PANTALLAS
# =========================================================
if not st.session_state.autenticado:
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Dividimos la pantalla en dos columnas limpias (50% y 50%)
    col_izq, col_der = st.columns([1, 1], gap="large")
    
    # --- MITAD IZQUIERDA: DISEÑO LIMPIO CON TU MASCOTA ---
    with col_izq:
        img_gato_html = f"<img class='gato-centrado' src='data:image/png;base64,{gato_b64}' />" if gato_b64 else "<p style='color:yellow;'>⚠️ Archivo 'gato.png' no detectado</p>"
        
        st.markdown(f"""
            <div class='bloque-azul-corporativo'>
                <h1 class='titulo-empresa'>La Espumosa Express</h1>
                <p class='sub-empresa'>Lavandería</p>
                {img_gato_html}
            </div>
        """, unsafe_allow_html=True)
        
    # --- MITAD DERECHA: FORMULARIO SIMPLIFICADO DE ACCESO ---
    with col_der:
        st.markdown("<div class='bloque-derecho-login'>", unsafe_allow_html=True)
        st.markdown("<p style='color:#16a34a; font-weight:bold; margin-bottom:0px; font-size:0.85rem;'>BIENVENIDO DE NUEVO</p>", unsafe_allow_html=True)
        st.markdown("<h1 style='margin-top:0px; font-weight:800; color:#1e293b; font-size:2.4rem;'>Inicia sesión</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color:#64748b; margin-top:-10px; font-size:0.95rem;'>Ingresa la contraseña de turno para abrir el sistema.</p>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Casillero con tu RUC fijo
        ruc_empresa = st.text_input("RUC de la empresa", value="20615475581", max_chars=11)
        st.caption("RUC de 11 dígitos configurado para tu local.")
        
        # Único campo requerido (Contraseña)
        clave_usuario = st.text_input("Contraseña de Acceso", type="password", placeholder="Ingresa la clave de tu lavandería")
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        if st.button("🧼 INRESAR DE FORMA SEGURA"):
            # Validación con tu RUC y tu nueva contraseña exacta
            if ruc_empresa == "20615475581" and clave_usuario == "espumosa3105":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("RUC o Contraseña incorrectos. Verifica los datos.")
        st.markdown("</div>", unsafe_allow_html=True)

else:
    # --- INTERFAZ CENTRAL DEL SOFTWARE OPERATIVO INTERNO ---
    st.markdown("<h1 style='color:#0284c7; text-align:center; margin-top:20px;'>🧼 Panel de Recepción y Control - La Espumosa Express</h1>", unsafe_allow_html=True)
    st.success("¡Contraseña correcta! Has ingresado con éxito.")
    
    if st.button("🚪 Cerrar Turno (Salir)"):
        st.session_state.autenticado = False
        st.rerun()

