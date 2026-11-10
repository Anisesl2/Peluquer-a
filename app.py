import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from html import escape
import re
import hashlib
import hmac
import secrets
import logging

# Configuración del registro de errores del sistema
logging.basicConfig(level=logging.WARNING)

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="Peluquería · Estilo & Exclusividad",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# DISEÑO NEGRO Y DORADO REFINADO (LUXURY THEME)
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Montserrat', sans-serif;
}

.stApp {
    background: #0d0d0d;
    color: #f1f1f1;
}

header[data-testid="stHeader"] {
    background: rgba(13,13,13,0.95);
}

.block-container {
    padding-top: 1.8rem;
    padding-bottom: 4rem;
    max-width: 1250px;
}

h1, h2, h3, h4 {
    color: #e6c587 !important;
    font-weight: 700;
}

p, label, span {
    color: #d1d1d1;
}

.gold {
    color: #e6c587;
}

.stButton > button {
    background: linear-gradient(135deg, #e6c587, #b89347);
    color: #0d0d0d;
    border: none;
    border-radius: 8px;
    font-weight: 700;
    min-height: 46px;
    letter-spacing: 0.5px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(230, 197, 135, 0.15);
}

.stButton > button:hover {
    background: linear-gradient(135deg, #f3d69c, #cca353);
    color: #000000;
    box-shadow: 0 6px 16px rgba(230, 197, 135, 0.3);
    transform: translateY(-1px);
}

div[data-testid="stForm"] {
    background: #141414;
    border: 1px solid #3d311d;
    border-radius: 14px;
    padding: 25px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.5);
}

div[data-baseweb="input"],
div[data-baseweb="select"],
div[data-baseweb="textarea"] {
    background-color: #1a1a1a !important;
    border-radius: 8px;
}

div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-testid="stDateInput"] input,
div[data-testid="stTextArea"] textarea {
    background: #1a1a1a !important;
    color: #ffffff !important;
    border: 1px solid #333333;
    border-radius: 8px;
}

div[data-testid="stTabs"] button {
    color: #e6c587;
    font-weight: 600;
}

div[data-testid="stMetric"] {
    background: #141414;
    border: 1px solid #3d311d;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

div[data-testid="stMetricValue"] {
    color: #e6c587 !important;
    font-weight: 800;
}

hr {
    border-color: #3d311d;
    margin: 30px 0;
}

.hero {
    min-height: 500px;
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    border-radius: 16px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 40px;
    position: relative;
    margin-bottom: 30px;
    box-shadow: 0 12px 30px rgba(0,0,0,0.7);
}

.hero::before {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(
        to bottom,
        rgba(13,13,13,0.35),
        rgba(13,13,13,0.90)
    );
}

.hero-content {
    position: relative;
    z-index: 1;
    max-width: 850px;
}

.hero h1 {
    font-size: clamp(32px, 5vw, 60px);
    color: #f7e3bc !important;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 3px;
    margin-bottom: 15px;
    text-shadow: 0 2px 8px rgba(0,0,0,0.8);
}

.hero p {
    color: #e0e0e0;
    font-size: 17px;
    line-height: 1.7;
}

.hero-label {
    color: #e6c587;
    letter-spacing: 6px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.section-title {
    text-align: center;
    margin-top: 40px;
    margin-bottom: 25px;
}

.section-title h2 {
    font-size: 28px;
    letter-spacing: 2px;
}

.section-title p {
    color: #999999;
}

.info-card {
    background: #141414;
    border: 1px solid #3d311d;
    border-radius: 14px;
    padding: 24px;
    height: 100%;
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.info-card:hover {
    border-color: #b89347;
    transform: translateY(-2px);
}

.info-card h3 {
    color: #e6c587;
    margin-bottom: 12px;
}

.gold-line {
    width: 60px;
    height: 3px;
    background: linear-gradient(90deg, #e6c587, #b89347);
    margin: 12px auto 20px auto;
    border-radius: 2px;
}

.footer {
    text-align: center;
    padding: 40px 10px;
    margin-top: 60px;
    border-top: 1px solid #3d311d;
    color: #888888;
}

.footer strong {
    color: #e6c587;
}

.small-text {
    color: #888888;
    font-size: 12px;
}

div[data-testid="stAlert"] {
    border-radius: 10px;
    border: 1px solid #3d311d;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# CONEXIÓN A SUPABASE
# ============================================================

def conectar_db():
    return psycopg2.connect(
        host=st.secrets["DB_HOST"],
        port=st.secrets.get("DB_PORT", 5432),
        database=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        sslmode="require",
        connect_timeout=15
    )


def consultar(sql, parametros=None):
    conexion = conectar_db()
    try:
        with conexion.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql, parametros or ())
            resultado = cursor.fetchall()
            return [dict(fila) for fila in resultado]
    finally:
        conexion.close()


def ejecutar(sql, parametros=None):
    conexion = conectar_db()
    try:
        with conexion.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql, parametros or ())
            resultado = None
            if cursor.description:
                resultado = cursor.fetchall()
            conexion.commit()
            return [dict(fila) for fila in resultado] if resultado else []
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def euros(valor):
    try:
        return f"{float(valor):,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "0,00 €"


# ============================================================
# SEGURIDAD: PIN DEL PROPIETARIO Y RATE LIMITING
# ============================================================

def crear_hash_pin(pin, salt=None):
    if salt is None:
        salt = secrets.token_bytes(16)
    pin_hash = hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), salt, 600_000)
    return salt.hex(), pin_hash.hex()


def obtener_credencial_pin():
    filas = consultar("SELECT salt, pin_hash FROM public.seguridad WHERE id = 1")
    if not filas:
        return None
    return filas[0]


def verificar_pin(pin):
    # Control de intentos fallidos (Rate Limiting)
    if "intentos_pin" not in st.session_state:
        st.session_state.intentos_pin = 0
        st.session_state.bloqueo_hasta = datetime.min

    if datetime.now() < st.session_state.bloqueo_hasta:
        segundos_restantes = (st.session_state.bloqueo_hasta - datetime.now()).seconds
        st.error(f"Demasiados intentos fallidos. Acceso bloqueado temporalmente. Espera {segundos_restantes} segundos.")
        return False

    credencial = obtener_credencial_pin()
    if not credencial:
        return False

    try:
        salt = bytes.fromhex(credencial["salt"])
        hash_guardado = bytes.fromhex(credencial["pin_hash"])
        hash_introducido = hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), salt, 600_000)
        
        valido = hmac.compare_digest(hash_introducido, hash_guardado)
        
        if valido:
            st.session_state.intentos_pin = 0
            return True
        else:
            st.session_state.intentos_pin += 1
            if st.session_state.intentos_pin >= 3:
                st.session_state.bloqueo_hasta = datetime.now() + timedelta(seconds=30)
                st.error("3 intentos incorrectos. Acceso bloqueado por 30 segundos.")
            return False
    except (ValueError, TypeError, KeyError):
        return False


