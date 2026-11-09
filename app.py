import streamlit as st
import psycopg2
import calendar
from datetime import date, time, datetime
from decimal import Decimal
from html import escape

# =========================================================
# CONFIGURACIÓN
# =========================================================

st.set_page_config(
    page_title="Peluquería",
    page_icon="💈",
    layout="centered"
)

HORAS = [
    f"{h:02d}:{m:02d}"
    for inicio, fin in [(9, 14), (16, 20)]
    for h in range(inicio, fin)
    for m in (0, 30)
]

MESES = [
    "Enero", "Febrero", "Marzo", "Abril",
    "Mayo", "Junio", "Julio", "Agosto",
    "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

# =========================================================
# CONEXIÓN A SUPABASE
# =========================================================

def conectar_db():
    return psycopg2.connect(
        host=st.secrets["DB_HOST"],
        port=st.secrets["DB_PORT"],
        dbname=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        sslmode="require"
    )


def consultar(sql, parametros=None):
    with conectar_db() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, parametros or ())
            return cur.fetchall()


def ejecutar(sql, parametros=None):
    with conectar_db() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, parametros or ())


def euros(valor):
    valor = Decimal(str(valor or 0))
    return f"{valor:.2f} €".replace(".", ",")


def asegurar_columna_duracion():
    """Añade la columna duracion a productos si aún no existe."""
    ejecutar("""
        ALTER TABLE public.productos
        ADD COLUMN IF NOT EXISTS duracion INTEGER NOT NULL DEFAULT 30
    """)


def obtener_servicios_activos():
    return consultar("""
        SELECT id, nombre, precio, duracion
        FROM public.productos
        WHERE activo = TRUE
        ORDER BY nombre ASC
    """)


# =========================================================
# DISEÑO
# =========================================================

st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #252525 0%, #080808 55%);
    color: #f5f5f5;
}

.block-container {
    max-width: 850px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    color: #d4af37 !important;
}

p, label, .stMarkdown, .stCaption {
    color: #f0f0f0;
}

div[data-testid="stMetric"] {
    background: #171717;
    border: 1px solid #b8952e;
    border-radius: 12px;
    padding: 15px;
}

div[data-testid="stMetricLabel"] {
    color: #d4af37 !important;
}

div[data-testid="stMetricValue"] {
    color: #ffffff !important;
}

