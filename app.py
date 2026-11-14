import streamlit as st

# =========================================================
# CONFIGURACIÓN DE LA PÁGINA
# =========================================================
st.set_page_config(
    page_title="Aplicación - Estilo Minimalista",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# ESTILOS CSS: NEGRO, GRIS Y BLANCO PURO
# =========================================================
st.markdown("""
<style>
    :root {
        --carbon: #0a0a0a;
        --anthracite: #121212;
        --surface: #1a1a1a;
        --surface-soft: #262626;
        --champagne: #ffffff;       
        --champagne-light: #e0e0e0; 
        --cream: #ffffff;
        --muted: #8c8c8c;
        --line: rgba(255, 255, 255, 0.12);
    }

    .stApp {
        background:
            radial-gradient(ellipse at 50% -10%, rgba(255,255,255,.04), transparent 45%),
            #0a0a0a;
    }

    h1, h2, h3, h4 {
        color: #ffffff !important;
    }

    a {
        color: #ffffff !important;
        text-decoration: underline;
    }

    .stButton > button,
    .stLinkButton > a,
    div[data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #ffffff, #d1d1d1);
        color: #0a0a0a !important;
        border: 1px solid #ffffff;
        border-radius: 6px;
        font-weight: 700;
        letter-spacing: .045em;
        transition: all 0.2s ease;
    }

    .stButton > button:hover,
    .stLinkButton > a:hover,
    div[data-testid="stFormSubmitButton"] button:hover {
        background: linear-gradient(135deg, #e0e0e0, #b5b5b5);
        color: #000 !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255,255,255,.15);
    }

    div[data-testid="stForm"],
    .info-card,
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #161616, #0e0e0e);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        box-shadow: 0 12px 30px rgba(0,0,0,.40);
    }

    .info-card {
        padding: 26px;
    }

    .info-card h3 {
        color: #ffffff !important;
    }

    .hero {
        min-height: 520px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 10px;
        box-shadow: 0 25px 65px rgba(0,0,0,.6);
        padding: 50px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        background: linear-gradient(180deg, rgba(10,10,10,.25), rgba(10,10,10,.85));
    }

    .hero-label {
        color: #b0b0b0;
        letter-spacing: .38em;
        text-transform: uppercase;
        font-size: 13px;
        margin-bottom: 10px;
    }

    .hero h1 {
        color: #ffffff !important;
        text-shadow: 0 4px 25px rgba(0,0,0,.8);
        font-size: clamp(32px, 4vw, 52px);
    }

    .section-title h2 {
        color: #ffffff !important;
    }

    .gold-line {
        background: linear-gradient(90deg, transparent, #ffffff, transparent);
        width: 75px;
        height: 2px;
        margin: 15px auto;
    }

    .home-intro {
        text-align: center;
        max-width: 780px;
        margin: 50px auto 35px;
    }

    .home-intro h2 {
        color: #ffffff !important;
        font-size: clamp(25px, 3vw, 36px);
        letter-spacing: .04em;
    }

    .home-intro p {
        color: #9e9e9e;
        line-height: 1.9;
    }

    .home-feature {
        background: linear-gradient(145deg, #161616, #0e0e0e);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 28px 22px;
        min-height: 190px;
        text-align: center;
        transition: border-color 0.2s ease;
    }

    .home-feature:hover {
        border-color: rgba(255, 255, 255, 0.25);
    }

    .home-feature .feature-icon {
        font-size: 30px;
        margin-bottom: 15px;
    }

    .home-feature h3 {
        color: #ffffff !important;
        font-size: 19px;
        margin-bottom: 10px;
    }

    .home-feature p {
        color: #9e9e9e;
        font-size: 14px;
        line-height: 1.7;
    }

    .home-service {
        background: linear-gradient(145deg, #181818, #0f0f0f);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 9px;
        padding: 24px;
        margin-bottom: 16px;
        text-align: center;
        transition: border-color 0.2s ease;
    }

    .home-service:hover {
        border-color: rgba(255, 255, 255, 0.22);
    }

    .home-service h3 {
        color: #ffffff !important;
        font-size: 18px;
        min-height: 48px;
    }

    .home-service .service-price {
        color: #ffffff;
        font-size: 27px;
        font-weight: 700;
        margin-top: 12px;
    }

    .home-service .service-caption {
        color: #8c8c8c;
        font-size: 12px;
        margin-top: 8px;
    }

    .home-cta {
        background: linear-gradient(135deg, #161616, #0e0e0e);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 10px;
        padding: 35px 25px;
        text-align: center;
        margin-top: 45px;
    }

    .home-cta h2 {
        color: #ffffff !important;
    }

    .home-cta p {
        color: #b0b0b0;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# CONTENIDO DE LA PANTALLA PRINCIPAL
# =========================================================

# 1. Sección Hero
st.markdown("""
<div class="hero">
    <div class="hero-label">Exclusividad & Diseño</div>
    <h1>Minimalismo en Negro y Blanco</h1>
    <div class="gold-line" style="margin: 15px 0;"></div>
    <p style="color: #b0b0b0; font-size: 16px; max-width: 600px; line-height: 1.6;">
        Una interfaz limpia, moderna y sofisticada diseñada para ofrecer la máxima elegancia y legibilidad en tus aplicaciones de Streamlit.
    </p>
</div>
""", unsafe_allow_html=True)

st.write("")
st.write("")

# 2. Introducción Principal
st.markdown("""
<div class="home-intro">
    <h2>Estructura de Alta Gama</h2>
    <div class="gold-line"></div>
    <p>Cada componente ha sido optimizado con contrastes precisos, degradados sutiles y transiciones fluidas para una experiencia de usuario impecable.</p>
</div>
""", unsafe_allow_html=True)

# 3. Características (Grid de 3 columnas)
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="home-feature">
        <div class="feature-icon">⬛</div>
        <h3>Estética Oscura</h3>
        <p>Tonos negros profundos y grises calibrados que reducen la fatiga visual y realzan el contenido.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="home-feature">
        <div class="feature-icon">✨</div>
        <h3>Blanco Puro</h3>
        <p>Tipografías y acentos principales en blanco absoluto para lograr un contraste limpio y sofisticado.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="home-feature">
        <div class="feature-icon">⚡</div>
        <h3>Alto Rendimiento</h3>
        <p>Diseño responsivo optimizado para adaptarse de forma fluida a ordenadores y dispositivos móviles.</p>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.write("")

# 4. Sección de Servicios / Planes
st.markdown("""
<div class="section-title" style="text-align: center; margin-bottom: 30px;">
    <h2>Planes y Opciones</h2>
    <div class="gold-line"></div>
</div>
""", unsafe_allow_html=True)

scol1, scol2 = st.columns(2)

with scol1:
    st.markdown("""
    <div class="home-service">
        <h3>Plan Esencial</h3>
        <div class="service-price">0 €</div>
        <div class="service-caption">Ideal para pruebas y proyectos personales</div>
        <br>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Seleccionar Esencial", use_container_width=True):
        st.success("¡Has seleccionado el plan Esencial!")

with scol2:
    st.markdown("""
    <div class="home-service">
        <h3>Plan Pro</h3>
        <div class="service-price">29 €</div>
        <div class="service-caption">Para desarrolladores y proyectos avanzados</div>
        <br>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Seleccionar Pro", use_container_width=True):
        st.success("¡Has seleccionado el plan Pro!")

# 5. Call to Action (CTA) Final
st.markdown("""
<div class="home-cta">
    <h2>¿Listo para comenzar?</h2>
    <p>Integra este diseño en tu aplicación actual y lleva su interfaz al siguiente nivel.</p>
</div>
""", unsafe_allow_html=True)
