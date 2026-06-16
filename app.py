import streamlit as st
import sqlite3
from datetime import date, time, datetime, timezone, timedelta
from modelo import predecir_partido, monte_carlo, obtener_rating_once

BANDERAS = {
    "Argentina": "ar", "España": "es", "Francia": "fr", "Inglaterra": "gb-eng",
    "Portugal": "pt", "Brasil": "br", "Marruecos": "ma", "Países Bajos": "nl",
    "Bélgica": "be", "Croacia": "hr", "Alemania": "de", "Uruguay": "uy",
    "Colombia": "co", "México": "mx", "Estados Unidos": "us", "Suecia": "se",
    "Japón": "jp", "Suiza": "ch", "Irán": "ir", "Turquía": "tr",
    "Ecuador": "ec", "Austria": "at", "Corea del Sur": "kr", "Senegal": "sn",
    "Noruega": "no", "Argelia": "dz", "Egipto": "eg", "Costa de Marfil": "ci",
    "República Checa": "cz", "Escocia": "gb-sct", "Panamá": "pa",
    "Paraguay": "py", "Sudáfrica": "za", "Túnez": "tn", "Arabia Saudí": "sa",
    "Ghana": "gh", "Cabo Verde": "cv", "Uzbekistán": "uz",
    "Bosnia y Herzegovina": "ba", "Jordania": "jo", "Irak": "iq",
    "Rep. Dem. del Congo": "cd", "Haití": "ht", "Catar": "qa",
    "Curazao": "cw", "Canadá": "ca", "Australia": "au", "Nueva Zelanda": "nz",
}

# UTC offset de cada sede y Colombia (UTC-5)
SEDES = {
    "— Estados Unidos —": None,
    "New York / New Jersey": {"ciudad": "New York", "utc": -4},
    "Los Angeles": {"ciudad": "Los Angeles", "utc": -7},
    "Dallas": {"ciudad": "Dallas", "utc": -5},
    "San Francisco": {"ciudad": "San Francisco", "utc": -7},
    "Miami": {"ciudad": "Miami", "utc": -4},
    "Seattle": {"ciudad": "Seattle", "utc": -7},
    "Boston": {"ciudad": "Boston", "utc": -4},
    "Kansas City": {"ciudad": "Kansas City", "utc": -5},
    "Philadelphia": {"ciudad": "Philadelphia", "utc": -4},
    "Atlanta": {"ciudad": "Atlanta", "utc": -4},
    "Houston": {"ciudad": "Houston", "utc": -5},
    "— México —": None,
    "Ciudad de México": {"ciudad": "Mexico City", "utc": -6},
    "Guadalajara": {"ciudad": "Guadalajara", "utc": -6},
    "Monterrey": {"ciudad": "Monterrey", "utc": -6},
    "— Canadá —": None,
    "Toronto": {"ciudad": "Toronto", "utc": -4},
    "Vancouver": {"ciudad": "Vancouver", "utc": -7},
}

COLORES_POS = {
    "Portero":       {"dot": "#EF9F27", "line": "#EF9F2733", "label": "#EF9F27", "rating": "#EF9F2799"},
    "Defensa":       {"dot": "#378ADD", "line": "#378ADD33", "label": "#378ADD", "rating": "#378ADD99"},
    "Mediocampista": {"dot": "#1D9E75", "line": "#1D9E7533", "label": "#1D9E75", "rating": "#1D9E7599"},
    "Delantero":     {"dot": "#D85A30", "line": "#D85A3033", "label": "#D85A30", "rating": "#D85A3099"},
}

def get_bandera_url(equipo):
    codigo = BANDERAS.get(equipo, "un")
    return f"https://flagcdn.com/48x36/{codigo}.png"

def get_equipos():
    conn = sqlite3.connect("mundial2026.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT equipo FROM jugadores ORDER BY equipo")
    equipos = [row[0] for row in cursor.fetchall()]
    conn.close()
    return equipos

