import streamlit as st
import urllib.parse
import base64
import pandas as pd
from datetime import datetime

# Configuración de pantalla completa estilo Software de Escritorio Comercial
st.set_page_config(
    page_title="La Espumosa Express - Panel General", 
    page_icon="🧼", 
    layout="wide"
)

# --- FUNCIÓN CONVERTIDORA PARA TU MASCOTA ---
def obtener_base64(ruta):
    try:
        with open(ruta, "rb") as file:
            return base64.b64encode(file.read()).decode()
    except FileNotFoundError:
        return ""

gato_b64 = obtener_base64("gato.png")

# --- CREDENCIALES (se leen de Streamlit Secrets, NO van escritas en el código) ---
def leer_secreto(nombre, defecto=""):
    try:
        return st.secrets.get(nombre, defecto)
    except Exception:
        return defecto

RUC_OK = str(leer_secreto("RUC"))
CLAVE_OK = str(leer_secreto("CLAVE"))

# --- TARIFAS DE SERVICIOS (edita aquí los precios) ---
SERVICIOS = {
    "Ropa por Kilo": 5.00,
    "Edredón 2 Plazas": 15.00,
}

# --- MAQUETACIÓN VISUAL CON COLORES EXCLUSIVOS DE LA ESPUMOSA ---
st.markdown("""
    <style>
    /* Oculta marca de Streamlit sin perder el botón del menú lateral en celular */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    [data-testid="stToolbar"], [data-testid="stDecoration"] {display: none;}
    header[data-testid="stHeader"] { background: transparent; }
    .block-container { padding-top: 2rem; }
    .stApp { background-color: #f0fdfa; }
    
    /* Menú Lateral Estilo Premium */
    [data-testid="stSidebar"] { background-color: #0369a1; border-right: 2px solid #0284c7; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        padding: 8px 10px; border-radius: 10px; width: 100%;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover { background-color: rgba(255,255,255,0.12); }
    
    /* Tarjetas de Indicadores con tus colores de marca */
    .kpi-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 16px;
        border: 2px solid #e0f2fe;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.05);
        margin-bottom: 15px;
        min-height: 128px;
        transition: transform .15s ease, box-shadow .15s ease;
    }
    .kpi-card:hover { transform: translateY(-3px); box-shadow: 0 8px 18px rgba(2, 132, 199, 0.12); }
    .kpi-title { font-size: 0.85rem; font-weight: bold; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }
    .kpi-value { font-size: 1.8rem; font-weight: 800; margin-top: 5px; margin-bottom: 2px; }
    .kpi-value-azul { color: #0284c7; }
    .kpi-value-verde { color: #0d9488; }
    .kpi-value-alerta { color: #e11d48; }
    .kpi-desc { font-size: 0.75rem; color: #94a3b8; line-height: 1.2; }
    
    /* Contenedores de las barras de Login */
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
    .gato-centrado { max-width: 220px; height: auto; filter: drop-shadow(0 15px 20px rgba(0,0,0,0.2)); }
    .stButton>button, .stFormSubmitButton>button {
        width: 100%; border-radius: 50px; height: 3.6em; font-weight: 800;
        background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%); color: white !important;
        border: none; font-size: 1rem; box-shadow: 0 8px 20px rgba(2, 132, 199, 0.25);
    }
    .stButton>button:hover, .stFormSubmitButton>button:hover { background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); }

    /* Ticket de la orden */
    .ticket {
        background:#ffffff; border:2px dashed #7dd3fc; border-radius:14px;
        padding:18px 22px; font-family: 'Courier New', monospace; color:#1e293b;
    }
    .ticket h4 { margin:0 0 6px 0; color:#0369a1; text-align:center; }
    .ticket .total { font-size:1.3rem; font-weight:800; color:#0d9488; text-align:right; }
    </style>
""", unsafe_allow_html=True)

if "autenticado" not in st.session_state: st.session_state.autenticado = False
if "ordenes" not in st.session_state: st.session_state.ordenes = []
if "ultima_orden" not in st.session_state: st.session_state.ultima_orden = None

