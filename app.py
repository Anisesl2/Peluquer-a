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

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="Peluquería",
    page_icon="💈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# DISEÑO NEGRO Y DORADO
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Playfair+Display:wght@400;500;600;700&display=swap');

:root {
    --carbon: #111211;
    --anthracite: #1b1c1a;
    --surface: #222320;
    --surface-soft: #292a26;
    --champagne: #c7ad7b;
    --champagne-light: #dfcca5;
    --cream: #eee9df;
    --muted: #aaa69d;
    --line: rgba(199,173,123,.22);
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(ellipse at 50% -15%, rgba(199,173,123,.075), transparent 42%),
        var(--carbon);
    color: var(--cream);
}

header[data-testid="stHeader"] {
    background: rgba(17,18,17,.94);
}

.block-container {
    max-width: 1280px;
    padding: 1.35rem 2.2rem 3.5rem;
}

h1, h2, h3, h4 {
    color: var(--champagne-light) !important;
    font-family: 'Playfair Display', Georgia, serif;
    font-weight: 500;
    letter-spacing: .01em;
}

p, label, span, div {
    color: inherit;
}

a { color: var(--champagne-light) !important; }

.stButton > button, .stLinkButton > a, div[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(135deg, #d8c49b 0%, #b89b68 100%);
    color: #171713 !important;
    border: 1px solid rgba(235,220,188,.55);
    border-radius: 4px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 700;
    letter-spacing: .075em;
    min-height: 48px;
    padding: .65rem 1.1rem;
    box-shadow: 0 5px 18px rgba(0,0,0,.18);
    transition: transform .2s ease, filter .2s ease, box-shadow .2s ease;
}

.stButton > button:hover, .stLinkButton > a:hover,
div[data-testid="stFormSubmitButton"] button:hover {
    background: linear-gradient(135deg, #ead9b5 0%, #c7ad7b 100%);
    color: #111 !important;
    border-color: var(--champagne-light);
    transform: translateY(-1px);
    box-shadow: 0 8px 22px rgba(0,0,0,.28);
}

div[data-testid="stForm"] {
    background: linear-gradient(145deg, rgba(37,38,34,.98), rgba(27,28,26,.98));
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 24px;
    box-shadow: 0 12px 34px rgba(0,0,0,.16);
}

div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="textarea"] {
    background-color: var(--surface-soft);
}

div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-testid="stDateInput"] input,
div[data-testid="stTextArea"] textarea {
    background: var(--surface-soft);
    color: var(--cream);
    border-color: rgba(199,173,123,.24);
    border-radius: 4px;
}

div[data-testid="stTabs"] button {
    color: var(--champagne-light);
    font-weight: 600;
}

