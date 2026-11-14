import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import date, datetime, time
from decimal import Decimal
from html import escape
import re, hashlib, hmac, secrets

st.set_page_config(page_title="Peluquería", page_icon="💈", layout="wide", initial_sidebar_state="collapsed")

# ============================ DISEÑO ============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700;800&family=Playfair+Display:wght@400;500;600;700&display=swap');
:root{--bg:#111211;--panel:#20211e;--panel2:#292a26;--gold:#c7ad7b;--gold2:#dfcca5;--text:#eee9df;--muted:#aaa69d;--line:rgba(199,173,123,.22)}
.stApp{background:radial-gradient(ellipse at 50% -15%,rgba(199,173,123,.09),transparent 42%),var(--bg);color:var(--text);font-family:'DM Sans',sans-serif}
.block-container{max-width:1320px;padding:1.3rem 2rem 3rem}
h1,h2,h3{font-family:'Playfair Display',Georgia,serif!important;color:var(--gold2)!important;font-weight:500!important}
.stButton>button,.stLinkButton>a,[data-testid="stFormSubmitButton"] button{background:linear-gradient(135deg,#d8c49b,#b89b68);color:#171713!important;border:1px solid rgba(235,220,188,.55);border-radius:6px;min-height:43px;font-weight:700;letter-spacing:.035em;transition:.2s}
.stButton>button:hover,.stLinkButton>a:hover{filter:brightness(1.1);transform:translateY(-2px)}
[data-testid="stForm"]{background:linear-gradient(145deg,#252622,#1b1c1a);border:1px solid var(--line);border-radius:12px;padding:22px}
[data-baseweb="input"],[data-baseweb="select"],[data-baseweb="textarea"]{background:var(--panel2)}
input,textarea{color:var(--text)!important}
[data-testid="stMetric"]{background:linear-gradient(145deg,#292a25,#1b1c1a);border:1px solid var(--line);padding:18px;border-radius:11px;min-height:110px}
[data-testid="stMetricValue"]{color:var(--gold2);font-weight:700}
[data-testid="stMetricLabel"]{color:var(--muted)}
[data-testid="stTabs"] button{color:var(--gold2);font-weight:600}
hr{border-color:var(--line)}
.hero{min-height:520px;background-size:cover;background-position:center 44%;border:1px solid var(--line);border-radius:12px;display:flex;align-items:center;justify-content:center;text-align:center;padding:35px;position:relative;margin:15px 0 28px;box-shadow:0 24px 60px #0005}
.hero:before{content:"";position:absolute;inset:0;border-radius:12px;background:linear-gradient(180deg,#0a0b0a55,#0a0b0add)}
.hero-content{position:relative;max-width:850px}
.hero h1{font-size:clamp(32px,5.4vw,66px)!important;letter-spacing:.04em;text-transform:uppercase;color:#f1e7d3!important}
.hero p{color:#f0ece4;line-height:1.8}
.hero-label{color:var(--gold2);letter-spacing:.3em;font-size:12px;font-weight:700}
.hero-logo{max-width:110px;max-height:90px;object-fit:contain;margin-bottom:20px}
.section-title{text-align:center;margin:42px 0 25px}
.section-title h2{letter-spacing:.06em}
.section-title p,.small-text{color:var(--muted);font-size:13px}
.gold-line{width:52px;height:1px;background:var(--gold);margin:15px auto 20px}
.info-card{background:linear-gradient(145deg,#292a25,#1b1c1a);border:1px solid var(--line);border-radius:11px;padding:23px;box-shadow:0 10px 28px #0002;margin-bottom:16px}
.info-card p{color:#d0ccc3;line-height:1.7}
.footer{text-align:center;padding:35px 10px 18px;margin-top:48px;border-top:1px solid var(--line);color:var(--muted);font-size:13px}
.footer strong{color:var(--gold2);font:500 18px 'Playfair Display';letter-spacing:.08em}
.admin-header{background:linear-gradient(120deg,#292a25,#171815);border:1px solid var(--line);border-radius:14px;padding:25px 28px;margin:15px 0 25px}
.admin-header .eyebrow{color:var(--gold);font-size:11px;font-weight:800;letter-spacing:3px;text-transform:uppercase}
.admin-header h1{margin:7px 0!important;font-size:32px!important}
.admin-header p,.admin-note{color:var(--muted)}
.status-paid{color:#8bd2a8;background:rgba(83,170,120,.12);border:1px solid rgba(83,170,120,.25);padding:5px 11px;border-radius:30px;font-size:11px;font-weight:800}
.status-pending{color:#e3c17d;background:rgba(199,173,123,.12);border:1px solid rgba(199,173,123,.25);padding:5px 11px;border-radius:30px;font-size:11px;font-weight:800}
.login-card{max-width:500px;margin:35px auto;background:linear-gradient(145deg,#292a25,#1b1c1a);border:1px solid var(--line);border-radius:15px;padding:30px}
@media(max-width:768px){.block-container{padding:.6rem .8rem 2rem}.hero{min-height:400px;padding:22px}.info-card{padding:17px}[data-testid="stForm"]{padding:15px}.stButton>button{font-size:12px}.admin-header{padding:20px}.admin-header h1{font-size:25px!important}}
</style>
""", unsafe_allow_html=True)

# ============================ BASE DE DATOS ============================
def conectar_db():
    return psycopg2.connect(
        host=st.secrets["DB_HOST"], port=st.secrets.get("DB_PORT", 5432),
        database=st.secrets["DB_NAME"], user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"], sslmode="require", connect_timeout=15
    )

def consultar(sql, parametros=None):
    con = conectar_db()
    try:
        with con.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, parametros or ())
            return [dict(r) for r in cur.fetchall()]
    finally:
        con.close()

def ejecutar(sql, parametros=None):
    con = conectar_db()
    try:
        with con.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, parametros or ())
            rows = cur.fetchall() if cur.description else []
        con.commit()
        return [dict(r) for r in rows]
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()

def euros(v):
    try:
        return f"{float(v):,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "0,00 €"

# ============================ SEGURIDAD ============================
def crear_hash_pin(pin, salt=None):
    salt = salt or secrets.token_bytes(16)
    return salt.hex(), hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, 600_000).hex()

def obtener_credencial_pin():
    rows = consultar("SELECT salt,pin_hash FROM public.seguridad WHERE id=1")
    return rows[0] if rows else None

def verificar_pin(pin):
    cred = obtener_credencial_pin()
    if not cred:
        return False
    try:
        h = hashlib.pbkdf2_hmac("sha256", pin.encode(), bytes.fromhex(cred["salt"]), 600_000)
        return hmac.compare_digest(h, bytes.fromhex(cred["pin_hash"]))
    except (ValueError, TypeError, KeyError):
        return False

def guardar_nuevo_pin(pin):
    salt, h = crear_hash_pin(pin)
    ejecutar("""INSERT INTO public.seguridad(id,salt,pin_hash,actualizado)
    VALUES(1,%s,%s,NOW()) ON CONFLICT(id) DO UPDATE
    SET salt=EXCLUDED.salt,pin_hash=EXCLUDED.pin_hash,actualizado=NOW()""", (salt, h))

# ============================ INICIALIZACIÓN ============================
def inicializar_base_datos():
    con = conectar_db()
    try:
        with con.cursor() as cur:
            cur.execute("""CREATE TABLE IF NOT EXISTS public.servicios(
                id SERIAL PRIMARY KEY,nombre VARCHAR(150) NOT NULL UNIQUE,
                precio NUMERIC(10,2) NOT NULL DEFAULT 0,activo BOOLEAN NOT NULL DEFAULT TRUE)""")
            cur.execute("""CREATE TABLE IF NOT EXISTS public.configuracion_web(
                clave VARCHAR(100) PRIMARY KEY,valor TEXT)""")
            cur.execute("""CREATE TABLE IF NOT EXISTS public.citas(
                id SERIAL PRIMARY KEY,cliente VARCHAR(150) NOT NULL,telefono VARCHAR(50) NOT NULL,
                servicio VARCHAR(150) NOT NULL,precio NUMERIC(10,2) NOT NULL DEFAULT 0,
                fecha DATE NOT NULL,hora TIME NOT NULL,pagada BOOLEAN NOT NULL DEFAULT FALSE)""")
            cur.execute("""CREATE TABLE IF NOT EXISTS public.productos(
                id SERIAL PRIMARY KEY,nombre VARCHAR(150) NOT NULL,
                precio NUMERIC(10,2) NOT NULL DEFAULT 0,activo BOOLEAN NOT NULL DEFAULT TRUE)""")
            cur.execute("""CREATE TABLE IF NOT EXISTS public.seguridad(
                id SMALLINT PRIMARY KEY CHECK(id=1),salt VARCHAR(64) NOT NULL,
                pin_hash VARCHAR(128) NOT NULL,actualizado TIMESTAMPTZ NOT NULL DEFAULT NOW())""")
            cur.execute("""SELECT fecha,hora,COUNT(*) FROM public.citas
                GROUP BY fecha,hora HAVING COUNT(*)>1 LIMIT 1""")
            if cur.fetchone():
                raise RuntimeError("Existen citas duplicadas por fecha y hora; resuélvelas antes de activar el índice.")
            cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_citas_fecha_hora ON public.citas(fecha,hora)")
            cur.execute("""INSERT INTO public.servicios(nombre,precio,activo) VALUES
                ('Corte de caballero',12,TRUE),('Corte infantil',9,TRUE),
                ('Arreglo de barba',7,TRUE),('Corte + barba',17,TRUE)
                ON CONFLICT(nombre) DO NOTHING""")
            defaults = {
                "nombre":"PELUQUERÍA", "eslogan":"TU ESTILO, NUESTRA PASIÓN",
                "descripcion":"Cuidamos cada detalle para que salgas con tu mejor imagen.",
                "direccion":"", "telefono":"", "whatsapp":"",
                "horario":"Lunes a viernes: 09:00 - 14:00 y 16:00 - 20:00",
                "logo":"", "foto_portada":"https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=1800&q=85",
                "galeria":"", "sobre_nosotros":"Somos una peluquería dedicada al cuidado de tu imagen."
            }
            for k, v in defaults.items():
                cur.execute("INSERT INTO public.configuracion_web(clave,valor) VALUES(%s,%s) ON CONFLICT(clave) DO NOTHING", (k, v))
            cur.execute("SELECT id FROM public.seguridad WHERE id=1")
            if not cur.fetchone():
                pin = str(st.secrets.get("OWNER_PIN", "1234")).strip()
                salt = secrets.token_bytes(16)
                hashed = hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, 600_000)
                cur.execute("INSERT INTO public.seguridad(id,salt,pin_hash) VALUES(1,%s,%s)", (salt.hex(), hashed.hex()))
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()

def obtener_configuracion():
    return {r["clave"]: r["valor"] or "" for r in consultar("SELECT clave,valor FROM public.configuracion_web")}

def guardar_configuracion(k, v):
    ejecutar("""INSERT INTO public.configuracion_web(clave,valor) VALUES(%s,%s)
    ON CONFLICT(clave) DO UPDATE SET valor=EXCLUDED.valor""", (k, str(v)))

def obtener_servicios(activos=False):
    return consultar("SELECT id,nombre,precio,activo FROM public.servicios " +
                     ("WHERE activo=TRUE " if activos else "") + "ORDER BY nombre")

def obtener_productos(activos=False):
    return consultar("SELECT id,nombre,precio,activo FROM public.productos " +
                     ("WHERE activo=TRUE " if activos else "") + "ORDER BY nombre")

# ============================ HORARIOS Y RESERVAS ============================
def generar_horarios():
    slots = []
    for start, end in [(9*60, 14*60), (16*60, 20*60)]:
        for m in range(start, end, 30):
            slots.append(time(m//60, m%60).strftime("%H:%M"))
    return slots

def hora_texto(v):
    return v.strftime("%H:%M") if hasattr(v, "strftime") else str(v)[:5]

def obtener_horas_ocupadas(fecha_sel):
    return [hora_texto(r["hora"]) for r in consultar("SELECT hora FROM public.citas WHERE fecha=%s", (fecha_sel,))]

def horarios_disponibles(fecha_sel):
    busy = obtener_horas_ocupadas(fecha_sel)
    now = datetime.now().strftime("%H:%M")
    return [h for h in generar_horarios() if h not in busy and (fecha_sel != date.today() or h > now)]

def reservar_cita(cliente, telefono, servicio, precio, fecha_reserva, hora_reserva):
    con = conectar_db()
    try:
        with con.cursor() as cur:
            cur.execute("""INSERT INTO public.citas(cliente,telefono,servicio,precio,fecha,hora,pagada)
            VALUES(%s,%s,%s,%s,%s,%s,FALSE) ON CONFLICT(fecha,hora) DO NOTHING RETURNING id""",
            (cliente, telefono, servicio, precio, fecha_reserva, hora_reserva))
            saved = cur.fetchone()
        con.commit()
        return saved is not None
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()

# ============================ SESIÓN Y NAVEGACIÓN ============================
for k, v in {"pagina":"Inicio", "admin_autenticado":False, "mensaje_pin":"", "login_intentos":0}.items():
    if k not in st.session_state:
        st.session_state[k] = v

def ir_a(p):
    st.session_state.pagina = p
    st.rerun()

def mostrar_encabezado(config):
    name = escape(config.get("nombre", "PELUQUERÍA"))
    c1, c2 = st.columns([1, 3])
    with c1:
        if config.get("logo", "").strip():
            try:
                st.image(config["logo"], width=130)
            except Exception:
                st.markdown(f"## ✂️ {name}")
        else:
            st.markdown(f"## ✂️ {name}")
    with c2:
        st.markdown(f"<div style='text-align:right;padding-top:18px;color:#dfcca5;font-weight:700;letter-spacing:2px'>{name.upper()}</div>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    pages = [("Inicio","⌂ Inicio"),("Servicios","✂ Servicios"),("Reservar","📅 Reservar"),
             ("Galería","📸 Galería"),("Contacto","📍 Contacto"),("Propietario","🔐 Propietario")]
    cols = st.columns(6, gap="small")
    for col, (p, label) in zip(cols, pages):
        with col:
            if st.button(label, key="nav_"+p, use_container_width=True,
                         type="primary" if st.session_state.pagina == p else "secondary"):
                ir_a(p)

def mostrar_footer(config):
    st.markdown(f"""<div class='footer'><strong>{escape(config.get('nombre','PELUQUERÍA'))}</strong><br><br>
    Peluquería · Barbería<br><span class='small-text'>© {datetime.now().year} Todos los derechos reservados</span></div>""",
    unsafe_allow_html=True)

def section(title, subtitle=""):
    st.markdown(f"<div class='section-title'><h2>{escape(title)}</h2><div class='gold-line'></div><p>{escape(subtitle)}</p></div>", unsafe_allow_html=True)

# ============================ PÁGINAS PÚBLICAS ============================
def pagina_inicio(config):
    name = escape(config.get("nombre", "PELUQUERÍA"))
    slogan = escape(config.get("eslogan", "TU ESTILO, NUESTRA PASIÓN"))
    desc = escape(config.get("descripcion", "Cuidamos cada detalle."))
    photo = escape(config.get("foto_portada", "").strip() or
        "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=1800&q=85", quote=True)
    logo = config.get("logo", "").strip()
    logo_html = f"<img class='hero-logo' src='{escape(logo,quote=True)}' alt='Logo'>" if logo else ""
    html = f"<div class='hero' style=\"background-image:url('{photo}')\"><div class='hero-content'>{logo_html}<div class='hero-label'>{name}</div><h1>{slogan}</h1><div class='gold-line'></div><p>{desc}</p></div></div>"
    if callable(getattr(st, "html", None)):
        st.html(html)
    else:
        st.markdown(html, unsafe_allow_html=True)
    mid = st.columns([1, 2, 1])
    with mid[1]:
        if st.button("📅 RESERVAR MI CITA", use_container_width=True, key="home_book"):
            ir_a("Reservar")
    section("BIENVENIDO", "Profesionalidad, estilo y atención personalizada.")
    cols = st.columns(3)
    for col, (title, txt) in zip(cols, [
        ("✂️ Estilo", "Cuidamos cada corte y nos adaptamos a tu personalidad."),
        ("⭐ Profesionalidad", "Atención cercana y servicio profesional."),
        ("📅 Reserva online", "Reserva cómodamente desde cualquier dispositivo.")
    ]):
        with col:
            st.markdown(f"<div class='info-card'><h3>{title}</h3><p>{txt}</p></div>", unsafe_allow_html=True)
    section("NUESTROS SERVICIOS", "Descubre nuestros cortes y tratamientos.")
    services = obtener_servicios(True)
    if services:
        cols = st.columns(min(3, len(services)))
        for i, s in enumerate(services):
            with cols[i % len(cols)]:
                st.markdown(f"<div class='info-card'><h3>{escape(s['nombre'])}</h3><h2>{euros(s['precio'])}</h2></div>", unsafe_allow_html=True)
    else:
        st.info("Próximamente publicaremos nuestros servicios.")
    if st.button("VER TODOS LOS SERVICIOS", use_container_width=True, key="home_services"):
        ir_a("Servicios")

def pagina_servicios():
    section("NUESTROS SERVICIOS Y TARIFAS", "Elige el servicio que mejor se adapta a ti.")
    services = obtener_servicios(True)
    if not services:
        st.info("No hay servicios publicados.")
        return
    cols = st.columns(3)
    for i, s in enumerate(services):
        with cols[i % 3]:
            st.markdown(f"<div class='info-card'><h3>✂️ {escape(s['nombre'])}</h3><h2>{euros(s['precio'])}</h2><p class='small-text'>Disponible bajo reserva.</p></div>", unsafe_allow_html=True)
    if st.button("📅 RESERVAR CITA", use_container_width=True):
        ir_a("Reservar")

def pagina_reservar():
    section("RESERVA TU CITA", "Reserva tu próximo corte de forma rápida y sencilla.")
    services = obtener_servicios(True)
    if not services:
        st.warning("No hay servicios disponibles.")
        return
    c1, c2 = st.columns(2)
    with c1:
        client = st.text_input("Nombre y apellidos", placeholder="Escribe tu nombre", key="book_name")
    with c2:
        phone = st.text_input("Teléfono", placeholder="Tu número de teléfono", key="book_phone")
    selected = st.selectbox("Servicio", services, format_func=lambda s: s["nombre"], key="book_service")
    st.markdown(f"<h3 style='text-align:center'>Precio: {euros(selected['precio'])}</h3>", unsafe_allow_html=True)
    day = st.date_input("Día", min_value=date.today(), value=date.today(), key="book_day")
    available = horarios_disponibles(day)
    hour = st.selectbox("Hora disponible", available, index=None, placeholder="Selecciona una hora",
                        key=f"book_hour_{day.isoformat()}") if available else None
    if not available:
        st.warning("No quedan horarios disponibles.")
    consent = st.checkbox("He leído y acepto la política de privacidad.", key="book_privacy")
    if st.button("CONFIRMAR MI RESERVA", use_container_width=True, key="book_submit"):
        if not client.strip():
            st.error("Introduce tu nombre.")
        elif not phone.strip():
            st.error("Introduce tu teléfono.")
        elif not consent:
            st.error("Debes aceptar la política de privacidad.")
        elif not hour:
            st.error("Selecciona una hora.")
        elif hour not in horarios_disponibles(day):
            st.error("La hora acaba de ocuparse. Selecciona otra.")
        else:
            try:
                ok = reservar_cita(client.strip(), phone.strip(), selected["nombre"], selected["precio"], day, hour)
                if not ok:
                    st.error("Ese horario acaba de reservarse. Prueba otro.")
                    st.rerun()
                else:
                    st.success("¡Cita reservada correctamente!")
                    st.markdown(f"""<div class='info-card'><h2 style='text-align:center'>RESERVA CONFIRMADA</h2>
                    <div class='gold-line'></div><p><b>Cliente:</b> {escape(client)}</p>
                    <p><b>Servicio:</b> {escape(selected['nombre'])}</p><p><b>Fecha:</b> {day.strftime('%d/%m/%Y')}</p>
                    <p><b>Hora:</b> {escape(hour)}</p><h2 style='text-align:center'>{euros(selected['precio'])}</h2></div>""",
                    unsafe_allow_html=True)
            except Exception:
                st.error("No se pudo guardar la reserva. Comprueba la conexión e inténtalo de nuevo.")

def pagina_galeria(config):
    section("NUESTRA GALERÍA", "Conoce nuestro espacio y algunos de nuestros trabajos.")
    urls = [u.strip() for u in config.get("galeria", "").splitlines() if u.strip().startswith(("https://", "http://"))]
    if urls:
        cols = st.columns(2)
        for i, u in enumerate(urls):
            with cols[i % 2]:
                st.image(u, use_container_width=True)
    else:
        st.info("Próximamente publicaremos fotografías.")
        st.image("https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=1400&q=85", use_container_width=True)

def pagina_contacto(config):
    section("CONTACTO", "Estamos aquí para atenderte.")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class='info-card'><h3>📍 Ubicación</h3><p>{escape(config.get('direccion','').strip() or 'Dirección pendiente')}</p>
        <h3>🕒 Horarios</h3><p>{escape(config.get('horario','').strip() or 'Horario pendiente')}</p></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='info-card'><h3>📞 Teléfono</h3><p>{escape(config.get('telefono','').strip() or 'Teléfono pendiente')}</p></div>", unsafe_allow_html=True)
        whatsapp = re.sub(r"\D", "", config.get("whatsapp", ""))
        if whatsapp:
            st.link_button("💬 CONTACTAR POR WHATSAPP", f"https://wa.me/{whatsapp}", use_container_width=True)
    if st.button("📅 RESERVAR CITA", use_container_width=True):
        ir_a("Reservar")

# ============================ HERRAMIENTAS ADMIN ============================
def admin_titulo(titulo, descripcion=""):
    st.markdown(f"""<div class='admin-header'><div class='eyebrow'>ÁREA PRIVADA · ADMINISTRACIÓN</div>
    <h1>{escape(titulo)}</h1><p>{escape(descripcion)}</p></div>""", unsafe_allow_html=True)

def totales_citas(rows):
    cobrado = sum((Decimal(str(x["precio"])) for x in rows if x["pagada"]), Decimal("0"))
    pendiente = sum((Decimal(str(x["precio"])) for x in rows if not x["pagada"]), Decimal("0"))
    return cobrado, pendiente

def obtener_citas_periodo(inicio, fin):
    return consultar("""SELECT id,cliente,telefono,servicio,precio,fecha,hora,pagada
        FROM public.citas WHERE fecha >= %s AND fecha < %s ORDER BY fecha DESC,hora DESC""", (inicio, fin))

# ============================ RESUMEN ============================
def panel_resumen():
    hoy = date.today()
    inicio_mes = hoy.replace(day=1)
    fin_mes = date(hoy.year + 1, 1, 1) if hoy.month == 12 else date(hoy.year, hoy.month + 1, 1)
    citas_hoy = consultar("""SELECT id,cliente,telefono,servicio,precio,fecha,hora,pagada
        FROM public.citas WHERE fecha=%s ORDER BY hora""", (hoy,))
    citas_mes = obtener_citas_periodo(inicio_mes, fin_mes)
    cobrado_hoy, pendiente_hoy = totales_citas(citas_hoy)
    cobrado_mes, pendiente_mes = totales_citas(citas_mes)

    st.markdown("### Resumen de hoy")
    cols = st.columns(4)
    cols[0].metric("Citas de hoy", len(citas_hoy))
    cols[1].metric("Cobrado hoy", euros(cobrado_hoy))
    cols[2].metric("Pendiente de cobro", euros(pendiente_hoy))
    cols[3].metric("Servicios activos", len(obtener_servicios(True)))

    st.markdown("---")
    st.markdown("### Balance del mes")
    a, b, c = st.columns(3)
    a.metric("Ingresos cobrados", euros(cobrado_mes))
    b.metric("Pendiente de cobro", euros(pendiente_mes))
    c.metric("Citas del mes", len(citas_mes))

    st.markdown("---")
    st.markdown("### Agenda de hoy")
    if not citas_hoy:
        st.info("No hay citas programadas para hoy.")
    for x in citas_hoy:
        with st.container(border=True):
            a, b, c = st.columns([1, 3, 1])
            a.markdown(f"## {hora_texto(x['hora'])}")
            b.markdown(f"**{x['cliente']}**")
            b.write(f"{x['servicio']} · {euros(x['precio'])}")
            b.caption(x["telefono"])
            if x["pagada"]:
                c.success("Cobrada")
            else:
                c.warning("Pendiente")

    st.markdown("---")
    st.markdown("### Próximas citas")
    proximas = consultar("""SELECT id,cliente,telefono,servicio,precio,fecha,hora,pagada
        FROM public.citas WHERE fecha > %s ORDER BY fecha,hora LIMIT 8""", (hoy,))
    if not proximas:
        st.info("No hay próximas reservas.")
    for x in proximas:
        with st.container(border=True):
            a, b, c = st.columns([1, 3, 1])
            a.markdown(f"**{x['fecha'].strftime('%d/%m/%Y')}**")
            a.write(hora_texto(x["hora"]))
            b.write(f"**{x['cliente']}**")
            b.write(x["servicio"])
            if x["pagada"]:
                c.success("Cobrada")
            else:
                c.warning("Pendiente")

# ============================ AGENDA ============================
def panel_citas():
    st.markdown("### Agenda de citas")
    st.caption("Consulta las reservas y controla los cobros.")
    c1, c2 = st.columns(2)
    with c1:
        day = st.date_input("Fecha de la agenda", value=date.today(), key="admin_appointments_day")
    with c2:
        filtro = st.selectbox("Estado de pago", ["Todas", "Pendientes", "Cobradas"], key="admin_appointments_filter")
    rows = consultar("""SELECT id,cliente,telefono,servicio,precio,fecha,hora,pagada
        FROM public.citas WHERE fecha=%s ORDER BY hora""", (day,))
    if filtro == "Pendientes":
        rows = [x for x in rows if not x["pagada"]]
    elif filtro == "Cobradas":
        rows = [x for x in rows if x["pagada"]]
    cobrado, pendiente = totales_citas(rows)
    a, b, c = st.columns(3)
    a.metric("Citas", len(rows))
    b.metric("Cobrado", euros(cobrado))
    c.metric("Pendiente", euros(pendiente))
    st.markdown("---")
    if not rows:
        st.info("No hay citas que coincidan con los filtros.")
        return
    for x in rows:
        with st.container(border=True):
            a, b, c = st.columns([1, 3, 1.3])
            with a:
                st.markdown(f"## {hora_texto(x['hora'])}")
                st.caption(x["fecha"].strftime("%d/%m/%Y"))
            with b:
                st.markdown(f"**{x['cliente']}**")
                st.write(x["servicio"])
                st.caption(f"Teléfono: {x['telefono']}")
                st.markdown(f"**{euros(x['precio'])}**")
            with c:
                if x["pagada"]:
                    st.success("PAGADA")
                    if st.button("Marcar pendiente", key=f"unpay_{x['id']}"):
                        ejecutar("UPDATE public.citas SET pagada=FALSE WHERE id=%s", (x["id"],))
                        st.rerun()
                else:
                    st.warning("PENDIENTE")
                    if st.button("✓ COBRAR CITA", key=f"pay_{x['id']}", use_container_width=True):
                        ejecutar("UPDATE public.citas SET pagada=TRUE WHERE id=%s", (x["id"],))
                        st.rerun()

# ============================ CAJA ============================
def panel_caja():
    st.markdown("### Caja y facturación")
    st.caption("Control económico de las citas registradas.")
    hoy = date.today()
    meses = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
    c1, c2 = st.columns(2)
    with c1:
        mes = st.selectbox("Mes", range(1, 13), index=hoy.month-1, format_func=lambda m: meses[m-1])
    with c2:
        anio = st.number_input("Año", min_value=2024, max_value=2100, value=hoy.year, step=1)
    inicio = date(int(anio), mes, 1)
    fin = date(int(anio)+1, 1, 1) if mes == 12 else date(int(anio), mes+1, 1)
    rows = obtener_citas_periodo(inicio, fin)
    cobrado, pendiente = totales_citas(rows)
    st.markdown("---")
    a, b, c = st.columns(3)
    a.metric("Dinero cobrado", euros(cobrado))
    b.metric("Dinero pendiente", euros(pendiente))
    c.metric("Total de citas", len(rows))

    st.markdown("---")
    st.markdown("### Evolución de ingresos diarios")
    datos = consultar("""SELECT fecha,COALESCE(SUM(precio),0) AS total
        FROM public.citas WHERE fecha >= %s AND fecha < %s AND pagada=TRUE
        GROUP BY fecha ORDER BY fecha""", (inicio, fin))
    if datos:
        import pandas as pd
        df = pd.DataFrame([{"Día": x["fecha"], "Ingresos": float(x["total"])} for x in datos]).set_index("Día")
        st.bar_chart(df, y="Ingresos")
    else:
        st.info("Todavía no hay ingresos cobrados en este periodo.")

    st.markdown("---")
    st.markdown("### Histórico de movimientos")
    if not rows:
        st.info("No hay movimientos registrados en este mes.")
        return
    filtro = st.radio("Mostrar", ["Todos", "Solo cobrados", "Solo pendientes"], horizontal=True, key="cash_filter")
    if filtro == "Solo cobrados":
        rows = [x for x in rows if x["pagada"]]
    elif filtro == "Solo pendientes":
        rows = [x for x in rows if not x["pagada"]]
    for x in rows:
        with st.container(border=True):
            a, b, c = st.columns([2, 2, 1])
            a.write(f"**{x['cliente']}**")
            a.caption(x["fecha"].strftime("%d/%m/%Y") + " · " + hora_texto(x["hora"]))
            b.write(x["servicio"])
            b.markdown(f"**{euros(x['precio'])}**")
            if x["pagada"]:
                c.success("PAGADA")
            else:
                c.warning("PENDIENTE")
                if c.button("COBRAR", key=f"histpay_{x['id']}", use_container_width=True):
                    ejecutar("UPDATE public.citas SET pagada=TRUE WHERE id=%s", (x["id"],))
                    st.rerun()

# ============================ SERVICIOS ============================
def panel_servicios():
    st.markdown("### Servicios y tarifas")
    st.caption("Administra los servicios que aparecen en las reservas.")
    rows = obtener_servicios()
    a, b = st.columns(2)
    a.metric("Servicios registrados", len(rows))
    b.metric("Servicios visibles", len([x for x in rows if x["activo"]]))

    with st.expander("＋ AÑADIR NUEVO SERVICIO"):
        with st.form("add_service"):
            name = st.text_input("Nombre del servicio")
            price = st.number_input("Precio (€)", min_value=0.0, value=12.0, step=.5)
            submit = st.form_submit_button("CREAR SERVICIO", use_container_width=True)
        if submit:
            if not name.strip():
                st.error("Escribe un nombre.")
            else:
                try:
                    ejecutar("INSERT INTO public.servicios(nombre,precio,activo) VALUES(%s,%s,TRUE)", (name.strip(), price))
                    st.success("Servicio creado.")
                    st.rerun()
                except psycopg2.IntegrityError:
                    st.error("Ya existe un servicio con ese nombre.")

    st.markdown("---")
    st.markdown("### Servicios registrados")
    if not rows:
        st.info("No hay servicios.")
        return
    for x in rows:
        with st.container(border=True):
            a, b, c = st.columns([3, 1, 1])
            a.markdown(f"**{x['nombre']}**")
            a.caption("Visible en reservas" if x["activo"] else "Oculto para los clientes")
            b.markdown(f"**{euros(x['precio'])}**")
            c.success("Activo") if x["activo"] else c.warning("Inactivo")

    st.markdown("---")
    st.markdown("### Editar servicio")
    mapping = {f"{x['nombre']} · {euros(x['precio'])}": x["id"] for x in rows}
    choice = st.selectbox("Selecciona el servicio", list(mapping), key="service_choice")
    item = next(x for x in rows if x["id"] == mapping[choice])
    with st.form("edit_service"):
        name = st.text_input("Nombre", value=item["nombre"])
        price = st.number_input("Precio", min_value=0.0, value=float(item["precio"]), step=.5)
        active = st.checkbox("Visible en reservas", value=item["activo"])
        save = st.form_submit_button("GUARDAR CAMBIOS", use_container_width=True)
    if save:
        if not name.strip():
            st.error("El nombre no puede estar vacío.")
        else:
            try:
                ejecutar("UPDATE public.servicios SET nombre=%s,precio=%s,activo=%s WHERE id=%s", (name.strip(), price, active, item["id"]))
                st.success("Servicio actualizado.")
                st.rerun()
            except psycopg2.IntegrityError:
                st.error("Ya existe otro servicio con ese nombre.")
    if st.button("🗑️ ELIMINAR SERVICIO", key="delete_service"):
        ejecutar("DELETE FROM public.servicios WHERE id=%s", (item["id"],))
        st.rerun()

# ============================ PRODUCTOS ============================
def panel_productos():
    st.markdown("### Productos")
    st.caption("Controla los productos disponibles en tu negocio.")
    rows = obtener_productos()
    a, b = st.columns(2)
    a.metric("Productos registrados", len(rows))
    b.metric("Productos activos", len([x for x in rows if x["activo"]]))
    with st.expander("＋ AÑADIR PRODUCTO"):
        with st.form("add_product"):
            name = st.text_input("Nombre del producto")
            price = st.number_input("Precio (€)", min_value=0.0, value=10.0, step=.5)
            submit = st.form_submit_button("AÑADIR PRODUCTO", use_container_width=True)
        if submit:
            if not name.strip():
                st.error("Escribe un nombre.")
            else:
                ejecutar("INSERT INTO public.productos(nombre,precio,activo) VALUES(%s,%s,TRUE)", (name.strip(), price))
                st.success("Producto añadido.")
                st.rerun()
    st.markdown("---")
    st.markdown("### Productos registrados")
    if not rows:
        st.info("No hay productos.")
        return
    for x in rows:
        with st.container(border=True):
            a, b, c = st.columns([3, 1, 1])
            a.markdown(f"**{x['nombre']}**")
            b.markdown(f"**{euros(x['precio'])}**")
            c.success("Activo") if x["activo"] else c.warning("Inactivo")
    st.markdown("---")
    st.markdown("### Editar producto")
    mapping = {f"{x['nombre']} · {euros(x['precio'])}": x["id"] for x in rows}
    choice = st.selectbox("Selecciona el producto", list(mapping), key="product_choice")
    item = next(x for x in rows if x["id"] == mapping[choice])
    with st.form("edit_product"):
        name = st.text_input("Nombre", value=item["nombre"])
        price = st.number_input("Precio", min_value=0.0, value=float(item["precio"]), step=.5)
        active = st.checkbox("Producto activo", value=item["activo"])
        save = st.form_submit_button("GUARDAR CAMBIOS", use_container_width=True)
    if save:
        if not name.strip():
            st.error("El nombre no puede estar vacío.")
        else:
            ejecutar("UPDATE public.productos SET nombre=%s,precio=%s,activo=%s WHERE id=%s", (name.strip(), price, active, item["id"]))
            st.success("Producto actualizado.")
            st.rerun()
    if st.button("🗑️ ELIMINAR PRODUCTO", key="delete_product"):
        ejecutar("DELETE FROM public.productos WHERE id=%s", (item["id"],))
        st.rerun()

# ============================ WEB ============================
def panel_web():
    st.markdown("### Personalización de la web")
    st.caption("Modifica los textos, imágenes y datos de contacto que ven tus clientes.")
    cfg = obtener_configuracion()
    with st.form("web_config"):
        tab1, tab2, tab3 = st.tabs(["🏷️ Identidad", "🖼️ Imágenes", "📍 Contacto"])
        with tab1:
            st.markdown("#### Identidad del negocio")
            name = st.text_input("Nombre", value=cfg.get("nombre", ""))
            slogan = st.text_input("Eslogan", value=cfg.get("eslogan", ""))
            desc = st.text_area("Descripción principal", value=cfg.get("descripcion", ""))
            about = st.text_area("Sobre nosotros", value=cfg.get("sobre_nosotros", ""))
        with tab2:
            st.markdown("#### Imagen e identidad visual")
            logo = st.text_input("URL del logotipo", value=cfg.get("logo", ""))
            cover = st.text_input("URL de la imagen de portada", value=cfg.get("foto_portada", ""))
            gallery = st.text_area("URLs de galería (una por línea)", value=cfg.get("galeria", ""))
        with tab3:
            st.markdown("#### Información de contacto")
            address = st.text_input("Dirección", value=cfg.get("direccion", ""))
            phone = st.text_input("Teléfono", value=cfg.get("telefono", ""))
            wa = st.text_input("WhatsApp internacional", value=cfg.get("whatsapp", ""))
            hours = st.text_area("Horario", value=cfg.get("horario", ""))
        save = st.form_submit_button("💾 GUARDAR CONFIGURACIÓN", use_container_width=True)
    if save:
        values = {"nombre":name,"eslogan":slogan,"descripcion":desc,"sobre_nosotros":about,
                  "logo":logo,"foto_portada":cover,"galeria":gallery,"direccion":address,
                  "telefono":phone,"whatsapp":wa,"horario":hours}
        for k, v in values.items():
            guardar_configuracion(k, v)
        st.success("Configuración guardada correctamente.")
        st.rerun()
    st.markdown("---")
    st.markdown("### Vista previa del logotipo")
    if cfg.get("logo", "").strip():
        try:
            st.image(cfg["logo"], width=180)
        except Exception:
            st.warning("No se ha podido cargar el logotipo.")
    else:
        st.info("Todavía no has configurado un logotipo.")

# ============================ CAMBIO DE PIN ============================
def panel_cambiar_pin():
    with st.expander("🔐 SEGURIDAD · Cambiar PIN de acceso"):
        st.caption("Modifica el código que utilizas para entrar en el panel.")
        with st.form("change_pin"):
            old = st.text_input("PIN actual", type="password")
            new = st.text_input("Nuevo PIN (4–12 cifras)", type="password")
            confirm = st.text_input("Confirmar nuevo PIN", type="password")
            submit = st.form_submit_button("ACTUALIZAR PIN", use_container_width=True)
        if submit:
            if not verificar_pin(old):
                st.error("PIN actual incorrecto.")
            elif not new.isdigit() or not 4 <= len(new) <= 12:
                st.error("El PIN debe tener de 4 a 12 cifras.")
            elif new != confirm:
                st.error("La confirmación no coincide.")
            elif new == old:
                st.error("El nuevo PIN debe ser distinto.")
            else:
                guardar_nuevo_pin(new)
                st.session_state.admin_autenticado = False
                st.session_state.mensaje_pin = "PIN actualizado. Inicia sesión de nuevo."
                st.rerun()

# ============================ PANEL PROPIETARIO ============================
def pagina_propietario():
    if not st.session_state.admin_autenticado:
        if st.session_state.mensaje_pin:
            st.success(st.session_state.mensaje_pin)
            st.session_state.mensaje_pin = ""
        st.markdown("""<div class='login-card' style='text-align:center'>
            <div style='font-size:42px'>🔐</div><h2>ÁREA DE PROPIETARIO</h2>
            <p style='color:#aaa69d'>Acceso privado a la administración del negocio.</p></div>""",
            unsafe_allow_html=True)
        with st.form("admin_login"):
            pin = st.text_input("PIN de acceso", type="password", placeholder="Introduce tu PIN")
            submit = st.form_submit_button("ENTRAR AL PANEL", use_container_width=True)
        if submit:
            if st.session_state.login_intentos >= 5:
                st.error("Demasiados intentos. Recarga la sesión más tarde.")
            elif verificar_pin(pin):
                st.session_state.admin_autenticado = True
                st.session_state.login_intentos = 0
                st.rerun()
            else:
                st.session_state.login_intentos += 1
                st.error("PIN incorrecto.")
        return

    admin_titulo("Panel de administración",
        "Gestiona las citas, los ingresos y la presencia online de tu peluquería.")
    a, b = st.columns([4, 1])
    with a:
        st.caption(f"Sesión iniciada · {datetime.now().strftime('%d/%m/%Y')}")
    with b:
        if st.button("SALIR 🔒", key="admin_logout", use_container_width=True):
            st.session_state.admin_autenticado = False
            st.rerun()

    tabs = st.tabs(["📊 Resumen", "📅 Agenda", "💰 Caja", "✂️ Servicios", "🧴 Productos", "🌐 Mi web"])
    with tabs[0]:
        panel_resumen()
    with tabs[1]:
        panel_citas()
    with tabs[2]:
        panel_caja()
    with tabs[3]:
        panel_servicios()
    with tabs[4]:
        panel_productos()
    with tabs[5]:
        panel_web()
    st.markdown("---")
    panel_cambiar_pin()

# ============================ EJECUCIÓN ============================
try:
    inicializar_base_datos()
    config = obtener_configuracion()
    mostrar_encabezado(config)
    page = st.session_state.pagina
    if page == "Inicio":
        pagina_inicio(config)
    elif page == "Servicios":
        pagina_servicios()
    elif page == "Reservar":
        pagina_reservar()
    elif page == "Galería":
        pagina_galeria(config)
    elif page == "Contacto":
        pagina_contacto(config)
    elif page == "Propietario":
        pagina_propietario()
    mostrar_footer(config)
except Exception as e:
    st.error("No se ha podido cargar la aplicación.")
    st.info("Comprueba la conexión con Supabase y las variables configuradas en Secrets.")
    with st.expander("Ver detalle técnico del error"):
        st.code(str(e))