def get_jugadores(equipo):
    conn = sqlite3.connect("mundial2026.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT nombre, posicion, rating FROM jugadores
        WHERE equipo = ?
        ORDER BY
            CASE posicion
                WHEN 'Portero' THEN 1
                WHEN 'Defensa' THEN 2
                WHEN 'Mediocampista' THEN 3
                WHEN 'Delantero' THEN 4
                ELSE 5
            END, rating DESC
    ''', (equipo,))
    jugadores = cursor.fetchall()
    conn.close()
    return jugadores

def convertir_hora(fecha, hora_col, utc_sede):
    colombia_utc = -5
    diferencia = utc_sede - colombia_utc
    dt_col = datetime.combine(fecha, hora_col)
    dt_sede = dt_col + timedelta(hours=diferencia)
    return dt_sede.strftime("%Y-%m-%d %H:%M"), dt_sede.strftime("%H:%M")

st.set_page_config(
    page_title="Predictor Mundial 2026",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
body, .stApp { background-color: #080808 !important; }
.titulo {
    font-size: 2rem; font-weight: 900; text-align: center;
    letter-spacing: 0.2em; color: #c9a84c;
    margin-bottom: 0.2rem; padding-top: 1rem;
}
.subtitulo {
    font-size: 0.7rem; color: #444; text-align: center;
    letter-spacing: 0.18em; margin-bottom: 2rem; text-transform: uppercase;
}
.panel-label {
    font-size: 0.65rem; font-weight: 700; color: #c9a84c;
    letter-spacing: 0.15em; text-transform: uppercase;
    border-bottom: 0.5px solid #1f1f1f; padding-bottom: 8px; margin-bottom: 1rem;
}
.marcador-box {
    background: #0f0f0f; border: 0.5px solid #1f1f1f;
    border-radius: 8px; padding: 1rem; text-align: center;
}
.marcador-box-label { font-size: 0.65rem; color: #555; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 6px; }
.marcador-box-score { font-size: 1.8rem; font-weight: 700; color: #c9a84c; }
.marcador-principal {
    background: #0d0b00; border: 1px solid #c9a84c55;
    border-radius: 8px; padding: 1rem; text-align: center;
}
.marcador-principal-label { font-size: 0.65rem; color: #c9a84c; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 6px; }
.marcador-principal-score { font-size: 2.5rem; font-weight: 900; color: #f0cc6a; letter-spacing: 6px; }
.stButton > button {
    background: #c9a84c !important; color: #000 !important;
    font-weight: 800 !important; font-size: 0.8rem !important;
    letter-spacing: 0.2em !important; text-transform: uppercase !important;
    border: none !important; border-radius: 6px !important;
}
div[data-testid="stMetricValue"] { color: #c9a84c !important; }
div[data-testid="stMetricLabel"] { color: #555 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="titulo">PREDICTOR MUNDIAL 2026</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">Forma reciente · Ranking FIFA · Ratings · Clima · Monte Carlo 100K</div>', unsafe_allow_html=True)

equipos = get_equipos()
opciones_equipo = ["— Selecciona un equipo —"] + equipos

def render_equipo(key_prefix, label):
    st.markdown(f'<div class="panel-label">{label}</div>', unsafe_allow_html=True)
    equipo = st.selectbox("", opciones_equipo, key=f"{key_prefix}_eq", label_visibility="collapsed")

    if equipo == "— Selecciona un equipo —":
        st.caption("Selecciona un equipo para ver los jugadores.")
        return equipo, []

    try:
        st.image(get_bandera_url(equipo), width=48)
    except:
        pass

    jugadores = get_jugadores(equipo)
    titulares = []
    pos_actual = None

    for nombre, posicion, rating in jugadores:
        col = COLORES_POS.get(posicion, {"dot": "#555", "line": "#33333333", "label": "#555", "rating": "#55555599"})
        if posicion != pos_actual:
            pos_actual = posicion
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;margin-top:12px;margin-bottom:4px;">
                <div style="width:6px;height:6px;border-radius:50%;background:{col['dot']};flex-shrink:0;"></div>
                <span style="font-size:9px;font-weight:700;color:{col['label']};letter-spacing:0.14em;text-transform:uppercase;">{posicion}s</span>
                <div style="flex:1;height:0.5px;background:{col['line']};"></div>
            </div>
            """, unsafe_allow_html=True)
        checked = st.checkbox(f"{nombre}", key=f"{key_prefix}_{nombre}", help=f"Rating: {rating}")
        if checked:
            titulares.append(nombre)
        st.markdown(f'<div style="font-size:11px;color:{col["rating"]};margin-top:-12px;margin-bottom:4px;padding-left:22px;">{rating}</div>', unsafe_allow_html=True)

    n = len(titulares)
    if n == 11:
        rating_once = obtener_rating_once(equipo, titulares)
        st.success(f"{n}/11 seleccionados · Rating: {rating_once}")
    elif n > 0:
        st.warning(f"{n}/11 seleccionados")
    else:
        st.caption("Sin selección — promedio del plantel")

    return equipo, titulares

col1, col2 = st.columns(2, gap="large")
with col1:
    local, titulares_local = render_equipo("l", "Equipo local")
with col2:
    visitante, titulares_visit = render_equipo("v", "Equipo visitante")

st.divider()

col3, col4, col5 = st.columns(3)
with col3:
    sede_opciones = list(SEDES.keys())
    sede_sel = st.selectbox("Ciudad sede", sede_opciones,
        format_func=lambda x: x if SEDES[x] is not None else f"── {x} ──")
    sede_info = SEDES.get(sede_sel)
with col4:
    fecha = st.date_input("Fecha del partido (hora Colombia)")
with col5:
    hora = st.time_input("Hora del partido (hora Colombia)", value=time(20, 0))

if sede_info:
    fecha_hora_sede, hora_sede = convertir_hora(fecha, hora, sede_info["utc"])
    st.caption(f"Hora en {sede_sel}: {hora_sede} · Hora Colombia: {hora.strftime('%H:%M')}")
    ciudad = sede_info["ciudad"]
    fecha_hora = fecha_hora_sede
else:
    fecha_hora = f"{fecha} {hora.strftime('%H:%M')}"
    ciudad = None

st.markdown("<br>", unsafe_allow_html=True)
predecir = st.button("PREDECIR PARTIDO", type="primary", use_container_width=True)

if predecir:
    if local == "— Selecciona un equipo —" or visitante == "— Selecciona un equipo —":
        st.error("Selecciona ambos equipos.")
    elif local == visitante:
        st.error("Selecciona equipos diferentes.")
    elif sede_info is None:
        st.error("Selecciona una ciudad sede válida.")
    else:
        with st.spinner("Simulando 100.000 partidos..."):
            tl = titulares_local if len(titulares_local) == 11 else None
            tv = titulares_visit if len(titulares_visit) == 11 else None
            pred = predecir_partido(local, visitante, ciudad, fecha_hora, tl, tv)
            mc = monte_carlo(local, visitante, ciudad, fecha_hora, tl, tv)

        st.divider()

        if pred["clima"]:
            c = pred["clima"]
            hora_p = c.get("hora_pronostico", "actual")
            st.info(f"{c['ciudad']} · {hora_p} · {c['temperatura']}°C · Humedad {c['humedad']}% · {c['descripcion']} · Factor clima: {pred['factor_clima']}")

        col_f1, col_mid, col_f2 = st.columns([1, 2, 1])
        with col_f1:
            try:
                st.image(get_bandera_url(local), width=64)
            except:
                pass
            st.markdown(f"<div style='color:#c9a84c;font-size:11px;letter-spacing:0.08em;text-transform:uppercase;'>{local}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:28px;font-weight:700;color:#fff;'>{pred['prob_local']}%</div>", unsafe_allow_html=True)
        with col_mid:
            st.markdown(f"<div style='text-align:center;color:#444;font-size:10px;letter-spacing:0.2em;margin-top:8px;'>EMPATE</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center;font-size:20px;font-weight:500;color:#666;'>{pred['prob_empate']}%</div>", unsafe_allow_html=True)
        with col_f2:
            try:
                st.image(get_bandera_url(visitante), width=64)
            except:
                pass
            st.markdown(f"<div style='color:#c9a84c;font-size:11px;letter-spacing:0.08em;text-transform:uppercase;'>{visitante}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:28px;font-weight:700;color:#fff;'>{pred['prob_visitante']}%</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col9, col10, col11 = st.columns(3)
        with col9:
            st.markdown(f"""<div class="marcador-box">
                <div class="marcador-box-label">Si gana {local}</div>
                <div class="marcador-box-score">{pred['marcador_si_local']}</div>
            </div>""", unsafe_allow_html=True)
        with col10:
            st.markdown(f"""<div class="marcador-principal">
                <div class="marcador-principal-label">Marcador más probable</div>
                <div class="marcador-principal-score">{pred['marcador']}</div>
            </div>""", unsafe_allow_html=True)
        with col11:
            st.markdown(f"""<div class="marcador-box">
                <div class="marcador-box-label">Si gana {visitante}</div>
                <div class="marcador-box-score">{pred['marcador_si_visit']}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown(f"<div style='text-align:center;font-size:11px;color:#444;margin-top:8px;'>Si empatan: <span style='color:#c9a84c;'>{pred['marcador_si_empate']}</span></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:10px;color:#555;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:10px;'>Top 5 marcadores más probables</div>", unsafe_allow_html=True)
        for i, (marcador, prob) in enumerate(mc["top_marcadores"]):
            nums = ["01", "02", "03", "04", "05"]
            c1, c2, c3, c4 = st.columns([0.3, 0.5, 4, 0.7])
            with c1:
                st.markdown(f"<div style='font-size:10px;color:#333;padding-top:4px;'>{nums[i]}</div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div style='font-size:13px;font-weight:500;color:#fff;padding-top:2px;'>{marcador}</div>", unsafe_allow_html=True)
            with c3:
                st.progress(min(int(prob * 6), 100))
            with c4:
                st.markdown(f"<div style='font-size:11px;color:#555;padding-top:4px;text-align:right;'>{prob}%</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col12, col13 = st.columns(2)
        with col12:
            st.metric(f"Rating {local}", pred["rating_local"])
        with col13:
            st.metric(f"Rating {visitante}", pred["rating_visitante"])