div[data-testid="stMetric"] {
    background: linear-gradient(145deg, #242521, #1b1c1a);
    border: 1px solid var(--line);
    padding: 17px;
    border-radius: 7px;
}

div[data-testid="stMetricValue"] {
    color: var(--champagne-light);
}

div[data-testid="stMetricLabel"] {
    color: var(--muted);
}

hr { border-color: var(--line); }

.hero {
    min-height: 610px;
    background-size: cover;
    background-position: center 44%;
    background-repeat: no-repeat;
    border: 1px solid rgba(223,204,165,.2);
    border-radius: 5px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 48px 34px;
    position: relative;
    margin: 12px 0 30px;
    box-shadow: 0 24px 60px rgba(0,0,0,.32);
}

.hero::before {
    content: "";
    position: absolute;
    inset: 0;
    background:
        linear-gradient(180deg, rgba(10,11,10,.28) 0%, rgba(10,11,10,.46) 42%, rgba(10,11,10,.88) 100%),
        linear-gradient(90deg, rgba(10,11,10,.30), transparent 55%, rgba(10,11,10,.22));
}

.hero-content {
    position: relative;
    z-index: 1;
    max-width: 860px;
}

.hero-logo {
    max-width: 118px;
    max-height: 100px;
    object-fit: contain;
    margin: 0 auto 25px;
    filter: drop-shadow(0 4px 14px rgba(0,0,0,.4));
}

.hero-label {
    color: var(--champagne-light);
    letter-spacing: .34em;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    margin-bottom: 17px;
}

.hero h1 {
    font-size: clamp(34px, 5.6vw, 68px);
    line-height: 1.08;
    color: #f1e7d3 !important;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: .055em;
    margin: 0 0 18px;
    text-shadow: 0 3px 22px rgba(0,0,0,.4);
}

.hero p {
    color: #f0ece4;
    font-size: clamp(14px, 1.5vw, 17px);
    line-height: 1.85;
    max-width: 650px;
    margin: 0 auto;
}

.section-title {
    text-align: center;
    margin: 54px 0 30px;
}

.section-title h2 {
    font-size: clamp(25px, 3vw, 34px);
    letter-spacing: .07em;
}

.section-title p {
    color: var(--muted);
    font-size: 14px;
    letter-spacing: .025em;
}

.info-card {
    background: linear-gradient(145deg, #242521, #1b1c1a);
    border: 1px solid var(--line);
    border-radius: 6px;
    padding: 25px;
    min-height: 100%;
    box-shadow: 0 10px 28px rgba(0,0,0,.13);
}

.info-card h3 {
    color: var(--champagne-light);
    font-family: 'Playfair Display', Georgia, serif;
    font-weight: 500;
    margin-bottom: 12px;
}

.info-card p { color: #d0ccc3; line-height: 1.7; }

.gold-line {
    width: 54px;
    height: 1px;
    background: var(--champagne);
    margin: 17px auto 21px;
}

.footer {
    text-align: center;
    padding: 38px 10px 20px;
    margin-top: 58px;
    border-top: 1px solid var(--line);
    color: var(--muted);
    font-size: 13px;
    letter-spacing: .025em;
}

.footer strong {
    color: var(--champagne-light);
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 18px;
    font-weight: 500;
    letter-spacing: .08em;
}

.brand-logo {
    max-height: 90px;
    object-fit: contain;
    margin-bottom: 15px;
}

.small-text { color: var(--muted); font-size: 12px; }

div[data-testid="stAlert"] { border-radius: 6px; }

[data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] {
    gap: 1.1rem;
}

@media (max-width: 768px) {
    .block-container {
        padding: .65rem .85rem 2.5rem;
    }

    .hero {
        min-height: 500px;
        padding: 35px 20px;
        margin: 4px 0 22px;
        background-position: center;
    }

    .hero-logo {
        max-width: 88px;
        max-height: 78px;
        margin-bottom: 20px;
    }

    .hero-label {
        font-size: 9px;
        letter-spacing: .24em;
    }

    .hero h1 {
        font-size: clamp(29px, 9vw, 43px);
        letter-spacing: .035em;
    }

    .hero p {
        font-size: 14px;
        line-height: 1.65;
    }

    .section-title {
        margin: 38px 0 22px;
    }

    .section-title h2 {
        font-size: 25px;
        letter-spacing: .04em;
    }

    .info-card {
        padding: 19px;
        margin-bottom: 12px;
    }

    div[data-testid="stForm"] {
        padding: 16px 13px;
    }

    div[data-testid="stMetric"] {
        padding: 12px;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.35rem;
    }

    .stButton > button, .stLinkButton > a,
    div[data-testid="stFormSubmitButton"] button {
        min-height: 47px;
        font-size: 12px;
        letter-spacing: .045em;
    }

    div[data-testid="stTabs"] button {
        font-size: 12px;
        padding: 8px 9px;
    }

    .footer { margin-top: 38px; }
}

@media (max-width: 420px) {
    .block-container { padding-left: .65rem; padding-right: .65rem; }
    .hero { min-height: 455px; }
    .hero h1 { font-size: 29px; }
    .info-card { padding: 16px; }
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
# SEGURIDAD: PIN DEL PROPIETARIO
# ============================================================

def crear_hash_pin(pin, salt=None):
    """Genera un hash PBKDF2 del PIN con una sal aleatoria."""
    if salt is None:
        salt = secrets.token_bytes(16)

    pin_hash = hashlib.pbkdf2_hmac(
        "sha256",
        pin.encode("utf-8"),
        salt,
        600_000
    )

    return salt.hex(), pin_hash.hex()


def obtener_credencial_pin():
    filas = consultar("""
        SELECT salt, pin_hash
        FROM public.seguridad
        WHERE id = 1
    """)

    if not filas:
        return None

    return filas[0]


def verificar_pin(pin):
    credencial = obtener_credencial_pin()

    if not credencial:
        return False

    try:
        salt = bytes.fromhex(credencial["salt"])
        hash_guardado = bytes.fromhex(credencial["pin_hash"])

        hash_introducido = hashlib.pbkdf2_hmac(
            "sha256",
            pin.encode("utf-8"),
            salt,
            600_000
        )

        return hmac.compare_digest(hash_introducido, hash_guardado)

    except (ValueError, TypeError, KeyError):
        return False


def guardar_nuevo_pin(pin):
    salt_hex, hash_hex = crear_hash_pin(pin)

    ejecutar("""
        INSERT INTO public.seguridad (id, salt, pin_hash, actualizado)
        VALUES (1, %s, %s, NOW())
        ON CONFLICT (id)
        DO UPDATE SET
            salt = EXCLUDED.salt,
            pin_hash = EXCLUDED.pin_hash,
            actualizado = NOW()
    """, (salt_hex, hash_hex))


# ============================================================
# INICIALIZACIÓN DE TABLAS
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

            # Esta tabla guarda el hash del PIN, nunca el PIN en texto plano.
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS public.seguridad (
                    id SMALLINT PRIMARY KEY CHECK (id = 1),
                    salt VARCHAR(64) NOT NULL,
                    pin_hash VARCHAR(128) NOT NULL,
                    actualizado TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)

            cursor.execute("""
                INSERT INTO public.servicios
                    (nombre, precio, activo)
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
                "descripcion": "Cuidamos cada detalle para que salgas con tu mejor imagen.",
                "direccion": "",
                "telefono": "",
                "whatsapp": "",
                "horario": "Lunes a viernes: 09:00 - 14:00 y 16:00 - 20:00",
                "logo": "",
                "foto_portada": "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=1800&q=85",
                "galeria": "",
                "sobre_nosotros": "Somos una peluquería dedicada al cuidado de tu imagen. Nuestro objetivo es ofrecerte un servicio profesional y personalizado."
            }

            for clave, valor in valores_iniciales.items():
                cursor.execute("""
                    INSERT INTO public.configuracion_web (clave, valor)
                    VALUES (%s, %s)
                    ON CONFLICT (clave) DO NOTHING;
                """, (clave, valor))

            # Solo se establece el PIN inicial si todavía no existe.
            # Si OWNER_PIN está definido en Streamlit Secrets se utiliza ese valor.
            pin_inicial = str(st.secrets.get("OWNER_PIN", "1234")).strip()
            cursor.execute("""
                SELECT id
                FROM public.seguridad
                WHERE id = 1
            """)
            existe_pin = cursor.fetchone()

            if not existe_pin:
                salt = secrets.token_bytes(16)
                pin_hash = hashlib.pbkdf2_hmac(
                    "sha256",
                    pin_inicial.encode("utf-8"),
                    salt,
                    600_000
                )

                cursor.execute("""
                    INSERT INTO public.seguridad
                        (id, salt, pin_hash, actualizado)
                    VALUES (1, %s, %s, NOW())
                    ON CONFLICT (id) DO NOTHING
                """, (salt.hex(), pin_hash.hex()))

        conexion.commit()

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()


# ============================================================
# CONFIGURACIÓN DE LA PELUQUERÍA
# ============================================================

def obtener_configuracion():

    filas = consultar("""
        SELECT clave, valor
        FROM public.configuracion_web
    """)

    configuracion = {}

    for fila in filas:
        configuracion[fila["clave"]] = fila["valor"] or ""

    return configuracion


def guardar_configuracion(clave, valor):

    ejecutar("""
        INSERT INTO public.configuracion_web (clave, valor)
        VALUES (%s, %s)
        ON CONFLICT (clave)
        DO UPDATE SET valor = EXCLUDED.valor
    """, (clave, str(valor)))


# ============================================================
# SERVICIOS
# ============================================================

def obtener_servicios(activos=False):

    if activos:
        return consultar("""
            SELECT id, nombre, precio, activo
            FROM public.servicios
            WHERE activo = TRUE
            ORDER BY nombre
        """)

    return consultar("""
        SELECT id, nombre, precio, activo
        FROM public.servicios
        ORDER BY nombre
    """)


# ============================================================
# PRODUCTOS
# ============================================================

def obtener_productos(activos=False):

    if activos:
        return consultar("""
            SELECT id, nombre, precio, activo
            FROM public.productos
            WHERE activo = TRUE
            ORDER BY nombre
        """)

    return consultar("""
        SELECT id, nombre, precio, activo
        FROM public.productos
        ORDER BY nombre
    """)


# ============================================================
# HORARIOS DE RESERVA
# ============================================================

def generar_horarios():

    horarios = []

    # Mañana: 09:00 a 14:00
    for minutos in range(9 * 60, 14 * 60, 30):
        hora = time(minutos // 60, minutos % 60)
        horarios.append(hora.strftime("%H:%M"))

    # Tarde: 16:00 a 20:00
    for minutos in range(16 * 60, 20 * 60, 30):
        hora = time(minutos // 60, minutos % 60)
        horarios.append(hora.strftime("%H:%M"))

    return horarios


def hora_texto(valor):
    if hasattr(valor, "strftime"):
        return valor.strftime("%H:%M")
    return str(valor)[:5]


def obtener_horas_ocupadas(fecha_seleccionada):

    filas = consultar("""
        SELECT hora
        FROM public.citas
        WHERE fecha = %s
    """, (fecha_seleccionada,))

    return [hora_texto(fila["hora"]) for fila in filas]


def horarios_disponibles(fecha_seleccionada):

    todos = generar_horarios()
    ocupados = obtener_horas_ocupadas(fecha_seleccionada)

    disponibles = [
        hora for hora in todos
        if hora not in ocupados
    ]

    if fecha_seleccionada == date.today():
        hora_actual = datetime.now().strftime("%H:%M")

        disponibles = [
            hora for hora in disponibles
            if hora > hora_actual
        ]

    return disponibles


# ============================================================
# SESIÓN
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
# ENCABEZADO Y NAVEGACIÓN
# ============================================================

def mostrar_encabezado(config):

    logo = config.get("logo", "").strip()
    nombre = config.get("nombre", "PELUQUERÍA")

    c1, c2 = st.columns([1, 3])

    with c1:
        if logo:
            try:
                st.image(logo, width=150)
            except Exception:
                st.markdown(f"## ✂️ {escape(nombre)}")
        else:
            st.markdown(f"## ✂️ {escape(nombre)}")

    with c2:
        st.markdown(
            f"<div style='text-align:right;padding-top:18px;color:#d6ad60;font-weight:700;letter-spacing:2px;'>"
            f"{escape(nombre.upper())}</div>",
            unsafe_allow_html=True
        )

    st.markdown("<hr>", unsafe_allow_html=True)

    columnas = st.columns(6, gap="small", wrap=False)

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
            if st.button(
                texto,
                key=f"nav_{pagina}",
                use_container_width=True
            ):
                ir_a(pagina)


# ============================================================
# PIE DE PÁGINA
# ============================================================

def mostrar_footer(config):

    nombre = escape(config.get("nombre", "PELUQUERÍA"))

    st.markdown(f"""
    <div class="footer">
        <strong>{nombre}</strong><br><br>
        Peluquería · Barbería<br>
        <span class="small-text">
        © {datetime.now().year} Todos los derechos reservados
        </span>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# PÁGINA DE INICIO
# ============================================================

def pagina_inicio(config):

    nombre = escape(config.get("nombre", "PELUQUERÍA"))
    eslogan = escape(config.get("eslogan", "TU ESTILO, NUESTRA PASIÓN"))
    descripcion = escape(config.get("descripcion", "Cuidamos cada detalle para ti."))

    foto = config.get("foto_portada", "").strip()
    logo = config.get("logo", "").strip()

    if not foto:
        foto = "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=1800&q=85"

    logo_html = (
        f"<img class='hero-logo' src='{escape(logo, quote=True)}' alt='Logotipo de {nombre}'>"
        if logo else ""
    )

    st.markdown(f"""
    <div class="hero" style="background-image:url('{escape(foto, quote=True)}');">
        <div class="hero-content">
            {logo_html}
            <div class="hero-label">{nombre}</div>
            <h1>{eslogan}</h1>
            <div class="gold-line"></div>
            <p>{descripcion}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    centro = st.columns([1, 2, 1])

    with centro[1]:
        if st.button(
            "📅  RESERVAR MI CITA",
            use_container_width=True,
            key="inicio_reservar"
        ):
            ir_a("Reservar")

    st.markdown("""
    <div class="section-title">
        <h2>BIENVENIDO</h2>
        <div class="gold-line"></div>
        <p>Profesionalidad, estilo y atención personalizada.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="info-card">
            <h3>✂️ Estilo</h3>
            <p>Trabajamos cada corte cuidando los detalles y adaptándonos a tu personalidad.</p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="info-card">
            <h3>⭐ Profesionalidad</h3>
            <p>Atención cercana y un servicio pensado para que disfrutes de tu visita.</p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="info-card">
            <h3>📅 Reserva online</h3>
            <p>Elige tu servicio, selecciona el día y reserva tu cita cómodamente.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="section-title">
        <h2>NUESTROS SERVICIOS</h2>
        <div class="gold-line"></div>
        <p>Descubre nuestros cortes y tratamientos.</p>
    </div>
    """, unsafe_allow_html=True)

    servicios = obtener_servicios(activos=True)

    if servicios:
        columnas = st.columns(min(3, len(servicios)))

        for i, servicio in enumerate(servicios):
            with columnas[i % len(columnas)]:
                st.markdown(f"""
                <div class="info-card">
                    <h3>{escape(servicio['nombre'])}</h3>
                    <h2>{euros(servicio['precio'])}</h2>
                </div>
                """, unsafe_allow_html=True)

    else:
        st.info("Próximamente publicaremos nuestros servicios.")

    centro = st.columns([1, 2, 1])

    with centro[1]:
        if st.button(
            "VER TODOS LOS SERVICIOS",
            use_container_width=True,
            key="inicio_servicios"
        ):
            ir_a("Servicios")


# ============================================================
# PÁGINA DE SERVICIOS
# ============================================================

def pagina_servicios():

    st.markdown("""
    <div class="section-title">
        <h2>NUESTROS SERVICIOS Y TARIFAS</h2>
        <div class="gold-line"></div>
        <p>Elige el servicio que mejor se adapta a ti.</p>
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
                <p class="small-text">Servicio disponible bajo reserva.</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    if st.button("📅 RESERVAR CITA", use_container_width=True):
        ir_a("Reservar")


# ============================================================
# PÁGINA DE RESERVAS
# ============================================================

def pagina_reservar():

    st.markdown("""
    <div class="section-title">
        <h2>RESERVA TU CITA</h2>
        <div class="gold-line"></div>
        <p>Reserva tu próximo corte de forma rápida y sencilla.</p>
    </div>
    """, unsafe_allow_html=True)

    servicios = obtener_servicios(activos=True)

    if not servicios:
        st.warning("No hay servicios disponibles para reservar.")
        return

    nombres = [s["nombre"] for s in servicios]

    # IMPORTANTE:
    # Los campos ya no están dentro de st.form(). Así Streamlit
    # actualiza la página al cambiar la fecha y consulta al momento
    # los horarios disponibles para ese día.

    cliente = st.text_input(
        "Nombre y apellidos",
        placeholder="Escribe tu nombre",
        key="reserva_cliente"
    )

    telefono = st.text_input(
        "Teléfono",
        placeholder="Tu número de teléfono",
        key="reserva_telefono"
    )

    servicio_nombre = st.selectbox(
        "Selecciona tu servicio",
        nombres,
        key="reserva_servicio"
    )

    servicio_elegido = next(
        s for s in servicios
        if s["nombre"] == servicio_nombre
    )

    st.markdown(
        f"<h3 style='text-align:center;'>Precio: {euros(servicio_elegido['precio'])}</h3>",
        unsafe_allow_html=True
    )

    fecha_seleccionada = st.date_input(
        "Selecciona el día",
        min_value=date.today(),
        value=date.today(),
        key="reserva_fecha"
    )

    # La consulta se vuelve a ejecutar automáticamente al cambiar la fecha.
    disponibles = horarios_disponibles(fecha_seleccionada)

    if disponibles:
        # La clave incluye la fecha para que, al cambiar de día,
        # no se conserve por error la hora elegida para otra fecha.
        hora_seleccionada = st.selectbox(
            "Selecciona la hora",
            disponibles,
            index=None,
            placeholder="Elige una hora disponible",
            key=f"reserva_hora_{fecha_seleccionada.isoformat()}"
        )
    else:
        hora_seleccionada = None
        st.warning("No quedan horas disponibles para este día.")

    aceptar = st.checkbox(
        "He leído y acepto la política de privacidad.",
        key="reserva_aceptar_privacidad"
    )

    enviar = st.button(
        "CONFIRMAR MI RESERVA",
        use_container_width=True,
        key="confirmar_reserva"
    )

    if enviar:

        if not cliente.strip():
            st.error("Introduce tu nombre.")

        elif not telefono.strip():
            st.error("Introduce tu teléfono.")

        elif not aceptar:
            st.error("Debes aceptar la política de privacidad.")

        elif not hora_seleccionada:
            st.error("Selecciona una hora disponible para reservar.")

        else:

            # Comprobamos de nuevo que la hora sigue libre.
            ocupadas = obtener_horas_ocupadas(fecha_seleccionada)

            if hora_seleccionada in ocupadas:
                st.error("Lo sentimos, esa hora acaba de ser reservada. Selecciona otra.")

            else:

                try:

                    ejecutar("""
                        INSERT INTO public.citas
                        (cliente, telefono, servicio, precio, fecha, hora, pagada)
                        VALUES (%s, %s, %s, %s, %s, %s, FALSE)
                    """, (
                        cliente.strip(),
                        telefono.strip(),
                        servicio_elegido["nombre"],
                        servicio_elegido["precio"],
                        fecha_seleccionada,
                        hora_seleccionada
                    ))

                    st.success("¡Tu cita se ha reservado correctamente!")

                    st.markdown(f"""
                    <div class="info-card">
                        <h2 style="text-align:center;">¡RESERVA CONFIRMADA!</h2>
                        <div class="gold-line"></div>
                        <p><strong>Cliente:</strong> {escape(cliente)}</p>
                        <p><strong>Servicio:</strong> {escape(servicio_elegido['nombre'])}</p>
                        <p><strong>Fecha:</strong> {fecha_seleccionada.strftime('%d/%m/%Y')}</p>
                        <p><strong>Hora:</strong> {escape(hora_seleccionada)}</p>
                        <h2 style="text-align:center;">{euros(servicio_elegido['precio'])}</h2>
                    </div>
                    """, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"No se ha podido guardar la reserva: {e}")


# ============================================================
# PÁGINA DE GALERÍA
# ============================================================

def pagina_galeria(config):

    st.markdown("""
    <div class="section-title">
        <h2>NUESTRA GALERÍA</h2>
        <div class="gold-line"></div>
        <p>Conoce nuestro espacio y algunos de nuestros trabajos.</p>
    </div>
    """, unsafe_allow_html=True)

    galeria = config.get("galeria", "").strip()

    if galeria:

        imagenes = [
            url.strip()
            for url in galeria.splitlines()
            if url.strip().startswith(("http://", "https://"))
        ]

        if imagenes:

            columnas = st.columns(2)

            for i, imagen in enumerate(imagenes):
                with columnas[i % 2]:
                    st.image(imagen, use_container_width=True)

        else:
            st.info("Todavía no hay fotografías publicadas.")

    else:

        st.markdown("""
        <p style="text-align:center;color:#aaaaaa;">
        Próximamente publicaremos fotografías de nuestros trabajos.
        </p>
        """, unsafe_allow_html=True)

        st.image(
            "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=1400&q=85",
            use_container_width=True
        )


# ============================================================
# PÁGINA DE CONTACTO
# ============================================================

def pagina_contacto(config):

    st.markdown("""
    <div class="section-title">
        <h2>CONTACTO</h2>
        <div class="gold-line"></div>
        <p>Estamos aquí para atenderte.</p>
    </div>
    """, unsafe_allow_html=True)

    direccion = config.get("direccion", "").strip()
    telefono = config.get("telefono", "").strip()
    whatsapp = config.get("whatsapp", "").strip()
    horario = config.get("horario", "").strip()

    c1, c2 = st.columns(2)

    with c1:

        st.markdown("""
        <div class="info-card">
            <h3>📍 Nuestra ubicación</h3>
        """, unsafe_allow_html=True)

        st.write(direccion if direccion else "Dirección pendiente de configurar.")

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div class="info-card">
            <h3>🕒 Horarios</h3>
        """, unsafe_allow_html=True)

        st.write(horario if horario else "Horario pendiente de configurar.")

        st.markdown("</div>", unsafe_allow_html=True)

    with c2:

        st.markdown("""
        <div class="info-card">
            <h3>📞 Teléfono</h3>
        """, unsafe_allow_html=True)

        st.write(telefono if telefono else "Teléfono pendiente de configurar.")

        st.markdown("</div>", unsafe_allow_html=True)

        if whatsapp:

            numero = re.sub(r"\D", "", whatsapp)

            if numero:

                st.markdown("<br>", unsafe_allow_html=True)

                st.link_button(
                    "💬 CONTACTAR POR WHATSAPP",
                    f"https://wa.me/{numero}",
                    use_container_width=True
                )

    st.markdown("---")

    if st.button("📅 RESERVAR CITA", use_container_width=True):
        ir_a("Reservar")


# ============================================================
# PANEL DE PROPIETARIO
# ============================================================

def panel_cambiar_pin():

    st.markdown("---")

    with st.expander("🔐 CAMBIAR PIN DE ACCESO", expanded=False):

        st.write(
            "Cambia el PIN que utilizas para entrar al panel de propietario. "
            "El PIN se almacena en la base de datos mediante un hash seguro."
        )

        with st.form("form_cambiar_pin"):

            pin_actual = st.text_input(
                "PIN actual",
                type="password",
                key="pin_actual_cambio"
            )

            pin_nuevo = st.text_input(
                "Nuevo PIN (entre 4 y 12 cifras)",
                type="password",
                key="pin_nuevo_cambio"
            )

            confirmar_pin = st.text_input(
                "Confirma el nuevo PIN",
                type="password",
                key="confirmar_pin_cambio"
            )

            cambiar = st.form_submit_button(
                "GUARDAR NUEVO PIN",
                use_container_width=True
            )

        if cambiar:

            if not verificar_pin(pin_actual):
                st.error("El PIN actual no es correcto.")

            elif not pin_nuevo.isdigit() or not (4 <= len(pin_nuevo) <= 12):
                st.error("El nuevo PIN debe contener entre 4 y 12 cifras.")

            elif pin_nuevo != confirmar_pin:
                st.error("La confirmación no coincide con el nuevo PIN.")

            elif pin_nuevo == pin_actual:
                st.error("El nuevo PIN debe ser diferente del actual.")

            else:
                try:
                    guardar_nuevo_pin(pin_nuevo)
                    st.session_state.admin_autenticado = False
                    st.session_state.mensaje_pin = (
                        "PIN cambiado correctamente. Vuelve a entrar con tu nuevo PIN."
                    )
                    st.rerun()

                except Exception:
                    st.error("No se ha podido actualizar el PIN. Inténtalo de nuevo.")


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

            pin = st.text_input(
                "PIN de acceso",
                type="password"
            )

            entrar = st.form_submit_button(
                "ENTRAR AL PANEL",
                use_container_width=True
            )

        if entrar:

            if verificar_pin(pin):
                st.session_state.admin_autenticado = True
                st.rerun()
            else:
                st.error("PIN incorrecto.")

        return

    st.markdown("""
    <div class="section-title">
        <h2>PANEL DE ADMINISTRACIÓN</h2>
        <div class="gold-line"></div>
        <p>Gestiona tu peluquería desde un único lugar.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("CERRAR SESIÓN", key="cerrar_admin"):
        st.session_state.admin_autenticado = False
        st.rerun()

    pestañas = st.tabs([
        "📅 Citas",
        "💰 Caja",
        "✂️ Servicios",
        "🧴 Productos",
        "🌐 Web"
    ])

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


# ============================================================
# PANEL DE CITAS
# ============================================================

def panel_citas():

    st.subheader("Gestión de citas")

    fecha_consulta = st.date_input(
        "Selecciona el día",
        value=date.today(),
        key="fecha_citas_admin"
    )

    citas = consultar("""
        SELECT id, cliente, telefono, servicio, precio,
               fecha, hora, pagada
        FROM public.citas
        WHERE fecha = %s
        ORDER BY hora
    """, (fecha_consulta,))

    total_citas = len(citas)

    total_cobrado = sum(
        (Decimal(str(c["precio"])) for c in citas if c["pagada"]),
        Decimal("0")
    )

    pendiente = sum(
        (Decimal(str(c["precio"])) for c in citas if not c["pagada"]),
        Decimal("0")
    )

    c1, c2, c3 = st.columns(3)

    c1.metric("Citas del día", total_citas)
    c2.metric("Cobrado", euros(total_cobrado))
    c3.metric("Pendiente", euros(pendiente))

    st.markdown("---")

    if not citas:
        st.info("No hay citas para este día.")
        return

    for cita in citas:

        hora = hora_texto(cita["hora"])

        with st.container(border=True):

            c1, c2, c3 = st.columns([2, 2, 1])

            with c1:
                st.markdown(f"### {hora}")
                st.write(f"**Cliente:** {cita['cliente']}")
                st.write(f"**Teléfono:** {cita['telefono']}")

            with c2:
                st.write(f"**Servicio:** {cita['servicio']}")
                st.write(f"**Precio:** {euros(cita['precio'])}")

                if cita["pagada"]:
                    st.success("PAGADA")
                else:
                    st.warning("PENDIENTE DE COBRO")

            with c3:

                if not cita["pagada"]:

                    if st.button(
                        "COBRAR",
                        key=f"cobrar_cita_{cita['id']}",
                        use_container_width=True
                    ):

                        ejecutar("""
                            UPDATE public.citas
                            SET pagada = TRUE
                            WHERE id = %s
                        """, (cita["id"],))

                        st.success("Cita cobrada.")
                        st.rerun()


# ============================================================
# PANEL DE CAJA
# ============================================================

def panel_caja():

    st.subheader("Caja y facturación")

    hoy = date.today()

    citas_hoy = consultar("""
        SELECT precio, pagada
        FROM public.citas
        WHERE fecha = %s
    """, (hoy,))

    cobrado_hoy = sum(
        (Decimal(str(c["precio"])) for c in citas_hoy if c["pagada"]),
        Decimal("0")
    )

    pendiente_hoy = sum(
        (Decimal(str(c["precio"])) for c in citas_hoy if not c["pagada"]),
        Decimal("0")
    )

    c1, c2, c3 = st.columns(3)

    c1.metric("Facturación cobrada hoy", euros(cobrado_hoy))
    c2.metric("Pendiente hoy", euros(pendiente_hoy))
    c3.metric("Citas hoy", len(citas_hoy))

    st.markdown("---")

    st.markdown("### Resumen mensual")

    mes = st.selectbox(
        "Mes",
        list(range(1, 13)),
        index=hoy.month - 1,
        format_func=lambda x: [
            "Enero", "Febrero", "Marzo", "Abril",
            "Mayo", "Junio", "Julio", "Agosto",
            "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ][x - 1]
    )

    anio = st.number_input(
        "Año",
        min_value=2024,
        max_value=2100,
        value=hoy.year,
        step=1
    )

    primer_dia = date(int(anio), mes, 1)

    if mes == 12:
        primer_dia_siguiente = date(int(anio) + 1, 1, 1)
    else:
        primer_dia_siguiente = date(int(anio), mes + 1, 1)

    citas_mes = consultar("""
        SELECT id, cliente, telefono, servicio, precio,
               fecha, hora, pagada
        FROM public.citas
        WHERE fecha >= %s AND fecha < %s
        ORDER BY fecha DESC, hora DESC
    """, (primer_dia, primer_dia_siguiente))

    cobrado_mes = sum(
        (Decimal(str(c["precio"])) for c in citas_mes if c["pagada"]),
        Decimal("0")
    )

    pendiente_mes = sum(
        (Decimal(str(c["precio"])) for c in citas_mes if not c["pagada"]),
        Decimal("0")
    )

    c1, c2, c3 = st.columns(3)

    c1.metric("Cobrado del mes", euros(cobrado_mes))
    c2.metric("Pendiente del mes", euros(pendiente_mes))
    c3.metric("Número de citas", len(citas_mes))

    st.markdown("---")

    st.markdown("### Histórico de citas")

    if not citas_mes:
        st.info("No hay movimientos en este mes.")
        return

    for cita in citas_mes:

        with st.container(border=True):

            c1, c2, c3 = st.columns([2, 2, 1])

            with c1:
                st.write(f"**{cita['cliente']}**")
                st.write(cita["fecha"].strftime("%d/%m/%Y"))
                st.write(hora_texto(cita["hora"]))

            with c2:
                st.write(cita["servicio"])
                st.write(euros(cita["precio"]))

            with c3:

                if cita["pagada"]:
                    st.success("PAGADA")
                else:
                    st.warning("PENDIENTE")

                    if st.button(
                        "COBRAR",
                        key=f"cobrar_historico_{cita['id']}"
                    ):

                        ejecutar("""
                            UPDATE public.citas
                            SET pagada = TRUE
                            WHERE id = %s
                        """, (cita["id"],))

                        st.rerun()


# ============================================================
# PANEL DE SERVICIOS
# ============================================================

def panel_servicios():

    st.subheader("Administrar servicios y cortes")

    st.write(
        "Los servicios activos aparecerán automáticamente "
        "en la página pública de reservas."
    )

    with st.expander("➕ Añadir nuevo servicio", expanded=False):

        with st.form("nuevo_servicio"):

            nombre = st.text_input("Nombre del servicio")

            precio = st.number_input(
                "Precio (€)",
                min_value=0.0,
                value=12.0,
                step=0.5
            )

            crear = st.form_submit_button(
                "GUARDAR SERVICIO",
                use_container_width=True
            )

        if crear:

            if not nombre.strip():
                st.error("Escribe el nombre del servicio.")

            else:

                try:

                    ejecutar("""
                        INSERT INTO public.servicios
                        (nombre, precio, activo)
                        VALUES (%s, %s, TRUE)
                    """, (nombre.strip(), precio))

                    st.success("Servicio añadido correctamente.")
                    st.rerun()

                except psycopg2.IntegrityError:
                    st.error("Ya existe un servicio con ese nombre.")

    servicios = obtener_servicios()

    st.markdown("---")
    st.markdown("### Servicios existentes")

    if not servicios:
        st.info("Todavía no has creado servicios.")
        return

    opciones = {
        f"{s['nombre']} — {euros(s['precio'])}": s["id"]
        for s in servicios
    }

    seleccion = st.selectbox(
        "Selecciona un servicio para modificarlo",
        list(opciones.keys()),
        key="editar_servicio_select"
    )

    servicio = next(
        s for s in servicios
        if s["id"] == opciones[seleccion]
    )

    with st.form("editar_servicio"):

        nombre_nuevo = st.text_input(
            "Nombre",
            value=servicio["nombre"]
        )

        precio_nuevo = st.number_input(
            "Precio (€)",
            min_value=0.0,
            value=float(servicio["precio"]),
            step=0.5
        )

        activo_nuevo = st.checkbox(
            "Servicio visible para los clientes",
            value=servicio["activo"]
        )

        guardar = st.form_submit_button(
            "GUARDAR CAMBIOS",
            use_container_width=True
        )

    if guardar:

        try:

            ejecutar("""
                UPDATE public.servicios
                SET nombre = %s,
                    precio = %s,
                    activo = %s
                WHERE id = %s
            """, (
                nombre_nuevo.strip(),
                precio_nuevo,
                activo_nuevo,
                servicio["id"]
            ))

            st.success("Servicio actualizado.")
            st.rerun()

        except psycopg2.IntegrityError:
            st.error("Ya existe un servicio con ese nombre.")

    st.markdown("---")

    if servicio["activo"]:
        st.success("Este servicio está publicado.")
    else:
        st.warning("Este servicio está desactivado y no aparece en las reservas.")

    if st.button(
        "🗑️ ELIMINAR SERVICIO",
        key="eliminar_servicio"
    ):

        ejecutar("""
            DELETE FROM public.servicios
            WHERE id = %s
        """, (servicio["id"],))

        st.success("Servicio eliminado.")
        st.rerun()


# ============================================================
# PANEL DE PRODUCTOS
# ============================================================

def panel_productos():

    st.subheader("Gestión de productos")

    with st.expander("➕ Añadir producto", expanded=False):

        with st.form("nuevo_producto"):

            nombre = st.text_input("Nombre del producto")

            precio = st.number_input(
                "Precio (€)",
                min_value=0.0,
                value=10.0,
                step=0.5
            )

            crear = st.form_submit_button(
                "AÑADIR PRODUCTO",
                use_container_width=True
            )

        if crear:

            if not nombre.strip():
                st.error("Introduce el nombre del producto.")

            else:

                ejecutar("""
                    INSERT INTO public.productos
                    (nombre, precio, activo)
                    VALUES (%s, %s, TRUE)
                """, (nombre.strip(), precio))

                st.success("Producto añadido.")
                st.rerun()

    productos = obtener_productos()

    st.markdown("---")
    st.markdown("### Productos registrados")

    if not productos:
        st.info("No hay productos registrados.")
        return

    opciones = {
        f"{p['nombre']} — {euros(p['precio'])}": p["id"]
        for p in productos
    }

    seleccion = st.selectbox(
        "Selecciona un producto",
        list(opciones.keys()),
        key="editar_producto_select"
    )

    producto = next(
        p for p in productos
        if p["id"] == opciones[seleccion]
    )

    with st.form("editar_producto"):

        nombre_nuevo = st.text_input(
            "Nombre del producto",
            value=producto["nombre"]
        )

        precio_nuevo = st.number_input(
            "Precio (€)",
            min_value=0.0,
            value=float(producto["precio"]),
            step=0.5
        )

        activo_nuevo = st.checkbox(
            "Producto activo",
            value=producto["activo"]
        )

        guardar = st.form_submit_button(
            "GUARDAR CAMBIOS",
            use_container_width=True
        )

    if guardar:

        ejecutar("""
            UPDATE public.productos
            SET nombre = %s,
                precio = %s,
                activo = %s
            WHERE id = %s
        """, (
            nombre_nuevo.strip(),
            precio_nuevo,
            activo_nuevo,
            producto["id"]
        ))

        st.success("Producto actualizado.")
        st.rerun()

    if st.button(
        "🗑️ ELIMINAR PRODUCTO",
        key="eliminar_producto"
    ):

        ejecutar("""
            DELETE FROM public.productos
            WHERE id = %s
        """, (producto["id"],))

        st.success("Producto eliminado.")
        st.rerun()


# ============================================================
# PANEL DE CONFIGURACIÓN DE LA WEB
# ============================================================

def panel_web():

    st.subheader("Personaliza la página pública")

    st.write(
        "Desde aquí puedes cambiar la presentación de la peluquería "
        "sin tener que modificar el código."
    )

    config = obtener_configuracion()

    with st.form("form_configuracion_web"):

        nombre = st.text_input(
            "Nombre de la peluquería",
            value=config.get("nombre", "")
        )

        eslogan = st.text_input(
            "Eslogan principal",
            value=config.get("eslogan", "")
        )

        descripcion = st.text_area(
            "Texto de presentación de la portada",
            value=config.get("descripcion", "")
        )

        sobre_nosotros = st.text_area(
            "Sobre nosotros",
            value=config.get("sobre_nosotros", "")
        )

        st.markdown("### Identidad visual")

        logo = st.text_input(
            "URL del logotipo",
            value=config.get("logo", ""),
            help="Pega aquí el enlace público de tu logotipo."
        )

        foto_portada = st.text_input(
            "URL de la fotografía principal",
            value=config.get("foto_portada", "")
        )

        galeria = st.text_area(
            "Fotografías de la galería",
            value=config.get("galeria", ""),
            help="Introduce una URL de imagen por línea."
        )

        st.markdown("### Datos de contacto")

        direccion = st.text_input(
            "Dirección",
            value=config.get("direccion", "")
        )

        telefono = st.text_input(
            "Teléfono",
            value=config.get("telefono", "")
        )

        whatsapp = st.text_input(
            "WhatsApp con prefijo internacional",
            value=config.get("whatsapp", ""),
            help="Ejemplo: 34600111222"
        )

        horario = st.text_area(
            "Horario comercial",
            value=config.get("horario", "")
        )

        guardar = st.form_submit_button(
            "GUARDAR CONFIGURACIÓN DE LA WEB",
            use_container_width=True
        )

    if guardar:

        valores = {
            "nombre": nombre,
            "eslogan": eslogan,
            "descripcion": descripcion,
            "sobre_nosotros": sobre_nosotros,
            "logo": logo,
            "foto_portada": foto_portada,
            "galeria": galeria,
            "direccion": direccion,
            "telefono": telefono,
            "whatsapp": whatsapp,
            "horario": horario
        }

        for clave, valor in valores.items():
            guardar_configuracion(clave, valor)

        st.success("Configuración guardada correctamente.")
        st.rerun()

    st.markdown("---")
    st.markdown("### Vista previa del logotipo")

    if config.get("logo", "").strip():
        st.image(config["logo"], width=180)
    else:
        st.info("Todavía no has configurado un logotipo.")


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

    st.error("No se ha podido cargar la aplicación.")
    st.error(str(error))

    st.info(
        "Comprueba la conexión con Supabase y las variables "
        "de configuración de la aplicación."
    )