# =========================================================
# 1. CONTROL DE ACCESO (PANTALLA DE LOGIN DE LA EMPRESA)
# =========================================================
if not st.session_state.autenticado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_izq, col_der = st.columns([1, 1.2], gap="large")
    
    with col_izq:
        img_html = f"<img class='gato-centrado' src='data:image/png;base64,{gato_b64}' />" if gato_b64 else "<div style='font-size:7rem;'>🧼</div>"
        st.markdown(f"""
            <div class='bloque-azul-corporativo'>
                <h1 style='color:white; font-size:2.6rem; font-weight:900; margin:0;'>La Espumosa Express</h1>
                <p style='color:#bae6fd; font-weight:bold; letter-spacing:3px; text-transform:uppercase; margin-bottom:20px;'>Lavandería</p>
                {img_html}
            </div>
        """, unsafe_allow_html=True)
        
    with col_der:
        st.markdown("<div style='padding: 10px 40px;'>", unsafe_allow_html=True)
        st.markdown("<p style='color:#0d9488; font-weight:bold; margin-bottom:0px; font-size:0.85rem;'>BIENVENIDO DE NUEVO</p>", unsafe_allow_html=True)
        st.markdown("<h1 style='margin-top:0px; font-weight:800; color:#1e293b; font-size:2.4rem;'>Inicia sesión</h1>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        if not CLAVE_OK:
            st.warning("⚠️ Falta configurar las credenciales en *Settings → Secrets* de Streamlit (RUC y CLAVE).")
        
        with st.form("form_login"):
            ruc_empresa = st.text_input("RUC de la empresa", value=RUC_OK, max_chars=11)
            clave_usuario = st.text_input("Contraseña de Acceso", type="password", placeholder="Ingresa la clave de tu lavandería")
            st.markdown("<br>", unsafe_allow_html=True)
            entrar = st.form_submit_button("🧼 INGRESAR DE FORMA SEGURA")

        if entrar:
            if CLAVE_OK and ruc_empresa == RUC_OK and clave_usuario == CLAVE_OK:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas.")
        st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 2. SISTEMA PRINCIPAL AUTENTICADO (MÓDULOS DEL PANEL)
# =========================================================
else:
    with st.sidebar:
        st.markdown("<h2 style='text-align: center; font-weight:800;'>🧼 La Espumosa</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size:0.8rem; margin-top:-15px;'>SEDE PRINCIPAL</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        menu_modulo = st.radio(
            "MÓDULOS DEL SISTEMA",
            ["📊 Tablero de Control", "📥 Orden de Servicio", "🧾 Facturación Electrónica", "📈 Reportes y Dashboards"]
        )
        st.markdown("---")
        if st.button("🚪 Cerrar Turno (Salir)"):
            st.session_state.autenticado = False
            st.rerun()

    if menu_modulo == "📊 Tablero de Control":
        c_tit, c_info = st.columns([3, 1])
        with c_tit:
            st.markdown("<h1 style='color:#0369a1; font-weight:800; margin:0;'>📊 Dashboard General</h1>", unsafe_allow_html=True)
            st.caption("Resumen financiero y operativo de las últimas actividades.")
        with c_info:
            st.info("📍 Sucursal: Sede Principal")

        st.markdown("<br>", unsafe_allow_html=True)

        # Fila 1 de Indicadores
        f1_c1, f1_c2, f1_c3, f1_c4 = st.columns(4)
        with f1_c1:
            st.markdown("""<div class='kpi-card'><div class='kpi-title'>📦 Órdenes del Período</div><div class='kpi-value kpi-value-azul'>108</div><div class='kpi-desc'>43 ya pagadas por completo.</div></div>""", unsafe_allow_html=True)
        with f1_c2:
            st.markdown("""<div class='kpi-card'><div class='kpi-title'>📈 Ventas del Período</div><div class='kpi-value kpi-value-verde'>S/ 3,200.56</div><div class='kpi-desc'>Total acumulado sin anular.</div></div>""", unsafe_allow_html=True)
        with f1_c3:
            st.markdown("""<div class='kpi-card'><div class='kpi-title'>💳 Cobrado en el Período</div><div class='kpi-value kpi-value-verde'>S/ 1,552.16</div><div class='kpi-desc'>Dinero real en caja.</div></div>""", unsafe_allow_html=True)
        with f1_c4:
            st.markdown("""<div class='kpi-card'><div class='kpi-title'>⚠️ Saldo por Cobrar</div><div class='kpi-value kpi-value-alerta'>S/ 1,867.70</div><div class='kpi-desc'>Pendiente contra entrega.</div></div>""", unsafe_allow_html=True)

        # Fila 2 de Indicadores
        f2_c1, f2_c2, f2_c3, f2_c4 = st.columns(4)
        with f2_c1:
            st.markdown("""<div class='kpi-card'><div class='kpi-title'>⚖️ Kilos Procesados</div><div class='kpi-value kpi-value-azul'>425.8 kg</div><div class='kpi-desc'>Peso total acumulado actual.</div></div>""", unsafe_allow_html=True)
        with f2_c2:
            st.markdown("""<div class='kpi-card'><div class='kpi-title'>👥 Clientes Nuevos</div><div class='kpi-value kpi-value-azul'>15</div><div class='kpi-desc'>Registros nuevos del período.</div></div>""", unsafe_allow_html=True)
        with f2_c3:
            st.markdown("""<div class='kpi-card'><div class='kpi-title'>🧺 Clientes Atendidos</div><div class='kpi-value kpi-value-azul'>57</div><div class='kpi-desc'>Clientes distintos atendidos.</div></div>""", unsafe_allow_html=True)
        with f2_c4:
            st.markdown("""<div class='kpi-card'><div class='kpi-title'>🎫 Ticket Promedio</div><div class='kpi-value kpi-value-azul'>S/ 29.63</div><div class='kpi-desc'>Consumo promedio por orden.</div></div>""", unsafe_allow_html=True)

        # Fila 3: Estado Logístico de Entregas
        st.markdown("<h3 style='color:#1e293b; font-family:sans-serif;'>🔄 Estado Logístico de Entregas</h3>", unsafe_allow_html=True)
        f3_c1, f3_c2, f3_c3, f3_c4 = st.columns(4)
        with f3_c1:
            st.markdown("""<div class='kpi-card' style='border-left: 5px solid #e11d48;'><div class='kpi-title' style='color:#e11d48;'>🚨 Entregas Vencidas</div><div class='kpi-value kpi-value-alerta'>256</div><div class='kpi-desc'>Pasó fecha de entrega.</div></div>""", unsafe_allow_html=True)
        with f3_c2:
            st.markdown("""<div class='kpi-card' style='border-left: 5px solid #eab308;'><div class='kpi-title' style='color:#eab308;'>📅 Entregas de Hoy</div><div class='kpi-value' style='color:#eab308;'>7</div><div class='kpi-desc'>Esperan recojo hoy.</div></div>""", unsafe_allow_html=True)
        with f3_c3:
            st.markdown("""<div class='kpi-card' style='border-left: 5px solid #2563eb;'><div class='kpi-title' style='color:#2563eb;'>⏰ Entregas de Mañana</div><div class='kpi-value' style='color:#2563eb;'>1</div><div class='kpi-desc'>Ropa lista para mañana.</div></div>""", unsafe_allow_html=True)
        with f3_c4:
            st.markdown("""<div class='kpi-card' style='border-left: 5px solid #0d9488;'><div class='kpi-title' style='color:#0d9488;'>✔️ Listas para Recoger</div><div class='kpi-value kpi-value-verde'>12</div><div class='kpi-desc'>Listas esperando al cliente.</div></div>""", unsafe_allow_html=True)

    elif menu_modulo == "📥 Orden de Servicio":
        st.markdown("<h1 style='color:#0369a1; font-weight:800; margin:0;'>📥 Nueva Orden de Servicio</h1>", unsafe_allow_html=True)
        st.caption("Registra al cliente, elige el servicio y genera el ticket.")
        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("form_orden", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                dni_c = st.text_input("DNI del Cliente:", max_chars=8)
                nom_c = st.text_input("Nombre Completo:")
                tel_c = st.text_input("WhatsApp Celular:", max_chars=9)
            with c2:
                serv = st.selectbox(
                    "Tipo de Servicio:",
                    list(SERVICIOS.keys()),
                    format_func=lambda s: f"{s} (S/ {SERVICIOS[s]:.2f})"
                )
                cant = st.number_input("Cantidad / Kilos:", min_value=0.0, step=0.5)
            guardar = st.form_submit_button("💾 GUARDAR PEDIDO")

        if guardar:
            errores = []
            if not (dni_c.isdigit() and len(dni_c) == 8): errores.append("El DNI debe tener 8 dígitos.")
            if not nom_c.strip(): errores.append("Falta el nombre del cliente.")
            if not (tel_c.isdigit() and len(tel_c) == 9): errores.append("El WhatsApp debe tener 9 dígitos.")
            if cant <= 0: errores.append("La cantidad debe ser mayor a 0.")

            if errores:
                for e in errores:
                    st.error(e)
            else:
                total = SERVICIOS[serv] * cant
                orden = {
                    "N° Orden": f"{len(st.session_state.ordenes) + 1:05d}",
                    "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "DNI": dni_c,
                    "Cliente": nom_c.strip().title(),
                    "WhatsApp": tel_c,
                    "Servicio": serv,
                    "Cantidad": cant,
                    "Total (S/)": round(total, 2),
                }
                st.session_state.ordenes.append(orden)
                st.session_state.ultima_orden = orden
                st.success("¡Pedido registrado exitosamente!")

        # Ticket de la última orden + envío por WhatsApp
        o = st.session_state.ultima_orden
        if o:
            st.markdown("<br>", unsafe_allow_html=True)
            t1, t2 = st.columns([1, 1], gap="large")
            with t1:
                st.markdown(f"""
                    <div class='ticket'>
                        <h4>🧼 LA ESPUMOSA EXPRESS</h4>
                        <div style='text-align:center; font-size:0.8rem;'>Lavandería · Ticket de orden</div>
                        <hr style='border-top:1px dashed #94a3b8;'>
                        <div>Orden N°: <b>{o['N° Orden']}</b></div>
                        <div>Fecha: {o['Fecha']}</div>
                        <div>Cliente: {o['Cliente']}</div>
                        <div>DNI: {o['DNI']}</div>
                        <hr style='border-top:1px dashed #94a3b8;'>
                        <div>{o['Servicio']} x {o['Cantidad']}</div>
                        <div class='total'>TOTAL: S/ {o['Total (S/)']:.2f}</div>
                    </div>
                """, unsafe_allow_html=True)
            with t2:
                mensaje = (
                    f"Hola {o['Cliente']} 👋, gracias por confiar en La Espumosa Express 🧼.\n"
                    f"Tu orden N° {o['N° Orden']} ({o['Servicio']} x {o['Cantidad']}) "
                    f"por S/ {o['Total (S/)']:.2f} fue registrada. Te avisaremos cuando esté lista."
                )
                enlace = f"https://wa.me/51{o['WhatsApp']}?text={urllib.parse.quote(mensaje)}"
                st.link_button("📲 Enviar ticket por WhatsApp", enlace)

        # Historial de órdenes de la sesión
        if st.session_state.ordenes:
            st.markdown("<h3 style='color:#1e293b;'>🗂️ Órdenes registradas</h3>", unsafe_allow_html=True)
            df = pd.DataFrame(st.session_state.ordenes).iloc[::-1]
            st.dataframe(df, hide_index=True)

    elif menu_modulo == "🧾 Facturación Electrónica":
        st.markdown("<h1 style='color:#0369a1; font-weight:800; margin:0;'>🧾 Facturación Electrónica</h1>", unsafe_allow_html=True)
        st.info("🚧 Módulo en construcción.")

    elif menu_modulo == "📈 Reportes y Dashboards":
        st.markdown("<h1 style='color:#0369a1; font-weight:800; margin:0;'>📈 Reportes y Dashboards</h1>", unsafe_allow_html=True)
        st.info("🚧 Módulo en construcción.")