.stButton button,
.stFormSubmitButton button {
    background: linear-gradient(135deg, #d4af37, #a88720);
    color: #080808;
    border: none;
    border-radius: 10px;
    min-height: 45px;
    font-weight: bold;
    width: 100%;
}

.stButton button:hover,
.stFormSubmitButton button:hover {
    background: #f0cf60;
    color: #000000;
}

input, textarea {
    background-color: #1b1b1b !important;
    color: white !important;
}

div[data-baseweb="select"] {
    background-color: #1b1b1b;
}

div[data-testid="stDateInput"] input {
    background-color: #1b1b1b;
    color: white;
}

hr {
    border-color: #a88720;
}

.cita-card {
    background: #171717;
    border: 1px solid #b8952e;
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 12px;
}

.estado-pagado {
    color: #5bd18b;
    font-weight: bold;
}

.estado-pendiente {
    color: #ffcc66;
    font-weight: bold;
}

.mensaje-exito {
    background: #123d28;
    border: 2px solid #36c878;
    border-radius: 14px;
    padding: 20px;
    margin-top: 20px;
    margin-bottom: 20px;
    text-align: center;
    box-shadow: 0 0 14px rgba(54, 200, 120, 0.20);
}

.mensaje-exito h3 {
    color: #75f0a8 !important;
    margin-top: 0;
    margin-bottom: 12px;
    font-size: 22px;
}

.mensaje-exito p {
    color: #ffffff !important;
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 5px;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# CABECERA
# =========================================================

st.markdown(
    "<h1 style='text-align:center;'>💈 PELUQUERÍA</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center;color:#d4af37;'>"
    "Reserva tu cita · Panel Profesional"
    "</p>",
    unsafe_allow_html=True
)

st.divider()


# =========================================================
# NAVEGACIÓN
# =========================================================

modo = st.radio(
    "Selecciona una opción",
    ["Reservar cita", "Panel propietario"],
    horizontal=True
)


# =========================================================
# RESERVAR CITA
# =========================================================

if modo == "Reservar cita":

    st.markdown("## 📅 Reserva tu cita")

    fecha_reserva = st.date_input(
        "Selecciona el día",
        value=date.today(),
        min_value=date.today(),
        format="DD/MM/YYYY"
    )

    citas_ocupadas = consultar(
        """
        SELECT hora
        FROM public.citas
        WHERE fecha = %s
        """,
        (fecha_reserva,)
    )

    horas_ocupadas = [
        str(fila[0])[:5]
        for fila in citas_ocupadas
    ]

    horas_disponibles = [
        hora for hora in HORAS
        if hora not in horas_ocupadas
    ]

    if fecha_reserva == date.today():
        hora_actual = datetime.now().strftime("%H:%M")
        horas_disponibles = [
            hora for hora in horas_disponibles
            if hora > hora_actual
        ]

    if not horas_disponibles:
        st.warning("No quedan horas disponibles para este día.")

    else:
        servicios_activos = obtener_servicios_activos()

        if not servicios_activos:
            st.warning(
                "Actualmente no hay servicios disponibles para reservar. "
                "Contacta con la peluquería."
            )
        else:
            # Diccionario con nombre como clave y datos del servicio
            servicios_dict = {
                servicio[1]: {
                    "id": servicio[0],
                    "nombre": servicio[1],
                    "precio": servicio[2],
                    "duracion": servicio[3]
                }
                for servicio in servicios_activos
            }

            with st.form("formulario_reserva"):

                cliente = st.text_input(
                    "Nombre del cliente",
                    placeholder="Introduce tu nombre"
                )

                telefono = st.text_input(
                    "Teléfono",
                    placeholder="Introduce tu teléfono"
                )

                servicio_nombre = st.selectbox(
                    "Servicio",
                    list(servicios_dict.keys())
                )

                servicio_seleccionado = servicios_dict[servicio_nombre]

                st.markdown(
                    f"### Precio: {euros(servicio_seleccionado['precio'])}"
                )
                st.caption(
                    f"Duración aproximada: "
                    f"{servicio_seleccionado['duracion']} minutos"
                )

                hora_reserva = st.selectbox(
                    "Hora disponible",
                    horas_disponibles
                )

                reservar = st.form_submit_button(
                    "Confirmar reserva"
                )

            if reservar:
                if not cliente.strip():
                    st.error("Introduce el nombre del cliente.")
                elif not telefono.strip():
                    st.error("Introduce el teléfono.")
                else:
                    try:
                        ejecutar(
                            """
                            INSERT INTO public.citas
                            (cliente, telefono, servicio, precio, fecha, hora, pagada)
                            VALUES (%s, %s, %s, %s, %s, %s, FALSE)
                            """,
                            (
                                cliente.strip(),
                                telefono.strip(),
                                servicio_nombre,
                                servicio_seleccionado["precio"],
                                fecha_reserva,
                                hora_reserva,
                            )
                        )

                        st.markdown(
                            f"""
                            <div class="mensaje-exito">
                                <h3>✅ ¡CITA CONFIRMADA!</h3>
                                <p>Tu reserva se ha realizado correctamente.</p>
                                <p>👤 Cliente: {escape(cliente.strip())}</p>
                                <p>📅 Fecha: {fecha_reserva.strftime('%d/%m/%Y')}</p>
                                <p>🕒 Hora: {hora_reserva}</p>
                                <p>✂️ Servicio: {escape(servicio_nombre)}</p>
                                <p>💶 Precio: {euros(servicio_seleccionado['precio'])}</p>
                                <p>⏱️ Duración: {servicio_seleccionado['duracion']} minutos</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    except Exception:
                        st.error(
                            "No se ha podido realizar la reserva. "
                            "Puede que esa hora ya esté ocupada."
                        )


# =========================================================
# PANEL DEL PROPIETARIO
# =========================================================

elif modo == "Panel propietario":

    st.markdown("## 🔐 Panel del propietario")

    if "propietario_autenticado" not in st.session_state:
        st.session_state.propietario_autenticado = False

    if not st.session_state.propietario_autenticado:

        pin = st.text_input(
            "Introduce el PIN del propietario",
            type="password"
        )

        if st.button("Entrar"):

            pin_correcto = str(
                st.secrets.get("OWNER_PIN", "1234")
            )

            if pin == pin_correcto:
                st.session_state.propietario_autenticado = True
                st.rerun()
            else:
                st.error("PIN incorrecto.")

    else:

        # Garantizamos la columna de duración en la tabla de productos.
        try:
            asegurar_columna_duracion()
        except Exception:
            st.error(
                "No se ha podido comprobar la columna de duración en Supabase. "
                "Revisa los permisos de la base de datos."
            )
            st.stop()

        if st.button("Cerrar sesión del propietario"):
            st.session_state.propietario_autenticado = False
            st.rerun()

        pestañas = st.tabs([
            "📅 Citas",
            "💰 Caja",
            "✂️ Servicios y cortes"
        ])

        # =================================================
        # PESTAÑA CITAS
        # =================================================

        with pestañas[0]:

            st.markdown("### Gestión de citas")

            fecha_gestion = st.date_input(
                "Consultar citas del día",
                value=date.today(),
                format="DD/MM/YYYY",
                key="fecha_gestion"
            )

            citas_dia = consultar(
                """
                SELECT id, cliente, telefono, servicio,
                       precio, hora, pagada
                FROM public.citas
                WHERE fecha = %s
                ORDER BY hora
                """,
                (fecha_gestion,)
            )

            total_citas = len(citas_dia)
            citas_cobradas = sum(1 for cita in citas_dia if cita[6])
            citas_pendientes = total_citas - citas_cobradas

            col1, col2, col3 = st.columns(3)
            col1.metric("Citas", total_citas)
            col2.metric("Cobradas", citas_cobradas)
            col3.metric("Pendientes", citas_pendientes)

            st.divider()

            if not citas_dia:
                st.info("No hay citas para este día.")
            else:
                for cita in citas_dia:
                    (
                        cita_id,
                        cliente_cita,
                        telefono_cita,
                        servicio_cita,
                        precio_cita,
                        hora_cita,
                        pagada_cita
                    ) = cita

                    estado = (
                        "✅ COBRADA"
                        if pagada_cita
                        else "🟡 PENDIENTE DE COBRO"
                    )

                    with st.container(border=True):
                        st.markdown(
                            f"### 🕒 {str(hora_cita)[:5]} · "
                            f"{escape(str(cliente_cita))}"
                        )
                        st.write(f"📞 {telefono_cita}")
                        st.write(f"✂️ {servicio_cita}")
                        st.write(f"💶 {euros(precio_cita)}")
                        st.write(estado)

                        if not pagada_cita:
                            if st.button(
                                f"💰 Cobrar cita de {cliente_cita}",
                                key=f"cobrar_cita_{cita_id}"
                            ):
                                ejecutar(
                                    """
                                    UPDATE public.citas
                                    SET pagada = TRUE
                                    WHERE id = %s
                                    """,
                                    (cita_id,)
                                )
                                st.success(
                                    f"Cita de {cliente_cita} cobrada."
                                )
                                st.rerun()
                                        # =================================================
        # PESTAÑA CAJA
        # =================================================

        with pestañas[1]:

            st.markdown("## 💰 Caja")
            st.markdown("### 📍 Caja de hoy")

            caja_hoy = consultar(
                """
                SELECT
                    COALESCE(SUM(precio) FILTER (WHERE pagada = TRUE), 0),
                    COALESCE(SUM(precio) FILTER (WHERE pagada = FALSE), 0),
                    COUNT(*) FILTER (WHERE pagada = TRUE),
                    COUNT(*)
                FROM public.citas
                WHERE fecha = %s
                """,
                (date.today(),)
            )[0]

            cobrado_hoy = caja_hoy[0]
            pendiente_hoy = caja_hoy[1]
            numero_cobradas_hoy = caja_hoy[2]
            total_citas_hoy = caja_hoy[3]

            col1, col2 = st.columns(2)
            col1.metric("Cobrado hoy", euros(cobrado_hoy))
            col2.metric("Pendiente hoy", euros(pendiente_hoy))

            st.caption(
                f"Citas cobradas hoy: {numero_cobradas_hoy} "
                f"de {total_citas_hoy}"
            )

            st.divider()
            st.markdown("### 📆 Consulta de caja mensual")

            col_mes, col_anio = st.columns(2)

            with col_mes:
                mes_seleccionado = st.selectbox(
                    "Selecciona el mes",
                    MESES,
                    index=date.today().month - 1,
                    key="mes_caja"
                )

            with col_anio:
                anios_disponibles = list(
                    range(date.today().year, date.today().year - 6, -1)
                )

                anio_seleccionado = st.selectbox(
                    "Selecciona el año",
                    anios_disponibles,
                    index=0,
                    key="anio_caja"
                )

            numero_mes = MESES.index(mes_seleccionado) + 1
            fecha_inicio = date(anio_seleccionado, numero_mes, 1)

            if numero_mes == 12:
                fecha_fin = date(anio_seleccionado + 1, 1, 1)
            else:
                fecha_fin = date(anio_seleccionado, numero_mes + 1, 1)

            citas_mes = consultar(
                """
                SELECT id, cliente, telefono, servicio,
                       precio, fecha, hora, pagada
                FROM public.citas
                WHERE fecha >= %s
                  AND fecha < %s
                ORDER BY fecha ASC, hora ASC
                """,
                (fecha_inicio, fecha_fin)
            )

            total_citas_mes = len(citas_mes)

            total_cobrado_mes = sum(
                (
                    Decimal(str(cita[4] or 0))
                    for cita in citas_mes
                    if cita[7]
                ),
                Decimal("0.00")
            )

            total_pendiente_mes = sum(
                (
                    Decimal(str(cita[4] or 0))
                    for cita in citas_mes
                    if not cita[7]
                ),
                Decimal("0.00")
            )

            numero_cobradas_mes = sum(1 for cita in citas_mes if cita[7])
            numero_pendientes_mes = sum(1 for cita in citas_mes if not cita[7])

            st.markdown(
                f"### Resumen de {mes_seleccionado} "
                f"{anio_seleccionado}"
            )

            col1, col2 = st.columns(2)
            col1.metric("💶 Total cobrado del mes", euros(total_cobrado_mes))
            col2.metric("🟡 Pendiente de cobrar", euros(total_pendiente_mes))

            col3, col4 = st.columns(2)
            col3.metric("✅ Citas cobradas", numero_cobradas_mes)
            col4.metric("📅 Total de citas", total_citas_mes)

            st.caption(
                f"Citas pendientes de cobro: {numero_pendientes_mes}"
            )

            st.divider()
            st.markdown(f"### 📋 Histórico de {mes_seleccionado}")

            if not citas_mes:
                st.info("No hay citas registradas durante este mes.")
                            else:
                for cita in citas_mes:
                    (
                        cita_id,
                        cliente_cita,
                        telefono_cita,
                        servicio_cita,
                        precio_cita,
                        fecha_cita,
                        hora_cita,
                        pagada_cita
                    ) = cita

                    fecha_texto = fecha_cita.strftime("%d/%m/%Y")
                    hora_texto = str(hora_cita)[:5]

                    if pagada_cita:
                        estado_texto = "✅ COBRADA"
                        clase_estado = "estado-pagado"
                    else:
                        estado_texto = "🟡 PENDIENTE"
                        clase_estado = "estado-pendiente"

                    st.markdown(
                        f"""
                        <div class="cita-card">
                            <h4 style="color:#d4af37;">
                                {fecha_texto} · {hora_texto}
                            </h4>
                            <p><b>Cliente:</b> {escape(str(cliente_cita))}</p>
                            <p><b>Teléfono:</b> {escape(str(telefono_cita))}</p>
                            <p><b>Servicio:</b> {escape(str(servicio_cita))}</p>
                            <p><b>Importe:</b> {euros(precio_cita)}</p>
                            <p class="{clase_estado}">{estado_texto}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    if not pagada_cita:
                        if st.button(
                            f"💰 Cobrar {cliente_cita} ({fecha_texto})",
                            key=f"cobrar_mes_{cita_id}"
                        ):
                            ejecutar(
                                """
                                UPDATE public.citas
                                SET pagada = TRUE
                                WHERE id = %s
                                """,
                                (cita_id,)
                            )
                            st.success(f"Cita de {cliente_cita} cobrada.")
                            st.rerun()

            st.divider()
            st.markdown(
                "<p style='text-align:center;color:#d4af37;'>"
                "💈 Gestión de caja · Peluquería"
                "</p>",
                unsafe_allow_html=True
            )

        # =================================================
        # PESTAÑA SERVICIOS Y CORTES
        # =================================================

        with pestañas[2]:

            st.markdown("## ✂️ Gestión de servicios y cortes")
            st.caption(
                "Aquí puedes administrar los cortes, tratamientos, "
                "precios y duración que aparecen en las reservas de los clientes."
            )

            # ---------------------------------------------
            # AÑADIR SERVICIO
            # ---------------------------------------------

            st.markdown("### ➕ Añadir nuevo servicio")

            with st.form("formulario_nuevo_servicio"):

                nuevo_nombre = st.text_input(
                    "Nombre del corte o servicio",
                    placeholder="Ej. Corte degradado"
                )

                nuevo_precio = st.number_input(
                    "Precio (€)",
                    min_value=0.0,
                    value=12.0,
                    step=0.50,
                    format="%.2f"
                )

                nueva_duracion = st.number_input(
                    "Duración (minutos)",
                    min_value=5,
                    max_value=240,
                    value=30,
                    step=5
                )

                guardar_servicio = st.form_submit_button(
                    "Añadir servicio al catálogo"
                )

            if guardar_servicio:
                if not nuevo_nombre.strip():
                    st.error("Introduce el nombre del servicio.")
                else:
                    ejecutar(
                        """
                        INSERT INTO public.productos
                        (nombre, precio, activo, duracion)
                        VALUES (%s, %s, TRUE, %s)
                        """,
                        (
                            nuevo_nombre.strip(),
                            Decimal(str(nuevo_precio)),
                            int(nueva_duracion)
                        )
                    )
                    st.success(
                        f"Servicio «{nuevo_nombre.strip()}» añadido. "
                        "Ya estará disponible en las reservas."
                    )
                    st.rerun()

            st.divider()

            # ---------------------------------------------
            # LISTADO DEL CATÁLOGO
            # ---------------------------------------------

            st.markdown("### 📋 Catálogo de servicios")

            servicios = consultar(
                """
                SELECT id, nombre, precio, activo, duracion
                FROM public.productos
                ORDER BY nombre ASC
                """
            )

            if not servicios:
                st.info("Todavía no hay servicios registrados.")
            else:
                total_servicios = len(servicios)
                servicios_activos = sum(1 for s in servicios if s[3])

                col1, col2 = st.columns(2)
                col1.metric("Servicios registrados", total_servicios)
                col2.metric("Servicios visibles en reservas", servicios_activos)

                for servicio in servicios:
                    (
                        servicio_id,
                        nombre_servicio,
                        precio_servicio,
                        activo_servicio,
                        duracion_servicio
                    ) = servicio

                    with st.container(border=True):
                        col_nombre, col_estado = st.columns([3, 1])

                        with col_nombre:
                            st.markdown(f"### ✂️ {escape(str(nombre_servicio))}")
                            st.markdown(
                                f"**Precio: {euros(precio_servicio)}**"
                            )
                            st.caption(
                                f"Duración: {duracion_servicio} minutos"
                            )

                        with col_estado:
                            if activo_servicio:
                                st.success("Activo")
                            else:
                                st.warning("Inactivo")

                st.divider()

                # -----------------------------------------
                # EDITAR SERVICIO
                # -----------------------------------------

                st.markdown("### ✏️ Modificar corte o servicio")

                opciones_servicios = {
                    f"{s[1]} — {euros(s[2])} · {s[4]} min (ID {s[0]})": s
                    for s in servicios
                }

                servicio_a_editar_label = st.selectbox(
                    "Selecciona el servicio que quieres modificar",
                    list(opciones_servicios.keys()),
                    key="servicio_editar"
                )

                servicio_actual = opciones_servicios[servicio_a_editar_label]

                id_editar = servicio_actual[0]
                nombre_actual = servicio_actual[1]
                precio_actual = servicio_actual[2]
                activo_actual = servicio_actual[3]
                duracion_actual = servicio_actual[4]

                with st.form("formulario_editar_servicio"):

                    nombre_editado = st.text_input(
                        "Nombre del servicio",
                        value=nombre_actual
                    )

                    precio_editado = st.number_input(
                        "Precio (€)",
                        min_value=0.0,
                        value=float(precio_actual),
                        step=0.50,
                        format="%.2f"
                    )

                    duracion_editada = st.number_input(
                        "Duración (minutos)",
                        min_value=5,
                        max_value=240,
                        value=int(duracion_actual),
                        step=5
                    )

                    activo_editado = st.checkbox(
                        "Mostrar este servicio en las reservas",
                        value=activo_actual
                    )

                    guardar_cambios = st.form_submit_button(
                        "Guardar cambios del servicio"
                    )

                if guardar_cambios:
                    if not nombre_editado.strip():
                        st.error("El nombre del servicio no puede estar vacío.")
                    else:
                        ejecutar(
                            """
                            UPDATE public.productos
                            SET nombre = %s,
                                precio = %s,
                                duracion = %s,
                                activo = %s
                            WHERE id = %s
                            """,
                            (
                                nombre_editado.strip(),
                                Decimal(str(precio_editado)),
                                int(duracion_editada),
                                activo_editado,
                                id_editar
                            )
                        )

                        st.success(
                            "Servicio actualizado. "
                            "El nuevo precio aparecerá en próximas reservas."
                        )
                        st.rerun()

                st.divider()

                # -----------------------------------------
                # ELIMINAR SERVICIO
                # -----------------------------------------

                st.markdown("### 🗑️ Eliminar servicio")

                st.warning(
                    "Eliminar un servicio lo quitará del catálogo. "
                    "Las citas ya registradas conservarán sus datos."
                )

                confirmar_eliminacion = st.checkbox(
                    f"Confirmo que quiero eliminar «{nombre_actual}»",
                    key=f"confirmar_borrar_servicio_{id_editar}"
                )

                if st.button(
                    "Eliminar servicio seleccionado",
                    key="boton_eliminar_servicio"
                ):
                    if confirmar_eliminacion:
                        ejecutar(
                            """
                            DELETE FROM public.productos
                            WHERE id = %s
                            """,
                            (id_editar,)
                        )
                        st.success("Servicio eliminado del catálogo.")
                        st.rerun()
                    else:
                        st.warning(
                            "Marca la casilla de confirmación antes de eliminar."
                        )
                
                                
