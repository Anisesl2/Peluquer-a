import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import date, datetime, time
from decimal import Decimal
from html import escape
import re, hashlib, hmac, secrets

st.set_page_config(page_title="Peluquería", page_icon="💈", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Playfair+Display:wght@400;500;600;700&display=swap');
:root{--bg:#111211;--panel:#20211e;--panel2:#292a26;--gold:#c7ad7b;--gold2:#dfcca5;--text:#eee9df;--muted:#aaa69d;--line:rgba(199,173,123,.22)}
.stApp{background:radial-gradient(ellipse at 50% -15%,rgba(199,173,123,.08),transparent 42%),var(--bg);color:var(--text);font-family:'DM Sans',sans-serif}
.block-container{max-width:1280px;padding:1.3rem 2rem 3rem}
h1,h2,h3{font-family:'Playfair Display',Georgia,serif!important;color:var(--gold2)!important;font-weight:500!important}
.stButton>button,.stLinkButton>a,[data-testid="stFormSubmitButton"] button{background:linear-gradient(135deg,#d8c49b,#b89b68);color:#171713!important;border:1px solid rgba(235,220,188,.55);border-radius:5px;min-height:45px;font-weight:700;letter-spacing:.045em;transition:.2s}
.stButton>button:hover,.stLinkButton>a:hover{filter:brightness(1.08);transform:translateY(-1px)}
[data-testid="stForm"]{background:linear-gradient(145deg,#252622,#1b1c1a);border:1px solid var(--line);border-radius:9px;padding:22px}
[data-baseweb="input"],[data-baseweb="select"],[data-baseweb="textarea"]{background:var(--panel2)}
input,textarea{color:var(--text)!important}
[data-testid="stMetric"]{background:linear-gradient(145deg,#242521,#1b1c1a);border:1px solid var(--line);padding:16px;border-radius:8px}
[data-testid="stMetricValue"]{color:var(--gold2)}
[data-testid="stMetricLabel"]{color:var(--muted)}
[data-testid="stTabs"] button{color:var(--gold2);font-weight:600}
hr{border-color:var(--line)}
.hero{min-height:540px;background-size:cover;background-position:center 44%;border:1px solid var(--line);border-radius:9px;display:flex;align-items:center;justify-content:center;text-align:center;padding:35px;position:relative;margin:15px 0 28px;box-shadow:0 24px 60px #0005}
.hero:before{content:"";position:absolute;inset:0;border-radius:9px;background:linear-gradient(180deg,#0a0b0a55,#0a0b0add)}
.hero-content{position:relative;max-width:850px}
.hero h1{font-size:clamp(32px,5.4vw,66px)!important;letter-spacing:.04em;text-transform:uppercase;color:#f1e7d3!important}
.hero p{color:#f0ece4;line-height:1.8}
.hero-label{color:var(--gold2);letter-spacing:.3em;font-size:12px;font-weight:700}
.hero-logo{max-width:110px;max-height:90px;object-fit:contain;margin-bottom:20px}
.section-title{text-align:center;margin:42px 0 25px}
.section-title h2{letter-spacing:.06em}
.section-title p,.small-text{color:var(--muted);font-size:13px}
.gold-line{width:52px;height:1px;background:var(--gold);margin:15px auto 20px}
.info-card{background:linear-gradient(145deg,#242521,#1b1c1a);border:1px solid var(--line);border-radius:8px;padding:23px;box-shadow:0 10px 28px #0002;margin-bottom:16px}
.info-card p{color:#d0ccc3;line-height:1.7}
.footer{text-align:center;padding:35px 10px 18px;margin-top:48px;border-top:1px solid var(--line);color:var(--muted);font-size:13px}
.footer strong{color:var(--gold2);font:500 18px 'Playfair Display';letter-spacing:.08em}
@media(max-width:768px){.block-container{padding:.6rem .8rem 2rem}.hero{min-height:430px;padding:22px}.info-card{padding:17px}[data-testid="stForm"]{padding:15px}.stButton>button{font-size:12px}}
</style>
""", unsafe_allow_html=True)

# ---------------------- DATABASE ----------------------
def conectar_db():
    return psycopg2.connect(host=st.secrets["DB_HOST"],port=st.secrets.get("DB_PORT",5432),
        database=st.secrets["DB_NAME"],user=st.secrets["DB_USER"],password=st.secrets["DB_PASSWORD"],
        sslmode="require",connect_timeout=15)

def consultar(sql, parametros=None):
    con=conectar_db()
    try:
        with con.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql,parametros or ())
            return [dict(r) for r in cur.fetchall()]
    finally: con.close()

def ejecutar(sql,parametros=None):
    con=conectar_db()
    try:
        with con.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql,parametros or ())
            rows=cur.fetchall() if cur.description else []
        con.commit()
        return [dict(r) for r in rows]
    except Exception:
        con.rollback()
        raise
    finally: con.close()

def euros(v):
    try:return f"{float(v):,.2f} €".replace(",","X").replace(".",",").replace("X",".")
    except:return "0,00 €"

# ---------------------- SECURITY ----------------------
def crear_hash_pin(pin,salt=None):
    salt=salt or secrets.token_bytes(16)
    return salt.hex(),hashlib.pbkdf2_hmac("sha256",pin.encode(),salt,600_000).hex()

def obtener_credencial_pin():
    rows=consultar("SELECT salt,pin_hash FROM public.seguridad WHERE id=1")
    return rows[0] if rows else None

def verificar_pin(pin):
    cred=obtener_credencial_pin()
    if not cred:return False
    try:
        hash_pin=hashlib.pbkdf2_hmac("sha256",pin.encode(),bytes.fromhex(cred["salt"]),600_000)
        return hmac.compare_digest(hash_pin,bytes.fromhex(cred["pin_hash"]))
    except (ValueError,TypeError,KeyError):return False

def guardar_nuevo_pin(pin):
    salt,h=crear_hash_pin(pin)
    ejecutar("""INSERT INTO public.seguridad(id,salt,pin_hash,actualizado) VALUES(1,%s,%s,NOW())
    ON CONFLICT(id) DO UPDATE SET salt=EXCLUDED.salt,pin_hash=EXCLUDED.pin_hash,actualizado=NOW()""",(salt,h))

# ---------------------- INITIALIZATION ----------------------
def inicializar_base_datos():
    con=conectar_db()
    try:
        with con.cursor() as cur:
            cur.execute("""CREATE TABLE IF NOT EXISTS public.servicios(id SERIAL PRIMARY KEY,nombre VARCHAR(150) NOT NULL UNIQUE,precio NUMERIC(10,2) NOT NULL DEFAULT 0,activo BOOLEAN NOT NULL DEFAULT TRUE)""")
            cur.execute("""CREATE TABLE IF NOT EXISTS public.configuracion_web(clave VARCHAR(100) PRIMARY KEY,valor TEXT)""")
            cur.execute("""CREATE TABLE IF NOT EXISTS public.citas(id SERIAL PRIMARY KEY,cliente VARCHAR(150) NOT NULL,telefono VARCHAR(50) NOT NULL,servicio VARCHAR(150) NOT NULL,precio NUMERIC(10,2) NOT NULL DEFAULT 0,fecha DATE NOT NULL,hora TIME NOT NULL,pagada BOOLEAN NOT NULL DEFAULT FALSE)""")
            cur.execute("""CREATE TABLE IF NOT EXISTS public.productos(id SERIAL PRIMARY KEY,nombre VARCHAR(150) NOT NULL,precio NUMERIC(10,2) NOT NULL DEFAULT 0,activo BOOLEAN NOT NULL DEFAULT TRUE)""")
            cur.execute("""CREATE TABLE IF NOT EXISTS public.seguridad(id SMALLINT PRIMARY KEY CHECK(id=1),salt VARCHAR(64) NOT NULL,pin_hash VARCHAR(128) NOT NULL,actualizado TIMESTAMPTZ NOT NULL DEFAULT NOW())""")
            cur.execute("""SELECT fecha,hora,COUNT(*) FROM public.citas GROUP BY fecha,hora HAVING COUNT(*)>1 LIMIT 1""")
            if cur.fetchone(): raise RuntimeError("Existen citas duplicadas por fecha y hora; resuélvelas antes de activar el índice.")
            cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_citas_fecha_hora ON public.citas(fecha,hora)")
            cur.execute("""INSERT INTO public.servicios(nombre,precio,activo) VALUES('Corte de caballero',12,TRUE),('Corte infantil',9,TRUE),('Arreglo de barba',7,TRUE),('Corte + barba',17,TRUE) ON CONFLICT(nombre) DO NOTHING""")
            defaults={"nombre":"PELUQUERÍA","eslogan":"TU ESTILO, NUESTRA PASIÓN","descripcion":"Cuidamos cada detalle para que salgas con tu mejor imagen.","direccion":"","telefono":"","whatsapp":"","horario":"Lunes a viernes: 09:00 - 14:00 y 16:00 - 20:00","logo":"","foto_portada":"https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=1800&q=85","galeria":"","sobre_nosotros":"Somos una peluquería dedicada al cuidado de tu imagen."}
            for k,v in defaults.items():cur.execute("INSERT INTO public.configuracion_web(clave,valor) VALUES(%s,%s) ON CONFLICT(clave) DO NOTHING",(k,v))
            cur.execute("SELECT id FROM public.seguridad WHERE id=1")
            if not cur.fetchone():
                pin=str(st.secrets.get("OWNER_PIN","1234")).strip()
                salt=secrets.token_bytes(16); hashed=hashlib.pbkdf2_hmac("sha256",pin.encode(),salt,600_000)
                cur.execute("INSERT INTO public.seguridad(id,salt,pin_hash) VALUES(1,%s,%s)",(salt.hex(),hashed.hex()))
        con.commit()
    except Exception:con.rollback();raise
    finally:con.close()

def obtener_configuracion():
    return {r["clave"]:r["valor"] or "" for r in consultar("SELECT clave,valor FROM public.configuracion_web")}

def guardar_configuracion(k,v):
    ejecutar("INSERT INTO public.configuracion_web(clave,valor) VALUES(%s,%s) ON CONFLICT(clave) DO UPDATE SET valor=EXCLUDED.valor",(k,str(v)))

def obtener_servicios(activos=False):
    return consultar("SELECT id,nombre,precio,activo FROM public.servicios "+("WHERE activo=TRUE " if activos else "")+"ORDER BY nombre")

def obtener_productos(activos=False):
    return consultar("SELECT id,nombre,precio,activo FROM public.productos "+("WHERE activo=TRUE " if activos else "")+"ORDER BY nombre")

# ---------------------- SCHEDULING ----------------------
def generar_horarios():
    slots=[]
    for start,end in [(9*60,14*60),(16*60,20*60)]:
        for m in range(start,end,30):slots.append(time(m//60,m%60).strftime("%H:%M"))
    return slots

def hora_texto(v):return v.strftime("%H:%M") if hasattr(v,"strftime") else str(v)[:5]

def obtener_horas_ocupadas(fecha_sel):
    return [hora_texto(r["hora"]) for r in consultar("SELECT hora FROM public.citas WHERE fecha=%s",(fecha_sel,))]

def horarios_disponibles(fecha_sel):
    busy=obtener_horas_ocupadas(fecha_sel); now=datetime.now().strftime("%H:%M")
    return [h for h in generar_horarios() if h not in busy and (fecha_sel!=date.today() or h>now)]

def reservar_cita(cliente,telefono,servicio,precio,fecha_reserva,hora_reserva):
    con=conectar_db()
    try:
        with con.cursor() as cur:
            cur.execute("""INSERT INTO public.citas(cliente,telefono,servicio,precio,fecha,hora,pagada)
            VALUES(%s,%s,%s,%s,%s,%s,FALSE) ON CONFLICT(fecha,hora) DO NOTHING RETURNING id""",
            (cliente,telefono,servicio,precio,fecha_reserva,hora_reserva))
            saved=cur.fetchone()
        con.commit();return saved is not None
    except Exception:con.rollback();raise
    finally:con.close()

# ---------------------- SESSION ----------------------
for k,v in {"pagina":"Inicio","admin_autenticado":False,"mensaje_pin":"","login_intentos":0}.items():
    if k not in st.session_state:st.session_state[k]=v

def ir_a(p):
    st.session_state.pagina=p;st.rerun()

# ---------------------- COMMON UI ----------------------
def mostrar_encabezado(config):
    name=escape(config.get("nombre","PELUQUERÍA"))
    c1,c2=st.columns([1,3])
    with c1:
        if config.get("logo","").strip():
            try:st.image(config["logo"],width=130)
            except:st.markdown(f"## ✂️ {name}")
        else:st.markdown(f"## ✂️ {name}")
    with c2:st.markdown(f"<div style='text-align:right;padding-top:18px;color:#dfcca5;font-weight:700;letter-spacing:2px'>{name.upper()}</div>",unsafe_allow_html=True)
    st.markdown("<hr>",unsafe_allow_html=True)
    pages=[("Inicio","⌂ Inicio"),("Servicios","✂ Servicios"),("Reservar","📅 Reservar"),("Galería","📸 Galería"),("Contacto","📍 Contacto"),("Propietario","🔐 Propietario")]
    cols=st.columns(6,gap="small")
    for col,(p,label) in zip(cols,pages):
        with col:
            if st.button(label,key="nav_"+p,use_container_width=True):ir_a(p)

def mostrar_footer(config):
    st.markdown(f"<div class='footer'><strong>{escape(config.get('nombre','PELUQUERÍA'))}</strong><br><br>Peluquería · Barbería<br><span class='small-text'>© {datetime.now().year} Todos los derechos reservados</span></div>",unsafe_allow_html=True)

def section(title,subtitle=""):
    st.markdown(f"<div class='section-title'><h2>{escape(title)}</h2><div class='gold-line'></div><p>{escape(subtitle)}</p></div>",unsafe_allow_html=True)

# ---------------------- PUBLIC PAGES ----------------------
def pagina_inicio(config):
    name=escape(config.get("nombre","PELUQUERÍA")); slogan=escape(config.get("eslogan","TU ESTILO, NUESTRA PASIÓN")); desc=escape(config.get("descripcion","Cuidamos cada detalle."))
    photo=escape(config.get("foto_portada","").strip() or "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=1800&q=85",quote=True)
    logo=config.get("logo","").strip()
    logo_html=f"<img class='hero-logo' src='{escape(logo,quote=True)}' alt='Logo'>" if logo else ""
    html=f"<div class='hero' style=\"background-image:url('{photo}')\"><div class='hero-content'>{logo_html}<div class='hero-label'>{name}</div><h1>{slogan}</h1><div class='gold-line'></div><p>{desc}</p></div></div>"
    if callable(getattr(st,"html",None)):st.html(html)
    else:st.markdown(html,unsafe_allow_html=True)
    mid=st.columns([1,2,1])
    with mid[1]:
        if st.button("📅 RESERVAR MI CITA",use_container_width=True,key="home_book"):ir_a("Reservar")
    section("BIENVENIDO","Profesionalidad, estilo y atención personalizada.")
    cols=st.columns(3)
    for col,(title,txt) in zip(cols,[("✂️ Estilo","Cuidamos cada corte y nos adaptamos a tu personalidad."),("⭐ Profesionalidad","Atención cercana y servicio profesional."),("📅 Reserva online","Reserva cómodamente desde cualquier dispositivo.")]):
        with col:st.markdown(f"<div class='info-card'><h3>{title}</h3><p>{txt}</p></div>",unsafe_allow_html=True)
    section("NUESTROS SERVICIOS","Descubre nuestros cortes y tratamientos.")
    services=obtener_servicios(True)
    if services:
        cols=st.columns(min(3,len(services)))
        for i,s in enumerate(services):
            with cols[i%len(cols)]:st.markdown(f"<div class='info-card'><h3>{escape(s['nombre'])}</h3><h2>{euros(s['precio'])}</h2></div>",unsafe_allow_html=True)
    else:st.info("Próximamente publicaremos nuestros servicios.")
    if st.button("VER TODOS LOS SERVICIOS",use_container_width=True,key="home_services"):ir_a("Servicios")

def pagina_servicios():
    section("NUESTROS SERVICIOS Y TARIFAS","Elige el servicio que mejor se adapta a ti.")
    services=obtener_servicios(True)
    if not services:st.info("No hay servicios publicados.");return
    cols=st.columns(3)
    for i,s in enumerate(services):
        with cols[i%3]:st.markdown(f"<div class='info-card'><h3>✂️ {escape(s['nombre'])}</h3><h2>{euros(s['precio'])}</h2><p class='small-text'>Disponible bajo reserva.</p></div>",unsafe_allow_html=True)
    if st.button("📅 RESERVAR CITA",use_container_width=True):ir_a("Reservar")

def pagina_reservar():
    section("RESERVA TU CITA","Reserva tu próximo corte de forma rápida y sencilla.")
    services=obtener_servicios(True)
    if not services:st.warning("No hay servicios disponibles.");return
    client=st.text_input("Nombre y apellidos",placeholder="Escribe tu nombre",key="book_name")
    phone=st.text_input("Teléfono",placeholder="Tu número de teléfono",key="book_phone")
    selected=st.selectbox("Servicio",services,format_func=lambda s:s["nombre"],key="book_service")
    st.markdown(f"<h3 style='text-align:center'>Precio: {euros(selected['precio'])}</h3>",unsafe_allow_html=True)
    day=st.date_input("Día",min_value=date.today(),value=date.today(),key="book_day")
    available=horarios_disponibles(day)
    hour=st.selectbox("Hora disponible",available,index=None,placeholder="Selecciona una hora",key=f"book_hour_{day.isoformat()}") if available else None
    if not available:st.warning("No quedan horarios disponibles.")
    consent=st.checkbox("He leído y acepto la política de privacidad.",key="book_privacy")
    if st.button("CONFIRMAR MI RESERVA",use_container_width=True,key="book_submit"):
        if not client.strip():st.error("Introduce tu nombre.")
        elif not phone.strip():st.error("Introduce tu teléfono.")
        elif not consent:st.error("Debes aceptar la política de privacidad.")
        elif not hour:st.error("Selecciona una hora.")
        elif hour not in horarios_disponibles(day):st.error("La hora acaba de ocuparse. Selecciona otra.")
        else:
            try:
                ok=reservar_cita(client.strip(),phone.strip(),selected["nombre"],selected["precio"],day,hour)
                if not ok:st.error("Ese horario acaba de reservarse. Prueba otro.");st.rerun()
                else:
                    st.success("¡Cita reservada correctamente!")
                    st.markdown(f"<div class='info-card'><h2 style='text-align:center'>RESERVA CONFIRMADA</h2><div class='gold-line'></div><p><b>Cliente:</b> {escape(client)}</p><p><b>Servicio:</b> {escape(selected['nombre'])}</p><p><b>Fecha:</b> {day.strftime('%d/%m/%Y')}</p><p><b>Hora:</b> {escape(hour)}</p><h2 style='text-align:center'>{euros(selected['precio'])}</h2></div>",unsafe_allow_html=True)
            except Exception:st.error("No se pudo guardar la reserva. Comprueba la conexión e inténtalo de nuevo.")

def pagina_galeria(config):
    section("NUESTRA GALERÍA","Conoce nuestro espacio y algunos de nuestros trabajos.")
    urls=[u.strip() for u in config.get("galeria","").splitlines() if u.strip().startswith(("https://","http://"))]
    if urls:
        cols=st.columns(2)
        for i,u in enumerate(urls):
            with cols[i%2]:st.image(u,use_container_width=True)
    else:
        st.info("Próximamente publicaremos fotografías.")
        st.image("https://images.unsplash.com/photo-1503951914875-452162b0f3f1?auto=format&fit=crop&w=1400&q=85",use_container_width=True)

def pagina_contacto(config):
    section("CONTACTO","Estamos aquí para atenderte.")
    c1,c2=st.columns(2)
    with c1:
        st.markdown(f"<div class='info-card'><h3>📍 Ubicación</h3><p>{escape(config.get('direccion','').strip() or 'Dirección pendiente')}</p><h3>🕒 Horarios</h3><p>{escape(config.get('horario','').strip() or 'Horario pendiente')}</p></div>",unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='info-card'><h3>📞 Teléfono</h3><p>{escape(config.get('telefono','').strip() or 'Teléfono pendiente')}</p></div>",unsafe_allow_html=True)
        whatsapp=re.sub(r"\D","",config.get("whatsapp",""))
        if whatsapp:st.link_button("💬 CONTACTAR POR WHATSAPP",f"https://wa.me/{whatsapp}",use_container_width=True)
    if st.button("📅 RESERVAR CITA",use_container_width=True):ir_a("Reservar")

# ---------------------- ADMIN ----------------------
def panel_cambiar_pin():
    with st.expander("🔐 Cambiar PIN"):
        with st.form("change_pin"):
            old=st.text_input("PIN actual",type="password")
            new=st.text_input("Nuevo PIN (4–12 cifras)",type="password")
            confirm=st.text_input("Confirmar nuevo PIN",type="password")
            submit=st.form_submit_button("GUARDAR PIN",use_container_width=True)
        if submit:
            if not verificar_pin(old):st.error("PIN actual incorrecto.")
            elif not new.isdigit() or not 4<=len(new)<=12:st.error("El PIN debe tener de 4 a 12 cifras.")
            elif new!=confirm:st.error("La confirmación no coincide.")
            elif new==old:st.error("El nuevo PIN debe ser distinto.")
            else:
                guardar_nuevo_pin(new);st.session_state.admin_autenticado=False
                st.session_state.mensaje_pin="PIN actualizado. Inicia sesión de nuevo.";st.rerun()

def pagina_propietario():
    if not st.session_state.admin_autenticado:
        if st.session_state.mensaje_pin:st.success(st.session_state.mensaje_pin);st.session_state.mensaje_pin=""
        section("ACCESO DE PROPIETARIO","Introduce tu PIN para acceder al panel.")
        with st.form("admin_login"):
            pin=st.text_input("PIN de acceso",type="password")
            submit=st.form_submit_button("ENTRAR AL PANEL",use_container_width=True)
        if submit:
            if st.session_state.login_intentos>=5:st.error("Demasiados intentos. Recarga la sesión más tarde.")
            elif verificar_pin(pin):st.session_state.admin_autenticado=True;st.session_state.login_intentos=0;st.rerun()
            else:st.session_state.login_intentos+=1;st.error("PIN incorrecto.")
        return
    section("PANEL DE ADMINISTRACIÓN","Gestiona tu peluquería desde un único lugar.")
    if st.button("CERRAR SESIÓN",key="admin_logout"):st.session_state.admin_autenticado=False;st.rerun()
    tabs=st.tabs(["📊 Resumen","📅 Citas","💰 Caja","✂️ Servicios","🧴 Productos","🌐 Web"])
    with tabs[0]:panel_resumen()
    with tabs[1]:panel_citas()
    with tabs[2]:panel_caja()
    with tabs[3]:panel_servicios()
    with tabs[4]:panel_productos()
    with tabs[5]:panel_web()
    panel_cambiar_pin()

def panel_resumen():
    today=date.today()
    rows=consultar("SELECT precio,pagada FROM public.citas WHERE fecha=%s",(today,))
    paid=sum((Decimal(str(x["precio"])) for x in rows if x["pagada"]),Decimal("0"))
    due=sum((Decimal(str(x["precio"])) for x in rows if not x["pagada"]),Decimal("0"))
    cols=st.columns(4)
    cols[0].metric("Citas de hoy",len(rows));cols[1].metric("Cobrado hoy",euros(paid));cols[2].metric("Pendiente",euros(due));cols[3].metric("Servicios activos",len(obtener_servicios(True)))
    st.markdown("### Próximas citas")
    nexts=consultar("SELECT id,cliente,telefono,servicio,precio,fecha,hora,pagada FROM public.citas WHERE fecha >= %s ORDER BY fecha,hora LIMIT 8",(today,))
    if not nexts:st.info("No hay próximas citas.")
    for x in nexts:
        with st.container(border=True):
            a,b,c=st.columns([2,3,1])
            a.markdown(f"### {x['fecha'].strftime('%d/%m')} · {hora_texto(x['hora'])}")
            b.write(f"**{x['cliente']}** · {x['servicio']} · {euros(x['precio'])}")
            c.success("Pagada") if x["pagada"] else c.warning("Pendiente")

def panel_citas():
    st.subheader("Agenda de citas")
    day=st.date_input("Día de agenda",value=date.today(),key="admin_appointments_day")
    rows=consultar("SELECT id,cliente,telefono,servicio,precio,fecha,hora,pagada FROM public.citas WHERE fecha=%s ORDER BY hora",(day,))
    paid=sum((Decimal(str(x["precio"])) for x in rows if x["pagada"]),Decimal("0"))
    due=sum((Decimal(str(x["precio"])) for x in rows if not x["pagada"]),Decimal("0"))
    a,b,c=st.columns(3);a.metric("Citas",len(rows));b.metric("Cobrado",euros(paid));c.metric("Pendiente",euros(due))
    if not rows:st.info("No hay citas para este día.")
    for x in rows:
        with st.container(border=True):
            a,b,c=st.columns([2,2,1])
            a.markdown(f"### {hora_texto(x['hora'])}");a.write(f"**{x['cliente']}**");a.write(x["telefono"])
            b.write(x["servicio"]);b.write(euros(x["precio"]))
            if x["pagada"]:b.success("PAGADA")
            else:
                b.warning("PENDIENTE")
                if c.button("COBRAR",key=f"pay_{x['id']}",use_container_width=True):
                    ejecutar("UPDATE public.citas SET pagada=TRUE WHERE id=%s",(x["id"],));st.rerun()

def panel_caja():
    st.subheader("Caja y facturación")
    today=date.today()
    month=st.selectbox("Mes",range(1,13),index=today.month-1,format_func=lambda m:["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"][m-1])
    year=st.number_input("Año",min_value=2024,max_value=2100,value=today.year,step=1)
    start=date(int(year),month,1);end=date(int(year)+1,1,1) if month==12 else date(int(year),month+1,1)
    rows=consultar("SELECT id,cliente,telefono,servicio,precio,fecha,hora,pagada FROM public.citas WHERE fecha >= %s AND fecha < %s ORDER BY fecha DESC,hora DESC",(start,end))
    paid=sum((Decimal(str(x["precio"])) for x in rows if x["pagada"]),Decimal("0"));due=sum((Decimal(str(x["precio"])) for x in rows if not x["pagada"]),Decimal("0"))
    a,b,c=st.columns(3);a.metric("Cobrado",euros(paid));b.metric("Pendiente",euros(due));c.metric("Citas",len(rows))
    st.markdown("### Histórico")
    for x in rows:
        with st.container(border=True):
            a,b,c=st.columns([2,2,1]);a.write(f"**{x['cliente']}**");a.write(x["fecha"].strftime("%d/%m/%Y")+" · "+hora_texto(x["hora"]))
            b.write(x["servicio"]);b.write(euros(x["precio"]))
            if x["pagada"]:c.success("PAGADA")
            elif c.button("COBRAR",key=f"histpay_{x['id']}"):ejecutar("UPDATE public.citas SET pagada=TRUE WHERE id=%s",(x["id"],));st.rerun()

def panel_servicios():
    st.subheader("Servicios y tarifas")
    with st.expander("➕ Añadir servicio"):
        with st.form("add_service"):
            name=st.text_input("Nombre");price=st.number_input("Precio (€)",min_value=0.0,value=12.0,step=.5)
            submit=st.form_submit_button("CREAR SERVICIO")
        if submit:
            if not name.strip():st.error("Escribe un nombre.")
            else:
                try:ejecutar("INSERT INTO public.servicios(nombre,precio,activo) VALUES(%s,%s,TRUE)",(name.strip(),price));st.success("Servicio creado.");st.rerun()
                except psycopg2.IntegrityError:st.error("Ya existe un servicio con ese nombre.")
    rows=obtener_servicios()
    if not rows:st.info("No hay servicios.");return
    mapping={f"{x['nombre']} · {euros(x['precio'])}":x["id"] for x in rows}
    choice=st.selectbox("Editar servicio",list(mapping),key="service_choice");item=next(x for x in rows if x["id"]==mapping[choice])
    with st.form("edit_service"):
        name=st.text_input("Nombre",value=item["nombre"]);price=st.number_input("Precio",min_value=0.0,value=float(item["precio"]),step=.5);active=st.checkbox("Visible en reservas",value=item["activo"]);save=st.form_submit_button("GUARDAR CAMBIOS")
    if save:
        try:ejecutar("UPDATE public.servicios SET nombre=%s,precio=%s,activo=%s WHERE id=%s",(name.strip(),price,active,item["id"]));st.success("Actualizado.");st.rerun()
        except psycopg2.IntegrityError:st.error("Nombre duplicado.")
    if st.button("🗑️ Eliminar servicio",key="delete_service"):
        ejecutar("DELETE FROM public.servicios WHERE id=%s",(item["id"],));st.rerun()

def panel_productos():
    st.subheader("Productos")
    with st.expander("➕ Añadir producto"):
        with st.form("add_product"):
            name=st.text_input("Nombre producto");price=st.number_input("Precio (€)",min_value=0.0,value=10.0,step=.5);submit=st.form_submit_button("AÑADIR")
        if submit:
            if not name.strip():st.error("Escribe un nombre.")
            else:ejecutar("INSERT INTO public.productos(nombre,precio,activo) VALUES(%s,%s,TRUE)",(name.strip(),price));st.rerun()
    rows=obtener_productos()
    if not rows:st.info("No hay productos.");return
    mapping={f"{x['nombre']} · {euros(x['precio'])}":x["id"] for x in rows}
    choice=st.selectbox("Editar producto",list(mapping),key="product_choice");item=next(x for x in rows if x["id"]==mapping[choice])
    with st.form("edit_product"):
        name=st.text_input("Nombre",value=item["nombre"]);price=st.number_input("Precio",min_value=0.0,value=float(item["precio"]),step=.5);active=st.checkbox("Producto activo",value=item["activo"]);save=st.form_submit_button("GUARDAR")
    if save:ejecutar("UPDATE public.productos SET nombre=%s,precio=%s,activo=%s WHERE id=%s",(name.strip(),price,active,item["id"]));st.rerun()
    if st.button("🗑️ Eliminar producto",key="delete_product"):ejecutar("DELETE FROM public.productos WHERE id=%s",(item["id"],));st.rerun()

def panel_web():
    st.subheader("Personalización de la web")
    cfg=obtener_configuracion()
    with st.form("web_config"):
        name=st.text_input("Nombre",value=cfg.get("nombre",""));slogan=st.text_input("Eslogan",value=cfg.get("eslogan",""));desc=st.text_area("Descripción",value=cfg.get("descripcion",""));about=st.text_area("Sobre nosotros",value=cfg.get("sobre_nosotros",""))
        st.markdown("### Imagen e identidad")
        logo=st.text_input("URL logotipo",value=cfg.get("logo",""));cover=st.text_input("URL portada",value=cfg.get("foto_portada",""));gallery=st.text_area("URLs galería (una por línea)",value=cfg.get("galeria",""))
        st.markdown("### Contacto")
        address=st.text_input("Dirección",value=cfg.get("direccion",""));phone=st.text_input("Teléfono",value=cfg.get("telefono",""));wa=st.text_input("WhatsApp internacional",value=cfg.get("whatsapp",""));hours=st.text_area("Horario",value=cfg.get("horario",""))
        save=st.form_submit_button("GUARDAR CONFIGURACIÓN",use_container_width=True)
    if save:
        values={"nombre":name,"eslogan":slogan,"descripcion":desc,"sobre_nosotros":about,"logo":logo,"foto_portada":cover,"galeria":gallery,"direccion":address,"telefono":phone,"whatsapp":wa,"horario":hours}
        for k,v in values.items():guardar_configuracion(k,v)
        st.success("Configuración guardada.");st.rerun()
    if cfg.get("logo","").strip():
        st.markdown("### Vista previa");st.image(cfg["logo"],width=160)

# ---------------------- MAIN ----------------------
try:
    inicializar_base_datos()
    config=obtener_configuracion()
    mostrar_encabezado(config)
    page=st.session_state.pagina
    if page=="Inicio":pagina_inicio(config)
    elif page=="Servicios":pagina_servicios()
    elif page=="Reservar":pagina_reservar()
    elif page=="Galería":pagina_galeria(config)
    elif page=="Contacto":pagina_contacto(config)
    elif page=="Propietario":pagina_propietario()
    mostrar_footer(config)
except Exception:
    st.error("No se ha podido cargar la aplicación.")
    st.info("Comprueba la conexión con Supabase y las variables configuradas en Secrets.")