def guardar_nuevo_pin(pin):
    salt_hex, hash_hex = crear_hash_pin(pin)
    ejecutar("""
        INSERT INTO public.seguridad (id, salt, pin_hash, actualizado)
        VALUES (1, %s, %s, NOW())
        ON CONFLICT (id)
        DO UPDATE SET salt = EXCLUDED.salt, pin_hash = EXCLUDED.pin_hash, actualizado = NOW()
    """, (salt_hex, hash_hex))


# ============================================================
# INICIALIZACIÓN DE BASE DE DATOS
# ============================================================

def inicializar_base_datos():
    conexion = conectar_db()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS public.servicios (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(150) NOT NULL UNIQUE,
                    precio NUMERIC(10,2) NOT NULL DEFAULT 0,
                    activo BOOLEAN NOT NULL DEFAULT TRUE
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS public.configuracion_web (
                    clave VARCHAR(100) PRIMARY KEY,
                    valor TEXT
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS public.citas (
                    id SERIAL PRIMARY KEY,
                    cliente VARCHAR(150) NOT NULL,
                    telefono VARCHAR(50) NOT NULL,
                    servicio VARCHAR(150) NOT NULL,
                    precio NUMERIC(10,2) NOT NULL DEFAULT 0,
                    fecha DATE NOT NULL,
                    hora TIME NOT NULL,
                    pagada BOOLEAN NOT NULL DEFAULT FALSE
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS public.productos (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(150) NOT NULL,
                    precio NUMERIC(10,2) NOT NULL DEFAULT 0,
                    activo BOOLEAN NOT NULL DEFAULT TRUE
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS public.seguridad (
                    id SMALLINT PRIMARY KEY CHECK (id = 1),
                    salt VARCHAR(64) NOT NULL,
                    pin_hash VARCHAR(128) NOT NULL,
                    actualizado TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)

            cursor.execute("""
                INSERT INTO public.servicios (nombre, precio, activo)
                VALUES
                    ('Corte de caballero', 12, TRUE),
                    ('Corte infantil', 9, TRUE),
                    ('Arreglo de barba', 7, TRUE),
                    ('Corte + barba', 17, TRUE)
                ON CONFLICT (nombre) DO NOTHING;
            """)

            valores_iniciales = {
                "nombre": "PELUQUERÍA",
                "eslogan": "TU ESTILO, NUESTRA PASIÓN",
                "descripcion": "Cuidamos cada detalle para ofrecerte una experiencia y una imagen impecables.",
                "direccion": "",
                "telefono": "",
                "whatsapp": "",
                "horario": "Lunes a viernes: 09:00 - 14:00 y 16:00 - 20:00",
                "logo": "",
                "foto_portada": "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=1800&q=85",
                "galeria": "",
                "sobre_nosotros": "Somos profesionales dedicados al cuidado personal con una larga trayectoria en el sector."
            }

            for clave, valor in valores_iniciales.items():
                cursor.execute("""
                    INSERT INTO public.configuracion_web (clave, valor)
                    VALUES (%s, %s)
                    ON CONFLICT (clave) DO NOTHING;
                """, (clave, valor))

            pin_inicial = str(st.secrets.get("OWNER_PIN", "1234")).strip()
            cursor.execute("SELECT id FROM public.seguridad WHERE id = 1")
            if not cursor.fetchone():
                salt, pin_hash = crear_hash_pin(pin_inicial)
                cursor.execute("""
                    INSERT INTO public.seguridad (id, salt, pin_hash, actualizado)
                    VALUES (1, %s, %s, NOW())
                """, (salt, pin_hash))

        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


# ============================================================
# FUNCIONES DE CONSULTA CONFIGURACIÓN Y SERVICIOS
# ============================================================

def obtener_configuracion():
    filas = consultar("SELECT clave, valor FROM public.configuracion_web")
    return {fila["clave"]: fila["valor"] or "" for fila in filas}


def guardar_configuracion(clave, valor):
    ejecutar("""
        INSERT INTO public.configuracion_web (clave, valor)
        VALUES (%s, %s)
        ON CONFLICT (clave) DO UPDATE SET valor = EXCLUDED.valor
    """, (clave, str(valor)))


def obtener_servicios(activos=False):
    if activos:
        return consultar("SELECT id, nombre, precio, activo FROM public.servicios WHERE activo = TRUE ORDER BY nombre")
    return consultar("SELECT id, nombre, precio, activo FROM public.servicios ORDER BY nombre")


def obtener_productos(activos=False):
    if activos:
        return consultar("SELECT id, nombre, precio, activo FROM public.productos WHERE activo = TRUE ORDER BY nombre")
    return consultar("SELECT id, nombre, precio, activo FROM public.productos ORDER BY nombre")


# ============================================================
# GESTIÓN DE HORARIOS
# ============================================================

def generar_horarios():
    horarios = []
    for minutos in range(9 * 60, 14 * 60, 30):
        horarios.append(time(minutos // 60, minutos % 60).strftime("%H:%M"))
    for minutos in range(16 * 60, 20 * 60, 30):
        horarios.append(time(minutos // 60, minutos % 60).strftime("%H:%M"))
    return horarios


def hora_texto(valor):
    if hasattr(valor, "strftime"):
        return valor.strftime("%H:%M")
    return str(valor)[:5]


def obtener_horas_ocupadas(fecha_seleccionada):
    filas = consultar("SELECT hora FROM public.citas WHERE fecha = %s", (fecha_seleccionada,))
    return [hora_texto(fila["hora"]) for fila in filas]


def horarios_disponibles(fecha_seleccionada):
    todos = generar_horarios()
    ocupados = obtener_horas_ocupadas(fecha_seleccionada)
    disponibles = [h for h in todos if h not in ocupados]

    if fecha_seleccionada == date.today():
        hora_actual = datetime.now().strftime("%H:%M")
        disponibles = [h for h in disponibles if h > hora_actual]

    return disponibles


# ============================================================
# CONTROL DE ESTADO DE SESIÓN
# ============================================================

if "pagina" not in st.session_state:
    st.session_state.pagina = "Inicio"

if "admin_autenticado" not in st.session_state:
    st.session_state.admin_autenticado = False

if "mensaje_pin" not in st.session_state:
    st.session_state.mensaje_pin = ""


def ir_a(pagina):
    st.session_state.pagina = pagina
    st.rerun()


# ============================================================
# COMPONENTES DE INTERFAZ: ENCABEZADO Y PIE
# ============================================================

def mostrar_encabezado(config):
    logo = config.get("logo", "").strip()
    nombre = config.get("nombre", "PELUQUERÍA")

    c1, c2 = st.columns([1, 3])
    with c1:
        if logo:
            try:
                st.image(logo, width=140)
            except Exception:
                st.markdown(f"## ✂️ {escape(nombre)}")
        else:
            st.markdown(f"## ✂️ {escape(nombre)}")

    with c2:
        st.markdown(
            f"<div style='text-align:right;padding-top:15px;color:#e6c587;font-weight:700;letter-spacing:2px;'>"
            f"{escape(nombre.upper())}</div>",
            unsafe_allow_html=True
        )

    st.markdown("<hr>", unsafe_allow_html=True)

    columnas = st.columns(6)
    paginas = [
        ("Inicio", "⌂ Inicio"),
        ("Servicios", "✂ Servicios"),
        ("Reservar", "📅 Reservar"),
        ("Galería", "📸 Galería"),
        ("Contacto", "📍 Contacto"),
        ("Propietario", "🔐 Propietario")
    ]

    for columna, (pagina, texto) in zip(columnas, paginas):
        with columna:
            if st.button(texto, key=f"nav_{pagina}", use_container_width=True):
                ir_a(pagina)


def mostrar_footer(config):
    nombre = escape(config.get("nombre", "PELUQUERÍA"))
    st.markdown(f"""
    <div class="footer">
        <strong>{nombre}</strong><br><br>
        Servicios Profesionales de Peluquería y Barbería<br>
        <span class="small-text">© {datetime.now().year} Todos los derechos reservados</span>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# PÁGINAS PÚBLICAS
# ============================================================

def pagina_inicio(config):
    nombre = escape(config.get("nombre", "PELUQUERÍA"))
    eslogan = escape(config.get("eslogan", "TU ESTILO, NUESTRA PASIÓN"))
    descripcion = escape(config.get("descripcion", "Cuidamos cada detalle para ti."))
    foto = config.get("foto_portada", "").strip() or "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=1800&q=85"

    st.markdown(f"""
    <div class="hero" style="background-image:url('{escape(foto, quote=True)}');">
        <div class="hero-content">
            <div class="hero-label">{nombre}</div>
            <h1>{eslogan}</h1>
            <div class="gold-line"></div>
            <p>{descripcion}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    centro = st.columns([1, 2, 1])
    with centro[1]:
        if st.button("📅  RESERVAR MI CITA AHORA", use_container_width=True, key="inicio_reservar"):
            ir_a("Reservar")

    st.markdown("""
    <div class="section-title">
        <h2>EXCELENCIA Y ESTILO</h2>
        <div class="gold-line"></div>
        <p>Profesionalidad y atención totalmente personalizada.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="info-card">
            <h3>✂️ Estilo Único</h3>
            <p>Cortes modernos y clásicos adaptados perfectamente a tu personalidad y facciones.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="info-card">
            <h3>⭐ Calidad Garantizada</h3>
            <p>Productos de alta gama y un trato cercano para que disfrutes de una experiencia única.</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="info-card">
            <h3>📅 Reserva Online</h3>
            <p>Elige tu servicio favorito, selecciona fecha y hora en segundos sin esperas.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="section-title">
        <h2>SERVICIOS DESTACADOS</h2>
        <div class="gold-line"></div>
        <p>Conoce algunos de nuestros servicios principales.</p>
    </div>
    """, unsafe_allow_html=True)

    servicios = obtener_servicios(activos=True)
    if servicios:
        columnas = st.columns(min(3, len(servicios)))
        for i, servicio in enumerate(servicios[:3]):
            with columnas[i % len(columnas)]:
                st.markdown(f"""
                <div class="info-card">
                    <h3>{escape(servicio['nombre'])}</h3>
                    <h2>{euros(servicio['precio'])}</h2>
                </div>
                """, unsafe_allow_html=True)


def pagina_servicios():
    st.markdown("""
    <div class="section-title">
        <h2>NUESTROS SERVICIOS Y TARIFAS</h2>
        <div class="gold-line"></div>
        <p>Descubre nuestra carta de servicios profesionales.</p>
    </div>
    """, unsafe_allow_html=True)

    servicios = obtener_servicios(activos=True)
    if not servicios:
        st.info("Actualmente no hay servicios publicados.")
        return

    columnas = st.columns(3)
    for i, servicio in enumerate(servicios):
        with columnas[i % 3]:
            st.markdown(f"""
            <div class="info-card" style="margin-bottom:20px;">
                <h3>✂️ {escape(servicio['nombre'])}</h3>
                <h2>{euros(servicio['precio'])}</h2>
                <p class="small-text">Disponible mediante reserva previa online.</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📅 RESERVAR CITA AHORA", use_container_width=True):
            ir_a("Reservar")


def pagina_reservar():
    st.markdown("""
    <div class="section-title">
        <h2>RESERVA TU CITA</h2>
        <div class="gold-line"></div>
        <p>Selecciona el servicio, fecha y hora que mejor te convengan.</p>
    </div>
    """, unsafe_allow_html=True)

    servicios = obtener_servicios(activos=True)
    if not servicios:
        st.warning("No hay servicios disponibles para reserva en este momento.")
        return

    nombres = [s["nombre"] for s in servicios]

    with st.form("formulario_reserva"):
        cliente = st.text_input("Nombre y Apellidos *", placeholder="Tu nombre completo")
        telefono = st.text_input("Teléfono de contacto *", placeholder="Ej: 600000000")
        
        servicio_nombre = st.selectbox("Selecciona el servicio", nombres)
        servicio_elegido = next(s for s in servicios if s["nombre"] == servicio_nombre)

        st.markdown(f"<h3 style='text-align:center; color:#e6c587;'>Precio: {euros(servicio_elegido['precio'])}</h3>", unsafe_allow_html=True)

        fecha_seleccionada = st.date_input("Fecha de la cita", min_value=date.today(), value=date.today())
        
        disponibles = horarios_disponibles(fecha_seleccionada)
        if disponibles:
            hora_seleccionada = st.selectbox("Hora disponible", disponibles)
        else:
            hora_seleccionada = None
            st.warning("No hay horas libres para la fecha seleccionada.")

        aceptar = st.checkbox("He leído y acepto la política de protección de datos y privacidad.")
        enviar = st.form_submit_button("CONFIRMAR Y RESERVAR CITA", use_container_width=True)

    if enviar:
        telefono_limpio = re.sub(r"[^\d+]", "", telefono)
        if not cliente.strip():
            st.error("Por favor, introduce tu nombre.")
        elif not telefono.strip() or len(telefono_limpio) < 6:
            st.error("Introduce un número de teléfono válido.")
        elif not aceptar:
            st.error("Debes aceptar la política de privacidad.")
        elif not hora_seleccionada:
            st.error("Selecciona un horario válido.")
        else:
            ocupadas = obtener_horas_ocupadas(fecha_seleccionada)
            if hora_seleccionada in ocupadas:
                st.error("Lo sentimos, esa hora acaba de ser reservada por otro cliente. Por favor, selecciona otra.")
            else:
                try:
                    ejecutar("""
                        INSERT INTO public.citas (cliente, telefono, servicio, precio, fecha, hora, pagada)
                        VALUES (%s, %s, %s, %s, %s, %s, FALSE)
                    """, (
                        cliente.strip(),
                        telefono_limpio,
                        servicio_elegido["nombre"],
                        servicio_elegido["precio"],
                        fecha_seleccionada,
                        hora_seleccionada
                    ))

                    st.success("¡Cita reservada con éxito!")
                    st.markdown(f"""
                    <div class="info-card">
                        <h3 style="text-align:center;">RESUMEN DE TU CITA</h3>
                        <div class="gold-line"></div>
                        <p><strong>Cliente:</strong> {escape(cliente)}</p>
                        <p><strong>Servicio:</strong> {escape(servicio_elegido['nombre'])}</p>
                        <p><strong>Fecha:</strong> {fecha_seleccionada.strftime('%d/%m/%Y')}</p>
                        <p><strong>Hora:</strong> {escape(hora_seleccionada)}</p>
                        <h3 style="text-align:center; color:#e6c587;">Total: {euros(servicio_elegido['precio'])}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception:
                    st.error("Error al registrar la cita. Inténtalo de nuevo más tarde.")


def pagina_galeria(config):
    st.markdown("""
    <div class="section-title">
        <h2>GALERÍA DE TRABAJOS</h2>
        <div class="gold-line"></div>
        <p>Un vistazo a nuestro espacio y mejores acabados.</p>
    </div>
    """, unsafe_allow_html=True)

    galeria = config.get("galeria", "").strip()
    if galeria:
        imagenes = [url.strip() for url in galeria.splitlines() if url.strip().startswith(("http://", "https://"))]
        if imagenes:
            columnas = st.columns(2)
            for i, imagen in enumerate(imagenes):
                with columnas[i % 2]:
                    st.image(imagen, use_container_width=True)
        else:
            st.info("Aún no hay imágenes válidas configuradas en la galería.")
    else:
        st.markdown("<p style='text-align:center; color:#888;'>Próximamente publicaremos imágenes de nuestro salón.</p>", unsafe_allow_html=True)
        st.image("https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=1400&q=85", use_container_width=True)


def pagina_contacto(config):
    st.markdown("""
    <div class="section-title">
        <h2>CONTACTO Y LOCALIZACIÓN</h2>
        <div class="gold-line"></div>
        <p>Estamos a tu entera disposición.</p>
    </div>
    """, unsafe_allow_html=True)

    direccion = config.get("direccion", "").strip()
    telefono = config.get("telefono", "").strip()
    whatsapp = config.get("whatsapp", "").strip()
    horario = config.get("horario", "").strip()

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="info-card">
            <h3>📍 Dirección</h3>
            <p>{escape(direccion) if direccion else 'Dirección pendiente de configurar.'}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="info-card">
            <h3>🕒 Horarios</h3>
            <p>{escape(horario) if horario else 'Horario pendiente de configurar.'}</p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="info-card">
            <h3>📞 Teléfono</h3>
            <p>{escape(telefono) if telefono else 'Teléfono pendiente de configurar.'}</p>
        </div>
        """, unsafe_allow_html=True)

        if whatsapp:
            numero = re.sub(r"\D", "", whatsapp)
            if numero:
                st.markdown("<br>", unsafe_allow_html=True)
                st.link_button("💬 ESCRIBIR POR WHATSAPP", f"https://wa.me/{numero}", use_container_width=True)


# ============================================================
# PANEL DE PROPIETARIO Y ADMINISTRACIÓN
# ============================================================

def panel_cambiar_pin():
    st.markdown("---")
    with st.expander("🔐 CAMBIAR PIN DE ACCESO", expanded=False):
        st.write("Modifica el PIN de seguridad del panel de administración.")
        with st.form("form_cambiar_pin"):
            pin_actual = st.text_input("PIN actual", type="password")
            pin_nuevo = st.text_input("Nuevo PIN (4 a 12 dígitos)", type="password")
            confirmar_pin = st.text_input("Confirma el nuevo PIN", type="password")
            cambiar = st.form_submit_button("ACTUALIZAR PIN", use_container_width=True)

        if cambiar:
            if not verificar_pin(pin_actual):
                st.error("El PIN actual no es correcto.")
            elif not pin_nuevo.isdigit() or not (4 <= len(pin_nuevo) <= 12):
                st.error("El nuevo PIN debe tener entre 4 y 12 dígitos numéricos.")
            elif pin_nuevo != confirmar_pin:
                st.error("Los nuevos PINs no coinciden.")
            elif pin_nuevo == pin_actual:
                st.error("El nuevo PIN debe ser diferente al actual.")
            else:
                try:
                    guardar_nuevo_pin(pin_nuevo)
                    st.session_state.admin_autenticado = False
                    st.session_state.mensaje_pin = "¡PIN actualizado con éxito! Inicia sesión de nuevo."
                    st.rerun()
                except Exception:
                    st.error("Error al actualizar el PIN.")


def pagina_propietario():
    if not st.session_state.admin_autenticado:
        if st.session_state.mensaje_pin:
            st.success(st.session_state.mensaje_pin)
            st.session_state.mensaje_pin = ""

        st.markdown("""
        <div class="section-title">
            <h2>ACCESO DE PROPIETARIO</h2>
            <div class="gold-line"></div>
            <p>Introduce tu PIN para acceder al panel de gestión.</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_propietario"):
            pin = st.text_input("PIN de Acceso", type="password")
            entrar = st.form_submit_button("ACCEDER AL PANEL", use_container_width=True)

        if entrar:
            if verificar_pin(pin):
                st.session_state.admin_autenticado = True
                st.rerun()
            else:
                st.error("PIN incorrecto.")
        return

    st.markdown("""
    <div class="section-title">
        <h2>PANEL DE GESTIÓN Y ADMINISTRACIÓN</h2>
        <div class="gold-line"></div>
        <p>Control integral de tu negocio.</p>
    </div>
    """, unsafe_allow_html=True)

    col_salir1, col_salir2, col_salir3 = st.columns([2, 1, 2])
    with col_salir2:
        if st.button("🚪 CERRAR SESIÓN", use_container_width=True):
            st.session_state.admin_autenticado = False
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    pestañas = st.tabs(["📅 Citas", "💰 Caja", "✂️ Servicios", "🧴 Productos", "🌐 Web"])

    with pestañas[0]:
        panel_citas()
    with pestañas[1]:
        panel_caja()
    with pestañas[2]:
        panel_servicios()
    with pestañas[3]:
        panel_productos()
    with pestañas[4]:
        panel_web()

    panel_cambiar_pin()


def panel_citas():
    st.subheader("Gestión de Citas Diarias")
    fecha_consulta = st.date_input("Seleccionar fecha", value=date.today(), key="fecha_citas_admin")

    citas = consultar("""
        SELECT id, cliente, telefono, servicio, precio, fecha, hora, pagada
        FROM public.citas WHERE fecha = %s ORDER BY hora
    """, (fecha_consulta,))

    total_citas = len(citas)
    total_cobrado = sum((Decimal(str(c["precio"])) for c in citas if c["pagada"]), Decimal("0"))
    pendiente = sum((Decimal(str(c["precio"])) for c in citas if not c["pagada"]), Decimal("0"))

    c1, c2, c3 = st.columns(3)
    c1.metric("Citas programadas", total_citas)
    c2.metric("Cobrado", euros(total_cobrado))
    c3.metric("Pendiente de cobro", euros(pendiente))

    st.markdown("---")
    if not citas:
        st.info("No hay citas registradas para esta fecha.")
        return

    for cita in citas:
        hora = hora_texto(cita["hora"])
        with st.container(border=True):
            c1, c2, c3 = st.columns([2, 2, 1])
            with c1:
                st.markdown(f"### 🕒 {hora}")
                st.write(f"**Cliente:** {escape(cita['cliente'])}")
                st.write(f"**Teléfono:** {escape(cita['telefono'])}")
            with c2:
                st.write(f"**Servicio:** {escape(cita['servicio'])}")
                st.write(f"**Precio:** {euros(cita['precio'])}")
                if cita["pagada"]:
                    st.success("PAGADA")
                else:
                    st.warning("PENDIENTE")
            with c3:
                if not cita["pagada"]:
                    if st.button("COBRAR", key=f"cobrar_cita_{cita['id']}", use_container_width=True):
                        ejecutar("UPDATE public.citas SET pagada = TRUE WHERE id = %s", (cita["id"],))
                        st.success("¡Cobrada!")
                        st.rerun()


def panel_caja():
    st.subheader("Control de Caja y Facturación")
    hoy = date.today()
    citas_hoy = consultar("SELECT precio, pagada FROM public.citas WHERE fecha = %s", (hoy,))
    
    cobrado_hoy = sum((Decimal(str(c["precio"])) for c in citas_hoy if c["pagada"]), Decimal("0"))
    pendiente_hoy = sum((Decimal(str(c["precio"])) for c in citas_hoy if not c["pagada"]), Decimal("0"))

    c1, c2, c3 = st.columns(3)
    c1.metric("Ingresos Hoy (Cobrado)", euros(cobrado_hoy))
    c2.metric("Pendiente Hoy", euros(pendiente_hoy))
    c3.metric("Citas Totales Hoy", len(citas_hoy))

    st.markdown("---")
    st.markdown("### Resumen Mensual")

    col_mes, col_anio = st.columns(2)
    with col_mes:
        mes = st.selectbox(
            "Mes", list(range(1, 13)), index=hoy.month - 1,
            format_func=lambda x: ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"][x - 1]
        )
    with col_anio:
        anio = st.number_input("Año", min_value=2024, max_value=2100, value=hoy.year, step=1)

    primer_dia = date(int(anio), mes, 1)
    primer_dia_siguiente = date(int(anio) + 1, 1, 1) if mes == 12 else date(int(anio), mes + 1, 1)

    citas_mes = consultar("""
        SELECT id, cliente, telefono, servicio, precio, fecha, hora, pagada
        FROM public.citas WHERE fecha >= %s AND fecha < %s ORDER BY fecha DESC, hora DESC
    """, (primer_dia, primer_dia_siguiente))

    cobrado_mes = sum((Decimal(str(c["precio"])) for c in citas_mes if c["pagada"]), Decimal("0"))
    pendiente_mes = sum((Decimal(str(c["precio"])) for c in citas_mes if not c["pagada"]), Decimal("0"))

    cm1, cm2, cm3 = st.columns(3)
    cm1.metric("Ingresos Cobrados (Mes)", euros(cobrado_mes))
    cm2.metric("Pendiente (Mes)", euros(pendiente_mes))
    cm3.metric("Total Citas Mes", len(citas_mes))


def panel_servicios():
    st.subheader("Gestión de Servicios")

    with st.expander("➕ Añadir Nuevo Servicio", expanded=False):
        with st.form("nuevo_servicio"):
            nombre = st.text_input("Nombre del servicio")
            precio = st.number_input("Precio (€)", min_value=0.0, value=12.0, step=0.5)
            crear = st.form_submit_button("GUARDAR SERVICIO", use_container_width=True)

        if crear:
            if not nombre.strip():
                st.error("Introduce el nombre del servicio.")
            else:
                try:
                    ejecutar("INSERT INTO public.servicios (nombre, precio, activo) VALUES (%s, %s, TRUE)", (nombre.strip(), precio))
                    st.success("¡Servicio añadido correctamente!")
                    st.rerun()
                except psycopg2.IntegrityError:
                    st.error("Ya existe un servicio con ese nombre.")

    servicios = obtener_servicios()
    if not servicios:
        st.info("No hay servicios registrados.")
        return

    st.markdown("---")
    opciones = {f"{s['nombre']} — {euros(s['precio'])}": s["id"] for s in servicios}
    seleccion = st.selectbox("Selecciona un servicio para editar", list(opciones.keys()))
    servicio = next(s for s in servicios if s["id"] == opciones[seleccion])

    with st.form("editar_servicio"):
        nombre_nuevo = st.text_input("Nombre", value=servicio["nombre"])
        precio_nuevo = st.number_input("Precio (€)", min_value=0.0, value=float(servicio["precio"]), step=0.5)
        activo_nuevo = st.checkbox("Servicio visible públicamente", value=servicio["activo"])
        guardar = st.form_submit_button("ACTUALIZAR SERVICIO", use_container_width=True)

    if guardar:
        try:
            ejecutar("UPDATE public.servicios SET nombre = %s, precio = %s, activo = %s WHERE id = %s",
                     (nombre_nuevo.strip(), precio_nuevo, activo_nuevo, servicio["id"]))
            st.success("¡Servicio actualizado!")
            st.rerun()
        except psycopg2.IntegrityError:
            st.error("Ya existe otro servicio con ese nombre.")

    if st.button("🗑️ ELIMINAR SERVICIO"):
        ejecutar("DELETE FROM public.servicios WHERE id = %s", (servicio["id"],))
        st.success("Servicio eliminado.")
        st.rerun()


def panel_productos():
    st.subheader("Gestión de Productos")
    with st.expander("➕ Añadir Producto", expanded=False):
        with st.form("nuevo_producto"):
            nombre = st.text_input("Nombre del producto")
            precio = st.number_input("Precio (€)", min_value=0.0, value=10.0, step=0.5)
            crear = st.form_submit_button("AÑADIR PRODUCTO", use_container_width=True)

        if crear:
            if not nombre.strip():
                st.error("Introduce el nombre.")
            else:
                ejecutar("INSERT INTO public.productos (nombre, precio, activo) VALUES (%s, %s, TRUE)", (nombre.strip(), precio))
                st.success("Producto añadido.")
                st.rerun()

    productos = obtener_productos()
    if productos:
        st.markdown("---")
        opciones = {f"{p['nombre']} — {euros(p['precio'])}": p["id"] for p in productos}
        seleccion = st.selectbox("Seleccionar producto", list(opciones.keys()), key="sel_prod")
        producto = next(p for p in productos if p["id"] == opciones[seleccion])

        with st.form("edit_prod"):
            nom = st.text_input("Nombre", value=producto["nombre"])
            pre = st.number_input("Precio (€)", min_value=0.0, value=float(producto["precio"]), step=0.5)
            act = st.checkbox("Activo", value=producto["activo"])
            if st.form_submit_button("Guardar Cambios", use_container_width=True):
                ejecutar("UPDATE public.productos SET nombre=%s, precio=%s, activo=%s WHERE id=%s", (nom, pre, act, producto["id"]))
                st.success("Actualizado.")
                st.rerun()


def panel_web():
    st.subheader("Personalización del Sitio Web")
    config = obtener_configuracion()

    with st.form("form_configuracion_web"):
        nombre = st.text_input("Nombre de la Peluquería", value=config.get("nombre", ""))
        eslogan = st.text_input("Eslogan Principal", value=config.get("eslogan", ""))
        descripcion = st.text_area("Descripción de la Portada", value=config.get("descripcion", ""))
        sobre_nosotros = st.text_area("Sección Sobre Nosotros", value=config.get("sobre_nosotros", ""))
        
        st.markdown("### Multimedia e Identidad")
        logo = st.text_input("URL del Logotipo", value=config.get("logo", ""))
        foto_portada = st.text_input("URL de la Fotografía Principal (Hero)", value=config.get("foto_portada", ""))
        galeria = st.text_area("URLs de la Galería (una por línea)", value=config.get("galeria", ""))

        st.markdown("### Contacto")
        direccion = st.text_input("Dirección física", value=config.get("direccion", ""))
        telefono = st.text_input("Teléfono de contacto", value=config.get("telefono", ""))
        whatsapp = st.text_input("WhatsApp (ej: 34600111222)", value=config.get("whatsapp", ""))
        horario = st.text_area("Horarios comerciales", value=config.get("horario", ""))

        guardar = st.form_submit_button("GUARDAR CONFIGURACIÓN WEB", use_container_width=True)

    if guardar:
        valores = {
            "nombre": nombre, "eslogan": eslogan, "descripcion": descripcion,
            "sobre_nosotros": sobre_nosotros, "logo": logo, "foto_portada": foto_portada,
            "galeria": galeria, "direccion": direccion, "telefono": telefono,
            "whatsapp": whatsapp, "horario": horario
        }
        for clave, valor in valores.items():
            guardar_configuracion(clave, valor)
        st.success("¡Configuración guardada correctamente!")
        st.rerun()


# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================

try:
    inicializar_base_datos()
    configuracion = obtener_configuracion()
    mostrar_encabezado(configuracion)

    pagina = st.session_state.pagina
    if pagina == "Inicio":
        pagina_inicio(configuracion)
    elif pagina == "Servicios":
        pagina_servicios()
    elif pagina == "Reservar":
        pagina_reservar()
    elif pagina == "Galería":
        pagina_galeria(configuracion)
    elif pagina == "Contacto":
        pagina_contacto(configuracion)
    elif pagina == "Propietario":
        pagina_propietario()

    mostrar_footer(configuracion)

except Exception as error:
    logging.error(f"Error crítico en la aplicación: {error}")
    st.error("Ha ocurrido un error inesperado al conectar con la base de datos.")
    st.info("Verifica que las credenciales de Supabase en los secretos de Streamlit sean correctas.")
