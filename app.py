
import streamlit as st
import psycopg2
from contextlib import contextmanager
from datetime import date

st.set_page_config(
    page_title="Peluquería",
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


st.markdown("""
<style>
.stApp {background-color: #f5f3ef;}
h1, h2, h3 {color: #222222;}
div.stButton > button {
    border-radius: 10px;
    min-height: 45px;
}
</style>
""", unsafe_allow_html=True)

st.title("💈 PELUQUERÍA")
st.caption("Sistema de citas y caja")

modo = st.radio(
    "Selecciona el acceso",
    ["📅 Reservar cita", "🔐 Acceso propietario"],
    horizontal=True
)

if modo == "📅 Reservar cita":

    st.header("Reserva tu cita")
    st.write("Elige tu servicio, día y hora.")

    with st.form("formulario_cita"):

        cliente = st.text_input("Nombre y apellidos")
        telefono = st.text_input("Teléfono")

        servicio = st.selectbox(
            "Servicio",
            list(SERVICIOS.keys())
        )

        st.write(f"**Precio: {SERVICIOS[servicio]:.2f} €**")

        fecha = st.date_input(
            "Día de la cita",
            min_value=date.today(),
            value=date.today()
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
            fila[0].strftime("%H:%M") for fila in filas
        ]

        horas_libres = [
            h for h in HORAS if h not in horas_ocupadas
        ]

        if horas_libres:
            hora = st.selectbox(
                "Hora disponible",
                horas_libres
            )
        else:
            hora = None
            st.warning("No quedan horas disponibles para este día.")

        aceptar = st.form_submit_button(
            "CONFIRMAR RESERVA",
            use_container_width=True
        )

        if aceptar:

            if not cliente.strip() or not telefono.strip():
                st.error("Introduce tu nombre y teléfono.")

            elif not hora:
                st.error("Selecciona otro día.")

            else:
                try:
                    with conectar() as con:
                        cursor = con.cursor()

                        cursor.execute("""
                            INSERT INTO citas
                            (cliente, telefono, servicio, precio, fecha, hora)
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
                        f"¡Cita reservada para {cliente} "
                        f"el {fecha.strftime('%d/%m/%Y')} a las {hora}!"
                    )

                except psycopg2.errors.UniqueViolation:
                    st.error(
                        "Esa hora acaba de ser reservada. "
                        "Selecciona otra."
                    )

                except Exception as e:
                    st.error("No se ha podido guardar la cita.")
                    st.exception(e)


elif modo == "🔐 Acceso propietario":

    st.header("Zona privada")

    if not st.session_state.get("autorizado", False):

        pin = st.text_input(
            "Introduce tu PIN",
            type="password"
        )

        if st.button("ENTRAR", use_container_width=True):

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

        pestanas = st.tabs(["📋 Citas", "💰 Caja"])

        with pestanas[0]:

            dia = st.date_input(
                "Consultar citas del día",
                value=date.today()
            )

            with conectar() as con:
                cursor = con.cursor()

                cursor.execute("""
                    SELECT id, cliente, telefono, servicio,
                           precio, hora, pagada
                    FROM citas
                    WHERE fecha = %s
                    ORDER BY hora
                """, (dia,))

                citas = cursor.fetchall()
                cursor.close()

            if not citas:
                st.info("No hay citas para este día.")

            else:

                for c in citas:

                    hora_texto = c[5].strftime("%H:%M")

                    with st.container(border=True):

                        st.write(f"**{hora_texto} — {c[1]}**")
                        st.write(f"{c[3]} · {c[4]:.2f} €")
                        st.caption(f"Teléfono: {c[2]}")

                        if c[6]:
                            st.success("PAGADA")

                        else:
                            st.warning("PENDIENTE DE COBRO")

                            if st.button(
                                "Cobrar",
                                key=f"cobrar_{c[0]}"
                            ):

                                with conectar() as con:
                                    cursor = con.cursor()

                                    cursor.execute(
                                        "UPDATE citas SET pagada=TRUE WHERE id=%s",
                                        (c[0],)
                                    )

                                    cursor.close()

                                st.rerun()

        with pestanas[1]:

            with conectar() as con:
                cursor = con.cursor()

                cursor.execute("""
                    SELECT COALESCE(SUM(precio), 0)
                    FROM citas
                    WHERE fecha=%s AND pagada=TRUE
                """, (date.today(),))

                total = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT COALESCE(SUM(precio), 0)
                    FROM citas
                    WHERE fecha=%s AND pagada=FALSE
                """, (date.today(),))

                pendientes = cursor.fetchone()[0]

                cursor.close()

            st.metric(
                "Recaudación de hoy",
                f"{total:.2f} €"
            )

            st.metric(
                "Pendiente de cobro",
                f"{pendientes:.2f} €"
            )

st.divider()
st.caption("Sistema de gestión · Peluquería")
