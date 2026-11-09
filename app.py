
import streamlit as st
import psycopg2
from contextlib import contextmanager
from datetime import date

# ==========================================
# CONFIGURACION
# ==========================================

st.set_page_config(
    page_title="Peluquería Premium",
    page_icon="💈",
    layout="centered"
)

PIN = st.secrets["OWNER_PIN"]

SERVICIOS = {
    "Corte de caballero": 12.00,
    "Corte infantil": 9.00,
    "Arreglo de barba": 7.00,
    "Corte + barba": 17.00
}

HORAS = [
    "09:00", "09:30", "10:00", "10:30",
    "11:00", "11:30", "12:00", "12:30",
    "16:00", "16:30", "17:00", "17:30",
    "18:00", "18:30", "19:00", "19:30"
]


# ==========================================
# CONEXION SUPABASE
# ==========================================

@contextmanager
def conectar():
    con = psycopg2.connect(
        host=st.secrets["DB_HOST"],
        port=st.secrets["DB_PORT"],
        database=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        sslmode="require"
    )

    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


# ==========================================
# DISEÑO NEGRO Y DORADO
# ==========================================

st.markdown("""
<style>

/* FONDO GENERAL */

.stApp {
    background:
        radial-gradient(
            ellipse at top,
            #29251c 0%,
            #151515 48%,
            #090909 100%
        );
    color: #f5f0e6;
}

/* ANCHO Y ESPACIADO */

.main .block-container {
    max-width: 850px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* TITULOS */

h1, h2, h3 {
    color: #d6b46a !important;
    font-family: Georgia, serif;
    letter-spacing: 0.5px;
}

p, label, span {
    color: #eee8dc;
}

/* CABECERA */

.premium-header {
    text-align: center;
    padding: 30px 15px;
    margin-bottom: 28px;
    background: linear-gradient(
        135deg,
        #29251e,
        #111111
    );
    border: 1px solid #a8894b;
    border-radius: 18px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.35);
}

.premium-icon {
    font-size: 48px;
}

.premium-title {
    color: #dfbd75;
    font-family: Georgia, serif;
    font-size: 35px;
    font-weight: bold;
    letter-spacing: 4px;
    margin: 8px 0;
}

.premium-subtitle {
    color: #c6a96c;
    font-size: 11px;
    letter-spacing: 4px;
}

/* FORMULARIOS Y TARJETAS */

[data-testid="stForm"],
[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(35, 35, 35, 0.85);
    border: 1px solid #806b3c;
    border-radius: 15px;
    padding: 12px;
}

/* CAMPOS DE TEXTO */

[data-testid="stTextInput"] input {
    background-color: #202020;
    color: white;
    border: 1px solid #806b3c;
    border-radius: 9px;
}

/* SELECTORES */

[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background-color: #202020;
    border-color: #806b3c;
    color: white;
}

/* FECHAS */

[data-testid="stDateInput"] input {
    background-color: #202020;
    color: white;
    border: 1px solid #806b3c;
}

/* BOTONES */

div.stButton > button,
div.stFormSubmitButton > button {
    background: linear-gradient(
        135deg,
        #d8b76d,
        #a27b35
    );
    color: #111111 !important;
    border: none;
    border-radius: 10px;
    min-height: 46px;
    font-weight: 800;
    transition: 0.2s;
}

div.stButton > button:hover,
div.stFormSubmitButton > button:hover {
    background: #f0d28c;
    border: 1px solid #f0d28c;
    color: #111111 !important;
}

/* PESTAÑAS */

button[role="tab"] {
    color: #d6b46a !important;
    font-weight: bold;
}

button[role="tab"][aria-selected="true"] {
    border-bottom: 3px solid #d6b46a !important;
}

/* INDICADORES DE CAJA */

[data-testid="stMetric"] {
    background: #202020;
    border: 1px solid #806b3c;
    border-radius: 13px;
    padding: 15px;
}

[data-testid="stMetricValue"] {
    color: #e3c174 !important;
}

/* SEPARADORES */

hr {
    border-color: #806b3c;
}

/* MENSAJES */

[data-testid="stAlert"] {
    border-radius: 10px;
}

/* PIE DE PAGINA */

.footer {
    text-align: center;
    color: #a8894b;
    font-size: 12px;
    padding: 20px 0;
    letter-spacing: 1px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# CABECERA PRINCIPAL
# ==========================================

st.markdown("""
<div class="premium-header">

    <div class="premium-icon">💈</div>

    <div class="premium-title">
        PELUQUERÍA
    </div>

    <div class="premium-subtitle">
        BARBERÍA · ESTILO · PRECISIÓN
    </div>

</div>
""", unsafe_allow_html=True)


# ==========================================
# MENU PRINCIPAL
# ==========================================

modo = st.radio(
    "Selecciona el acceso",
    ["📅 Reservar cita", "🔐 Acceso propietario"],
    horizontal=True
)


# ==========================================
# RESERVAR CITA
# ==========================================

if modo == "📅 Reservar cita":

    st.header("Reserva tu cita")

    st.write(
        "Selecciona tu servicio, el día y la hora que prefieras."
    )

    with st.form("formulario_cita"):

        cliente = st.text_input(
            "Nombre y apellidos",
            placeholder="Escribe tu nombre"
        )

        telefono = st.text_input(
            "Teléfono",
            placeholder="Tu número de teléfono"
        )

        servicio = st.selectbox(
            "Selecciona tu servicio",
            list(SERVICIOS.keys())
        )

        st.markdown(
            f"""
            <div style="
                background:#25231e;
                border:1px solid #b08d48;
                border-radius:12px;
                padding:15px;
                text-align:center;
                margin:12px 0;
            ">
                <div style="color:#c6a96c;font-size:13px;">
                    PRECIO DEL SERVICIO
                </div>
                <div style="
                    color:#e3c174;
                    font-size:30px;
                    font-weight:bold;
                ">
                    {SERVICIOS[servicio]:.2f} €
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        fecha = st.date_input(
            "Día de la cita",
            min_value=date.today(),
            value=date.today(),
            format="DD/MM/YYYY"
        )

        with conectar() as con:

            cursor = con.cursor()

            cursor.execute(
                "SELECT hora FROM citas WHERE fecha = %s",
                (fecha,)
            )

            filas = cursor.fetchall()
            cursor.close()

        horas_ocupadas = [
            fila[0].strftime("%H:%M")
            for fila in filas
        ]

        horas_libres = [
            h for h in HORAS
            if h not in horas_ocupadas
        ]

        if horas_libres:

            hora = st.selectbox(
                "Hora disponible",
                horas_libres
            )

        else:

            hora = None

            st.warning(
                "No quedan horas disponibles para este día."
            )

        aceptar = st.form_submit_button(
            "💈 CONFIRMAR RESERVA",
            use_container_width=True
        )

        if aceptar:

            if not cliente.strip() or not telefono.strip():

                st.error(
                    "Introduce tu nombre y teléfono."
                )

            elif not hora:

                st.error(
                    "Selecciona otro día."
                )

            else:

                try:

                    with conectar() as con:

                        cursor = con.cursor()

                        cursor.execute("""
                            INSERT INTO citas
                            (
                                cliente,
                                telefono,
                                servicio,
                                precio,
                                fecha,
                                hora
                            )
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (
                            cliente.strip(),
                            telefono.strip(),
                            servicio,
                            SERVICIOS[servicio],
                            fecha,
                            hora
                        ))

                        cursor.close()

                    st.success(
                        f"¡Reserva confirmada para {cliente}! "
                        f"Fecha: {fecha.strftime('%d/%m/%Y')} "
                        f"a las {hora}."
                    )

                except psycopg2.errors.UniqueViolation:

                    st.error(
                        "Esa hora acaba de ser reservada. "
                        "Selecciona otra."
                    )

                except Exception:

                    st.error(
                        "No se ha podido guardar la cita. "
                        "Inténtalo de nuevo."
                    )


# ==========================================
# ACCESO PROPIETARIO
# ==========================================

elif modo == "🔐 Acceso propietario":

    st.header("Zona privada")

    if not st.session_state.get("autorizado", False):

        st.markdown("""
        <div style="
            text-align:center;
            padding:15px;
            color:#d6b46a;
        ">
            🔒 ACCESO EXCLUSIVO DEL PROPIETARIO
        </div>
        """, unsafe_allow_html=True)

        pin = st.text_input(
            "Introduce tu PIN",
            type="password"
        )

        if st.button(
            "🔐 ENTRAR",
            use_container_width=True
        ):

            if pin == PIN:

                st.session_state.autorizado = True
                st.rerun()

            else:

                st.error("PIN incorrecto.")

    else:

        if st.button("Cerrar sesión"):

            st.session_state.autorizado = False
            st.rerun()

        st.subheader("Panel de control")

        pestanas = st.tabs([
            "📋 Citas",
            "💰 Caja"
        ])

        # ==================================
        # PESTAÑA CITAS
        # ==================================

        with pestanas[0]:

            dia = st.date_input(
                "Consultar citas del día",
                value=date.today(),
                format="DD/MM/YYYY"
            )

            with conectar() as con:

                cursor = con.cursor()

                cursor.execute("""
                    SELECT
                        id,
                        cliente,
                        telefono,
                        servicio,
                        precio,
                        hora,
                        pagada
                    FROM citas
                    WHERE fecha = %s
                    ORDER BY hora
                """, (dia,))

                citas = cursor.fetchall()
                cursor.close()

            if not citas:

                st.info(
                    "No hay citas para este día."
                )

            else:

                cobradas = sum(
                    1 for c in citas if c[6]
                )

                pendientes_count = len(citas) - cobradas

                col1, col2 = st.columns(2)

                col1.metric(
                    "Total de citas",
                    len(citas)
                )

                col2.metric(
                    "Citas cobradas",
                    cobradas
                )

                st.divider()

                for c in citas:

                    hora_texto = c[5].strftime("%H:%M")

                    with st.container(border=True):

                        st.markdown(
                            f"### 🕒 {hora_texto} — {c[1]}"
                        )

                        st.write(
                            f"**{c[3]}** · {c[4]:.2f} €"
                        )

                        st.caption(
                            f"Teléfono: {c[2]}"
                        )

                        if c[6]:

                            st.success(
                                "✓ CITA PAGADA"
                            )

                        else:

                            st.warning(
                                "PENDIENTE DE COBRO"
                            )

                            if st.button(
                                "💰 COBRAR CITA",
                                key=f"cobrar_{c[0]}",
                                use_container_width=True
                            ):

                                with conectar() as con:

                                    cursor = con.cursor()

                                    cursor.execute(
                                        """
                                        UPDATE citas
                                        SET pagada = TRUE
                                        WHERE id = %s
                                        """,
                                        (c[0],)
                                    )

                                    cursor.close()

                                st.rerun()

        # ==================================
        # PESTAÑA CAJA
        # ==================================

        with pestanas[1]:

            st.subheader("💰 Caja del día")

            with conectar() as con:

                cursor = con.cursor()

                cursor.execute("""
                    SELECT COALESCE(SUM(precio), 0)
                    FROM citas
                    WHERE fecha = %s
                    AND pagada = TRUE
                """, (date.today(),))

                total = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT COALESCE(SUM(precio), 0)
                    FROM citas
                    WHERE fecha = %s
                    AND pagada = FALSE
                """, (date.today(),))

                pendientes = cursor.fetchone()[0]

                cursor.close()

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "💶 RECAUDACIÓN DE HOY",
                    f"{total:.2f} €"
                )

            with col2:

                st.metric(
                    "⏳ PENDIENTE DE COBRO",
                    f"{pendientes:.2f} €"
                )

            st.divider()

            st.caption(
                "Resumen económico correspondiente a las citas de hoy."
            )


# ==========================================
# PIE DE PAGINA
# ==========================================

st.markdown("""
<div class="footer">
    💈 SISTEMA DE GESTIÓN · PELUQUERÍA
    <br>
    DISEÑO PREMIUM
</div>
""", unsafe_allow_html=True)
