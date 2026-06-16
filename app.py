import streamlit as st
import sqlite3
from datetime import datetime, timedelta
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

ESTADIOS = {
    "New York": {"nombre": "MetLife Stadium", "img": "estadios/new_york.jpg"},
    "Los Angeles": {"nombre": "SoFi Stadium", "img": "estadios/los_angeles.jpg"},
    "Dallas": {"nombre": "AT&T Stadium", "img": "estadios/dallas.jpg"},
    "San Francisco": {"nombre": "Levi's Stadium", "img": "estadios/san_francisco.jpg"},
    "Miami": {"nombre": "Hard Rock Stadium", "img": "estadios/miami.jpg"},
    "Seattle": {"nombre": "Lumen Field", "img": "estadios/seattle.jpg"},
    "Boston": {"nombre": "Gillette Stadium", "img": "estadios/boston.jpg"},
    "Kansas City": {"nombre": "Arrowhead Stadium", "img": "estadios/kansas_city.jpg"},
    "Philadelphia": {"nombre": "Lincoln Financial Field", "img": "estadios/philadelphia.jpg"},
    "Atlanta": {"nombre": "Mercedes-Benz Stadium", "img": "estadios/atlanta.jpg"},
    "Houston": {"nombre": "NRG Stadium", "img": "estadios/houston.jpg"},
    "Mexico City": {"nombre": "Estadio Azteca", "img": "estadios/mexico_city.jpg"},
    "Guadalajara": {"nombre": "Estadio Akron", "img": "estadios/guadalajara.jpg"},
    "Monterrey": {"nombre": "Estadio BBVA", "img": "estadios/monterrey.jpg"},
    "Toronto": {"nombre": "BMO Field", "img": "estadios/toronto.jpg"},
    "Vancouver": {"nombre": "BC Place", "img": "estadios/vancouver.jpg"},
}

SEDES_UTC = {
    "New York": -4, "Los Angeles": -7, "Dallas": -5, "San Francisco": -7,
    "Miami": -4, "Seattle": -7, "Boston": -4, "Kansas City": -5,
    "Philadelphia": -4, "Atlanta": -4, "Houston": -5, "Mexico City": -6,
    "Guadalajara": -6, "Monterrey": -6, "Toronto": -4, "Vancouver": -7,
}

