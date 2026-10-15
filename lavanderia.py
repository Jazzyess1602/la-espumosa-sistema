import streamlit as st
import urllib.parse
import base64
import pandas as pd
from datetime import datetime, timedelta, timezone
import altair as alt

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
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"], .stApp, button, input, textarea, select { font-family: 'Plus Jakarta Sans', sans-serif !important; }

    /* Oculta marca de Streamlit sin perder el botón del menú lateral en celular */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    [data-testid="stToolbar"], [data-testid="stDecoration"] {display: none;}
    header[data-testid="stHeader"] { background: transparent; }
    .block-container { padding-top: 1.6rem; max-width: 1400px; }
    .stApp { background-color: #f4f7fb; }

    /* Menú lateral claro y limpio */
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
    [data-testid="stSidebar"] * { color: #334155; }
    .side-brand { text-align:center; padding: 6px 0 14px 0; border-bottom: 1px solid #eef2f7; margin-bottom: 14px; }
    .side-name { font-weight: 800; font-size: 1.05rem; color:#0f172a !important; margin-top: 8px; }
    .side-sub { font-size: .68rem; letter-spacing: 1.5px; color:#94a3b8 !important; font-weight:700; }
    .side-label { font-size:.7rem; font-weight:800; letter-spacing:1.5px; color:#94a3b8 !important; margin: 6px 0 6px 6px; }
    [data-testid="stSidebar"] div[role="radiogroup"] { gap: 4px; }
    [data-testid="stSidebar"] div[role="radiogroup"] label { padding: 11px 14px; border-radius: 12px; width: 100%; cursor: pointer; }
    [data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child { display: none; }
    [data-testid="stSidebar"] div[role="radiogroup"] label:hover { background-color: #f1f5f9; }
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) { background-color: #e0f2fe; }
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p { color: #0369a1 !important; font-weight: 700; }

    /* Barra superior */
    .topbar { display:flex; gap:12px; flex-wrap:wrap; margin-bottom: 22px; }
    .chip { display:flex; align-items:center; gap:12px; background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:10px 16px; box-shadow:0 1px 3px rgba(15,23,42,.04); }
    .chip-k { font-size:.78rem; font-weight:600; color:#64748b; border-right:1px solid #e2e8f0; padding-right:12px; }
    .chip-v { font-size:.88rem; font-weight:800; color:#0f172a; letter-spacing:.2px; }

    /* Tarjetas de indicadores */
    .kpi-card {
        background-color: #ffffff; padding: 18px 20px; border-radius: 16px;
        border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(15,23,42,.05);
        margin-bottom: 16px; min-height: 140px;
        transition: transform .15s ease, box-shadow .15s ease;
    }
    .kpi-card:hover { transform: translateY(-3px); box-shadow: 0 10px 22px rgba(2,132,199,.12); }
    .kpi-head { display:flex; align-items:center; gap:10px; }
    .kpi-ico { width:38px; height:38px; border-radius:11px; display:flex; align-items:center; justify-content:center; font-size:1.1rem; flex-shrink:0; }
    .kpi-title { font-size: .86rem; font-weight: 700; color: #334155; flex:1; line-height:1.15; }
    .kpi-tag { font-size:.62rem; font-weight:800; letter-spacing:.6px; background:#f1f5f9; color:#64748b; padding:3px 9px; border-radius:20px; }
    .kpi-value { font-size: 1.85rem; font-weight: 800; margin-top: 10px; margin-bottom: 2px; letter-spacing:-.5px; }
    .kpi-desc { font-size: .76rem; color: #94a3b8; line-height: 1.3; }

    /* Tarjetas contenedoras (gráficos, formularios) */
    [data-testid="stVerticalBlockBorderWrapper"] { background:#ffffff; border-radius:16px; border:1px solid #e2e8f0 !important; box-shadow:0 1px 3px rgba(15,23,42,.05); }
    [data-testid="stForm"] { background:#ffffff; border-radius:16px; border:1px solid #e2e8f0; padding:24px; box-shadow:0 1px 3px rgba(15,23,42,.05); }
    .card-title { font-weight:800; font-size:1.05rem; color:#0f172a; margin:0; }
    .card-sub { font-size:.78rem; color:#94a3b8; margin-bottom:6px; }
    .page-title { color:#0f172a; font-weight:800; font-size:1.6rem; margin:0; letter-spacing:-.4px; }
    [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input { border-radius:10px; }

    /* Contenedores de las barras de Login */
    .bloque-azul-corporativo {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        padding: 40px; border-radius: 20px; min-height: 440px;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        box-shadow: 0 10px 30px rgba(2, 132, 199, 0.15); text-align: center;
    }
    .gato-centrado { max-width: 220px; height: auto; filter: drop-shadow(0 15px 20px rgba(0,0,0,0.2)); }
    .stButton>button, .stFormSubmitButton>button {
        width: 100%; border-radius: 50px; height: 3.2em; font-weight: 800;
        background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%); color: white !important;
        border: none; font-size: .95rem; box-shadow: 0 8px 20px rgba(2, 132, 199, 0.25);
    }
    .stButton>button:hover, .stFormSubmitButton>button:hover { background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); }
    [data-testid="stSidebar"] .stButton>button p { color:#ffffff !important; }

    /* Ticket de la orden */
    .ticket { background:#ffffff; border:2px dashed #7dd3fc; border-radius:14px; padding:18px 22px; font-family:'Courier New', monospace; color:#1e293b; }
    .ticket h4 { margin:0 0 6px 0; color:#0369a1; text-align:center; }
    .ticket .total { font-size:1.3rem; font-weight:800; color:#0d9488; text-align:right; }
        </style>
""", unsafe_allow_html=True)

def kpi(icono, titulo, valor, desc, color="#0284c7", tag=None, borde=False, valor_color="#0f172a"):
    tag_html = f"<span class='kpi-tag'>{tag}</span>" if tag else ""
    borde_css = f"border-left:5px solid {color};" if borde else ""
    return (
        f"<div class='kpi-card' style='{borde_css}'>"
        f"<div class='kpi-head'><div class='kpi-ico' style='background:{color}1a;color:{color};'>{icono}</div>"
        f"<div class='kpi-title'>{titulo}</div>{tag_html}</div>"
        f"<div class='kpi-value' style='color:{valor_color};'>{valor}</div>"
        f"<div class='kpi-desc'>{desc}</div></div>"
    )

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
        logo = (f"<img src='data:image/png;base64,{gato_b64}' style='width:68px;height:68px;border-radius:50%;object-fit:cover;box-shadow:0 4px 12px rgba(2,132,199,.25);'/>"
                if gato_b64 else "<div style='font-size:2.6rem;'>🧼</div>")
        st.markdown(f"<div class='side-brand'>{logo}<div class='side-name'>La Espumosa Express</div><div class='side-sub'>LAVANDERÍA · SEDE PRINCIPAL</div></div>", unsafe_allow_html=True)
        st.markdown("<div class='side-label'>INICIO</div>", unsafe_allow_html=True)

        menu_modulo = st.radio(
            "MÓDULOS DEL SISTEMA",
            ["📊 Tablero de Control", "📥 Orden de Servicio", "🧾 Facturación Electrónica", "📈 Reportes y Dashboards"],
            label_visibility="collapsed"
        )
        st.markdown("---")
        if st.button("🚪 Cerrar Turno (Salir)"):
            st.session_state.autenticado = False
            st.rerun()

    # Barra superior (hora de Perú)
    ahora = datetime.now(timezone(timedelta(hours=-5))).strftime("%d/%m/%Y %H:%M")
    st.markdown(
        f"<div class='topbar'>"
        f"<div class='chip'><span class='chip-k'>🚩 Sucursal</span><span class='chip-v'>SEDE PRINCIPAL</span></div>"
        f"<div class='chip'><span class='chip-k'>🕒 Fecha</span><span class='chip-v'>{ahora}</span></div>"
        f"</div>", unsafe_allow_html=True)

    if menu_modulo == "📊 Tablero de Control":
        st.markdown("<h1 class='page-title'>Dashboard General</h1>", unsafe_allow_html=True)
        st.caption("Resumen financiero y operativo de las últimas actividades.")

        # Fila 1 de Indicadores
        f1_c1, f1_c2, f1_c3, f1_c4 = st.columns(4)
        with f1_c1:
            st.markdown(kpi("📋", "Órdenes del período", "108", "43 ya pagadas por completo.", "#6366f1"), unsafe_allow_html=True)
        with f1_c2:
            st.markdown(kpi("📈", "Ventas del período", "S/ 3,200.56", "Total acumulado sin anular.", "#059669"), unsafe_allow_html=True)
        with f1_c3:
            st.markdown(kpi("💳", "Cobrado en el período", "S/ 1,552.16", "Dinero real en caja.", "#0891b2"), unsafe_allow_html=True)
        with f1_c4:
            st.markdown(kpi("⚠️", "Saldo por cobrar", "S/ 1,867.70", "Pendiente contra entrega.", "#e11d48"), unsafe_allow_html=True)

        # Fila 2 de Indicadores
        f2_c1, f2_c2, f2_c3, f2_c4 = st.columns(4)
        with f2_c1:
            st.markdown(kpi("⚖️", "Kilos procesados", "425.8 kg", "Peso total acumulado actual.", "#2563eb", tag="PERÍODO", borde=True), unsafe_allow_html=True)
        with f2_c2:
            st.markdown(kpi("👥", "Clientes nuevos", "15", "Vinieron por primera vez a la lavandería.", "#059669", tag="PERÍODO", borde=True), unsafe_allow_html=True)
        with f2_c3:
            st.markdown(kpi("🧺", "Clientes atendidos", "57", "Clientes distintos que dejaron ropa.", "#7c3aed", tag="PERÍODO", borde=True), unsafe_allow_html=True)
        with f2_c4:
            st.markdown(kpi("🎫", "Ticket promedio", "S/ 29.63", "Lo que deja en promedio cada orden.", "#0891b2", tag="PERÍODO", borde=True), unsafe_allow_html=True)

        # Fila 3: Estado Logístico de Entregas
        f3_c1, f3_c2, f3_c3, f3_c4 = st.columns(4)
        with f3_c1:
            st.markdown(kpi("🚨", "Entregas vencidas", "256", "Pasó su fecha de entrega y aún no se entregan.", "#e11d48", tag="HOY", borde=True, valor_color="#e11d48"), unsafe_allow_html=True)
        with f3_c2:
            st.markdown(kpi("📅", "Entregas de hoy", "7", "El cliente las espera hoy.", "#d97706", tag="HOY", borde=True), unsafe_allow_html=True)
        with f3_c3:
            st.markdown(kpi("⏰", "Entregas de mañana", "1", "Ténlas listas para mañana.", "#ea580c", tag="MAÑANA", borde=True), unsafe_allow_html=True)
        with f3_c4:
            st.markdown(kpi("✅", "Listas para recoger", "12", "Ya terminadas, esperando que el cliente pase.", "#059669", tag="HOY", borde=True), unsafe_allow_html=True)

        # Gráficos
        g1, g2 = st.columns([2, 1])
        with g1:
            with st.container(border=True):
                st.markdown("<p class='card-title'>Actividad reciente</p><p class='card-sub'>Últimos 7 días del período · datos de ejemplo</p>", unsafe_allow_html=True)
                hoy = datetime.now(timezone(timedelta(hours=-5)))
                dias = [(hoy - timedelta(days=i)).strftime("%d/%m") for i in range(6, -1, -1)]
                df_act = pd.DataFrame({"Día": dias, "Órdenes": [9, 14, 11, 17, 12, 15, 11], "Ventas": [210, 340, 260, 420, 310, 380, 290]})
                base = alt.Chart(df_act).encode(x=alt.X("Día:N", sort=None, axis=alt.Axis(labelAngle=0, title=None)))
                barras = base.mark_bar(color="#6366f1", cornerRadiusTopLeft=6, cornerRadiusTopRight=6, size=30).encode(
                    y=alt.Y("Órdenes:Q", axis=alt.Axis(title="Órdenes")), tooltip=["Día", "Órdenes"])
                linea = base.mark_line(color="#059669", strokeWidth=3, point=alt.OverlayMarkDef(color="#059669", size=60)).encode(
                    y=alt.Y("Ventas:Q", axis=alt.Axis(title="Ventas (S/)", orient="right")), tooltip=["Día", "Ventas"])
                st.altair_chart(alt.layer(barras, linea).resolve_scale(y="independent").properties(height=270))
        with g2:
            with st.container(border=True):
                st.markdown("<p class='card-title'>Estado de órdenes</p><p class='card-sub'>Distribución del período · datos de ejemplo</p>", unsafe_allow_html=True)
                df_est = pd.DataFrame({"Estado": ["Entregadas", "Listas", "En proceso"], "Cantidad": [61, 12, 35]})
                donut = alt.Chart(df_est).mark_arc(innerRadius=62, outerRadius=105).encode(
                    theta="Cantidad:Q",
                    color=alt.Color("Estado:N",
                                    scale=alt.Scale(domain=["Entregadas", "Listas", "En proceso"], range=["#059669", "#0891b2", "#f59e0b"]),
                                    legend=alt.Legend(orient="bottom", title=None)),
                    tooltip=["Estado", "Cantidad"]).properties(height=270)
                st.altair_chart(donut)

    elif menu_modulo == "📥 Orden de Servicio":
        st.markdown("<h1 class='page-title'>Nueva Orden de Servicio</h1>", unsafe_allow_html=True)
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
        st.markdown("<h1 class='page-title'>Facturación Electrónica</h1>", unsafe_allow_html=True)
        st.info("🚧 Módulo en construcción.")

    elif menu_modulo == "📈 Reportes y Dashboards":
        st.markdown("<h1 class='page-title'>Reportes y Dashboards</h1>", unsafe_allow_html=True)
        st.info("🚧 Módulo en construcción.")