COLORES_POS = {
    "Portero":       {"dot": "#EF9F27", "line": "#EF9F2733", "label": "#EF9F27", "rating": "#EF9F27"},
    "Defensa":       {"dot": "#378ADD", "line": "#378ADD33", "label": "#378ADD", "rating": "#378ADD"},
    "Mediocampista": {"dot": "#1D9E75", "line": "#1D9E7533", "label": "#1D9E75", "rating": "#1D9E75"},
    "Delantero":     {"dot": "#D85A30", "line": "#D85A3033", "label": "#D85A30", "rating": "#D85A30"},
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

def get_partidos_equipo(equipo):
    conn = sqlite3.connect("mundial2026.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT fecha, hora_colombia, local, visitante, ciudad
        FROM calendario
        WHERE local = ? OR visitante = ?
        ORDER BY fecha, hora_colombia
    ''', (equipo, equipo))
    partidos = cursor.fetchall()
    conn.close()
    return partidos

def convertir_hora(fecha_str, hora_str, ciudad):
    utc_sede = SEDES_UTC.get(ciudad, -5)
    diferencia = utc_sede - (-5)
    dt = datetime.strptime(f"{fecha_str} {hora_str}", "%Y-%m-%d %H:%M")
    dt_sede = dt + timedelta(hours=diferencia)
    return dt_sede.strftime("%Y-%m-%d %H:%M"), dt_sede.strftime("%H:%M")

st.set_page_config(
    page_title="Predictor Mundial 2026",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
body, .stApp { background-color: #1e2a4a !important; }
.titulo {
    font-size: 2rem; font-weight: 900; text-align: center;
    letter-spacing: 0.2em; color: #c9a84c;
    margin-bottom: 0.2rem; padding-top: 1rem;
}
.subtitulo {
    font-size: 0.85rem; color: #7f9ab5; text-align: center;
    letter-spacing: 0.12em; margin-bottom: 2rem; text-transform: uppercase;
}
.panel-label {
    font-size: 0.8rem; font-weight: 700; color: #c9a84c;
    letter-spacing: 0.12em; text-transform: uppercase;
    border-bottom: 0.5px solid #2d3f6b; padding-bottom: 8px; margin-bottom: 1rem;
}
.partido-card {
    background: #162040; border: 0.5px solid #2d3f6b;
    border-radius: 8px; padding: 12px 16px; margin-bottom: 8px;
}
.partido-fecha { font-size: 12px; color: #7f9ab5; margin-bottom: 4px; }
.partido-equipos { font-size: 15px; color: #ffffff; font-weight: 600; margin: 2px 0; }
.partido-ciudad { font-size: 12px; color: #c9a84c; margin-top: 2px; }
.estadio-nombre { font-size: 12px; color: #7f9ab5; margin-top: 2px; }
.marcador-box {
    background: #162040; border: 0.5px solid #2d3f6b;
    border-radius: 8px; padding: 1rem; text-align: center;
}
.marcador-box-label { font-size: 0.75rem; color: #7f9ab5; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 6px; }
.marcador-box-score { font-size: 1.8rem; font-weight: 700; color: #c9a84c; }
.marcador-principal {
    background: #0d1a3a; border: 1px solid #c9a84c55;
    border-radius: 8px; padding: 1rem; text-align: center;
}
.marcador-principal-label { font-size: 0.75rem; color: #c9a84c; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 6px; }
.marcador-principal-score { font-size: 2.5rem; font-weight: 900; color: #f0cc6a; letter-spacing: 6px; }
.stButton > button {
    background: #c9a84c !important; color: #000 !important;
    font-weight: 800 !important; font-size: 0.85rem !important;
    letter-spacing: 0.15em !important; text-transform: uppercase !important;
    border: none !important; border-radius: 6px !important;
}
div[data-testid="stMetricValue"] { color: #c9a84c !important; font-size: 1.5rem !important; }
div[data-testid="stMetricLabel"] { color: #7f9ab5 !important; font-size: 0.85rem !important; }
.stCheckbox label { color: #b0bec5 !important; font-size: 13px !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="titulo">PREDICTOR MUNDIAL 2026</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">Forma reciente · Ranking FIFA · Ratings · Clima · Monte Carlo 100K</div>', unsafe_allow_html=True)

equipos = get_equipos()
opciones_equipo = ["— Selecciona un equipo —"] + equipos

for key in ["local_sel", "visitante_sel", "ciudad_sel", "fecha_sel", "hora_sel"]:
    if key not in st.session_state:
        st.session_state[key] = None

st.markdown('<div class="panel-label">Selecciona un equipo para ver sus partidos</div>', unsafe_allow_html=True)
equipo_buscar = st.selectbox("", opciones_equipo, key="buscar_eq", label_visibility="collapsed")

if equipo_buscar != "— Selecciona un equipo —":
    try:
        st.image(get_bandera_url(equipo_buscar), width=48)
    except:
        pass
    partidos = get_partidos_equipo(equipo_buscar)
    if partidos:
        st.markdown('<div class="panel-label" style="margin-top:1rem;">Partidos programados</div>', unsafe_allow_html=True)
        for p in partidos:
            fecha, hora_col, local, visitante, ciudad = p
            fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
            fecha_display = fecha_dt.strftime("%d %b %Y")
            _, hora_sede = convertir_hora(fecha, hora_col, ciudad)
            estadio = ESTADIOS.get(ciudad, {})

            col_info, col_btn = st.columns([4, 1])
            with col_info:
                st.markdown(f"""
                <div class="partido-card">
                    <div class="partido-fecha">{fecha_display} · {hora_col} Colombia · {hora_sede} hora local</div>
                    <div class="partido-equipos">{local} vs {visitante}</div>
                    <div class="partido-ciudad">{ciudad}</div>
                    <div class="estadio-nombre">{estadio.get('nombre', '')}</div>
                </div>
                """, unsafe_allow_html=True)
            with col_btn:
                if st.button("Elegir", key=f"btn_{fecha}_{local}_{visitante}"):
                    st.session_state.local_sel = local
                    st.session_state.visitante_sel = visitante
                    st.session_state.ciudad_sel = ciudad
                    st.session_state.fecha_sel = fecha
                    st.session_state.hora_sel = hora_col
                    st.rerun()

st.divider()

if st.session_state.ciudad_sel:
    fecha_hora_sede, hora_sede = convertir_hora(
        st.session_state.fecha_sel,
        st.session_state.hora_sel,
        st.session_state.ciudad_sel
    )
    fecha_dt = datetime.strptime(st.session_state.fecha_sel, "%Y-%m-%d")
    ciudad = st.session_state.ciudad_sel
    estadio = ESTADIOS.get(ciudad, {})

    st.markdown(f"""
    <div style="background:#162040;border:0.5px solid #2d3f6b;border-radius:10px;padding:14px 18px;margin-bottom:1rem;">
        <div style="font-size:13px;color:#7f9ab5;margin-bottom:4px;">{fecha_dt.strftime('%d %b %Y')} · {st.session_state.hora_sel} Colombia · {hora_sede} hora local</div>
        <div style="font-size:18px;color:#ffffff;font-weight:700;">{st.session_state.local_sel} vs {st.session_state.visitante_sel}</div>
        <div style="font-size:13px;color:#c9a84c;margin-top:2px;">{estadio.get('nombre', ciudad)} · {ciudad}</div>
    </div>
    """, unsafe_allow_html=True)

    if estadio.get("img"):
        try:
            st.image(estadio["img"], use_container_width=True, caption=estadio.get("nombre", ""))
        except:
            pass

    col1, col2 = st.columns(2, gap="large")

    def render_equipo(key_prefix, label, equipo_default):
        st.markdown(f'<div class="panel-label">{label}</div>', unsafe_allow_html=True)
        try:
            st.image(get_bandera_url(equipo_default), width=48)
        except:
            pass
        st.markdown(f"<div style='font-size:16px;color:#fff;font-weight:600;margin-bottom:12px;'>{equipo_default}</div>", unsafe_allow_html=True)

        jugadores = get_jugadores(equipo_default)
        titulares = []
        pos_actual = None

        for nombre, posicion, rating in jugadores:
            col = COLORES_POS.get(posicion, {"dot": "#555", "line": "#33333333", "label": "#7f9ab5", "rating": "#7f9ab5"})
            if posicion != pos_actual:
                pos_actual = posicion
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:8px;margin-top:14px;margin-bottom:6px;">
                    <div style="width:7px;height:7px;border-radius:50%;background:{col['dot']};flex-shrink:0;"></div>
                    <span style="font-size:11px;font-weight:700;color:{col['label']};letter-spacing:0.12em;text-transform:uppercase;">{posicion}s</span>
                    <div style="flex:1;height:0.5px;background:{col['line']};"></div>
                </div>
                """, unsafe_allow_html=True)
            checked = st.checkbox(f"{nombre}", key=f"{key_prefix}_{nombre}", help=f"Rating: {rating}")
            if checked:
                titulares.append(nombre)
            st.markdown(f'<div style="font-size:12px;color:{col["rating"]};margin-top:-10px;margin-bottom:6px;padding-left:24px;">{rating}</div>', unsafe_allow_html=True)

        n = len(titulares)
        if n == 11:
            rating_once = obtener_rating_once(equipo_default, titulares)
            st.success(f"{n}/11 seleccionados · Rating: {rating_once}")
        elif n > 0:
            st.warning(f"{n}/11 seleccionados")
        else:
            st.caption("Sin selección — promedio del plantel")

        return titulares

    with col1:
        titulares_local = render_equipo("l", "Equipo local", st.session_state.local_sel)
    with col2:
        titulares_visit = render_equipo("v", "Equipo visitante", st.session_state.visitante_sel)

    st.markdown("<br>", unsafe_allow_html=True)
    predecir = st.button("PREDECIR PARTIDO", type="primary", use_container_width=True)

    if predecir:
        with st.spinner("Simulando 100.000 partidos..."):
            tl = titulares_local if len(titulares_local) == 11 else None
            tv = titulares_visit if len(titulares_visit) == 11 else None
            pred = predecir_partido(st.session_state.local_sel, st.session_state.visitante_sel, ciudad, fecha_hora_sede, tl, tv)
            mc = monte_carlo(st.session_state.local_sel, st.session_state.visitante_sel, ciudad, fecha_hora_sede, tl, tv)

        st.divider()

        if pred["clima"]:
            c = pred["clima"]
            hora_p = c.get("hora_pronostico", "actual")
            st.info(f"{c['ciudad']} · {hora_p} · {c['temperatura']}°C · Humedad {c['humedad']}% · {c['descripcion']} · Factor clima: {pred['factor_clima']}")

        col_f1, col_mid, col_f2 = st.columns([1, 2, 1])
        with col_f1:
            try:
                st.image(get_bandera_url(st.session_state.local_sel), width=64)
            except:
                pass
            st.markdown(f"<div style='color:#c9a84c;font-size:12px;letter-spacing:0.08em;text-transform:uppercase;'>{st.session_state.local_sel}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:32px;font-weight:700;color:#fff;'>{pred['prob_local']}%</div>", unsafe_allow_html=True)
        with col_mid:
            st.markdown(f"<div style='text-align:center;color:#7f9ab5;font-size:12px;letter-spacing:0.2em;margin-top:10px;'>EMPATE</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center;font-size:24px;font-weight:500;color:#b0bec5;'>{pred['prob_empate']}%</div>", unsafe_allow_html=True)
        with col_f2:
            try:
                st.image(get_bandera_url(st.session_state.visitante_sel), width=64)
            except:
                pass
            st.markdown(f"<div style='color:#c9a84c;font-size:12px;letter-spacing:0.08em;text-transform:uppercase;'>{st.session_state.visitante_sel}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:32px;font-weight:700;color:#fff;'>{pred['prob_visitante']}%</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col9, col10, col11 = st.columns(3)
        with col9:
            st.markdown(f"""<div class="marcador-box">
                <div class="marcador-box-label">Si gana {st.session_state.local_sel}</div>
                <div class="marcador-box-score">{pred['marcador_si_local']}</div>
            </div>""", unsafe_allow_html=True)
        with col10:
            st.markdown(f"""<div class="marcador-principal">
                <div class="marcador-principal-label">Marcador más probable</div>
                <div class="marcador-principal-score">{pred['marcador']}</div>
            </div>""", unsafe_allow_html=True)
        with col11:
            st.markdown(f"""<div class="marcador-box">
                <div class="marcador-box-label">Si gana {st.session_state.visitante_sel}</div>
                <div class="marcador-box-score">{pred['marcador_si_visit']}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown(f"<div style='text-align:center;font-size:13px;color:#7f9ab5;margin-top:10px;'>Si empatan: <span style='color:#c9a84c;font-weight:600;'>{pred['marcador_si_empate']}</span></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:12px;color:#7f9ab5;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:10px;'>Top 5 marcadores más probables</div>", unsafe_allow_html=True)
        for i, (marcador, prob) in enumerate(mc["top_marcadores"]):
            nums = ["01", "02", "03", "04", "05"]
            c1, c2, c3, c4 = st.columns([0.3, 0.5, 4, 0.7])
            with c1:
                st.markdown(f"<div style='font-size:12px;color:#7f9ab5;padding-top:4px;'>{nums[i]}</div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div style='font-size:14px;font-weight:600;color:#fff;padding-top:2px;'>{marcador}</div>", unsafe_allow_html=True)
            with c3:
                st.progress(min(int(prob * 6), 100))
            with c4:
                st.markdown(f"<div style='font-size:12px;color:#7f9ab5;padding-top:4px;text-align:right;'>{prob}%</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col12, col13 = st.columns(2)
        with col12:
            st.metric(f"Rating {st.session_state.local_sel}", pred["rating_local"])
        with col13:
            st.metric(f"Rating {st.session_state.visitante_sel}", pred["rating_visitante"])

else:
    st.markdown("<div style='text-align:center;color:#7f9ab5;font-size:14px;margin-top:2rem;'>Selecciona un equipo arriba y elige un partido para comenzar</div>", unsafe_allow_html=True)