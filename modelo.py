import sqlite3
import numpy as np
from scipy.stats import poisson
from config import RANKING_FIFA
from partidos import ES_A_EN, calcular_forma
from clima import obtener_clima_pronostico, factor_clima

LIGA_FACTOR = {
    "Champions":   1.5,
    "Europa_Top":  1.2,
    "Europa_Mid":  1.0,
    "Europa_Low":  0.8,
    "America":     0.85,
    "Asia_Africa": 0.65,
}

def obtener_rating_once(equipo_es, titulares=None):
    conn = sqlite3.connect("mundial2026.db")
    cursor = conn.cursor()
    if titulares:
        ratings = []
        for jugador in titulares:
            cursor.execute('''
                SELECT rating FROM jugadores
                WHERE equipo = ? AND nombre = ?
            ''', (equipo_es, jugador))
            row = cursor.fetchone()
            if row:
                ratings.append(row[0])
        if ratings:
            conn.close()
            return round(sum(ratings) / len(ratings), 1)
    cursor.execute('''
        SELECT AVG(rating) FROM jugadores WHERE equipo = ?
    ''', (equipo_es,))
    resultado = cursor.fetchone()[0]
    conn.close()
    return round(resultado, 1) if resultado else 75.0

def obtener_factor_liga(equipo_es, titulares=None):
    conn = sqlite3.connect("mundial2026.db")
    cursor = conn.cursor()
    if titulares:
        factores = []
        for jugador in titulares:
            cursor.execute('''
                SELECT liga FROM jugadores
                WHERE equipo = ? AND nombre = ?
            ''', (equipo_es, jugador))
            row = cursor.fetchone()
            if row:
                factores.append(LIGA_FACTOR.get(row[0], 1.0))
        if factores:
            conn.close()
            return round(sum(factores) / len(factores), 3)
        conn.close()
        return 1.0
    cursor.execute('''
        SELECT liga FROM jugadores WHERE equipo = ?
    ''', (equipo_es,))
    ligas = [row[0] for row in cursor.fetchall()]
    conn.close()
    if not ligas:
        return 1.0
    return round(sum(LIGA_FACTOR.get(l, 1.0) for l in ligas) / len(ligas), 3)

def peso_rival(rival):
    ranking = RANKING_FIFA.get(rival, 150)
    if ranking <= 10:
        return 3.0
    elif ranking <= 20:
        return 2.0
    elif ranking <= 30:
        return 1.5
    elif ranking <= 50:
        return 1.0
    elif ranking <= 80:
        return 0.4
    elif ranking <= 120:
        return 0.2
    else:
        return 0.1

def calcular_lambda(equipo_es, titulares=None):
    conn = sqlite3.connect("mundial2026.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT goles_favor, goles_contra, rival, competicion
        FROM partidos_manuales
        WHERE equipo = ?
        ORDER BY fecha DESC
        LIMIT 10
    ''', (equipo_es,))
    partidos = cursor.fetchall()
    conn.close()

    ranking = RANKING_FIFA.get(equipo_es, 40)
    ranking_factor = max(0, (80 - ranking) / 80)
    rating = obtener_rating_once(equipo_es, titulares)
    rating_factor = (rating - 65) / 25
    liga_factor = obtener_factor_liga(equipo_es, titulares)

    if not partidos:
        return max(0.3, ranking_factor * 3.0 * liga_factor), 1.2

    goles_favor_pond = 0
    goles_contra_pond = 0
    peso_total = 0

    for gf, gc, rival, comp in partidos:
        w = peso_rival(rival)
        if comp in ["Eliminatorias CONMEBOL", "Eliminatorias UEFA",
                    "Eliminatorias AFC", "Eliminatorias CAF",
                    "CONCACAF Eliminatorias", "Mundial 2026",
                    "Copa América", "Eurocopa", "Copa Africana",
                    "Nations League", "Liga de Naciones CONCACAF",
                    "East Asian Championship", "CAFA Nations Cup",
                    "Canadian Shield", "FIFA Series"]:
            w *= 1.3
        goles_favor_pond += gf * w
        goles_contra_pond += gc * w
        peso_total += w

    goles_por_partido = goles_favor_pond / peso_total
    goles_contra_por_partido = goles_contra_pond / peso_total

    lambda_ataque = ((goles_por_partido * 0.15) + (ranking_factor * 3.0 * 0.55) + (rating_factor * 1.5 * 0.3)) * liga_factor
    lambda_defensa = goles_contra_por_partido * (1 - rating_factor * 0.25) * (1 / liga_factor)

    return max(0.3, lambda_ataque), max(0.2, lambda_defensa)

def monte_carlo(local_es, visitante_es, ciudad=None, fecha_hora=None, titulares_local=None, titulares_visit=None, iteraciones=100000):
    lambda_local_atq, lambda_local_def = calcular_lambda(local_es, titulares_local)
    lambda_visit_atq, lambda_visit_def = calcular_lambda(visitante_es, titulares_visit)
    lambda_l = (lambda_local_atq + lambda_visit_def) / 2
    lambda_v = (lambda_visit_atq + lambda_local_def) / 2

    if ciudad and fecha_hora:
        clima_info = obtener_clima_pronostico(ciudad, fecha_hora)
        if clima_info:
            factor_c = factor_clima(clima_info)
            ranking_local = RANKING_FIFA.get(local_es, 40)
            ranking_visit = RANKING_FIFA.get(visitante_es, 40)
            if ranking_local > ranking_visit:
                lambda_l *= (1 - factor_c * 0.5)
            else:
                lambda_v *= (1 - factor_c * 0.5)

    goles_l = np.random.poisson(lambda_l, iteraciones)
    goles_v = np.random.poisson(lambda_v, iteraciones)

    local_gana = np.sum(goles_l > goles_v)
    empate = np.sum(goles_l == goles_v)
    visit_gana = np.sum(goles_l < goles_v)

    marcadores = {}
    marcadores_local = {}
    marcadores_visit = {}
    marcadores_empate = {}

    for g1, g2 in zip(goles_l, goles_v):
        key = f"{g1}-{g2}"
        marcadores[key] = marcadores.get(key, 0) + 1
        if g1 > g2:
            marcadores_local[key] = marcadores_local.get(key, 0) + 1
        elif g1 == g2:
            marcadores_empate[key] = marcadores_empate.get(key, 0) + 1
        else:
            marcadores_visit[key] = marcadores_visit.get(key, 0) + 1

    top5 = sorted(marcadores.items(), key=lambda x: x[1], reverse=True)[:5]
    mejor_local = sorted(marcadores_local.items(), key=lambda x: x[1], reverse=True)
    mejor_visit = sorted(marcadores_visit.items(), key=lambda x: x[1], reverse=True)
    mejor_empate = sorted(marcadores_empate.items(), key=lambda x: x[1], reverse=True)

    marcador_si_local = mejor_local[0][0] if mejor_local else "1-0"
    marcador_si_visit = mejor_visit[0][0] if mejor_visit else "0-1"
    marcador_si_empate = mejor_empate[0][0] if mejor_empate else "0-0"

    return {
        "prob_local_mc": round(local_gana / iteraciones * 100, 1),
        "prob_empate_mc": round(empate / iteraciones * 100, 1),
        "prob_visitante_mc": round(visit_gana / iteraciones * 100, 1),
        "top_marcadores": [(m, round(c/iteraciones*100, 1)) for m, c in top5],
        "marcador_probable": top5[0][0] if top5 else "1-0",
        "marcador_si_local": marcador_si_local,
        "marcador_si_visit": marcador_si_visit,
        "marcador_si_empate": marcador_si_empate,
        "lambda_local": round(lambda_l, 3),
        "lambda_visitante": round(lambda_v, 3),
    }

def predecir_partido(local_es, visitante_es, ciudad=None, fecha_hora=None, titulares_local=None, titulares_visit=None):
    mc = monte_carlo(local_es, visitante_es, ciudad, fecha_hora, titulares_local, titulares_visit)

    clima_info = None
    factor_c = 0
    if ciudad and fecha_hora:
        clima_info = obtener_clima_pronostico(ciudad, fecha_hora)
        if clima_info:
            factor_c = factor_clima(clima_info)

    liga_local = obtener_factor_liga(local_es, titulares_local)
    liga_visitante = obtener_factor_liga(visitante_es, titulares_visit)

    return {
        "local": local_es,
        "visitante": visitante_es,
        "marcador": mc["top_marcadores"][0][0] if mc["top_marcadores"] else "1-0",
        "marcador_si_local": mc["marcador_si_local"],
        "marcador_si_visit": mc["marcador_si_visit"],
        "marcador_si_empate": mc["marcador_si_empate"],
        "prob_local": mc["prob_local_mc"],
        "prob_empate": mc["prob_empate_mc"],
        "prob_visitante": mc["prob_visitante_mc"],
        "top_marcadores": mc["top_marcadores"],
        "clima": clima_info,
        "factor_clima": factor_c,
        "rating_local": obtener_rating_once(local_es, titulares_local),
        "rating_visitante": obtener_rating_once(visitante_es, titulares_visit),
        "liga_local": liga_local,
        "liga_visitante": liga_visitante,
        "lambda_local": mc["lambda_local"],
        "lambda_visitante": mc["lambda_visitante"],
    }

if __name__ == "__main__":
    local = input("Equipo local: ")
    visitante = input("Equipo visitante: ")
    ciudad = input("Ciudad sede: ").strip()
    fecha_hora = input("Fecha y hora (YYYY-MM-DD HH:MM): ").strip()

    print(f"\n¿Ingresar alineación titular? (s/n): ", end="")
    usar_titular = input().strip().lower()

    titulares_local = None
    titulares_visit = None

    if usar_titular == "s":
        print(f"\nTitulares de {local}:")
        titulares_local = [t.strip() for t in input().split(",")]
        print(f"Titulares de {visitante}:")
        titulares_visit = [t.strip() for t in input().split(",")]

    pred = predecir_partido(local, visitante, ciudad, fecha_hora, titulares_local, titulares_visit)

    print(f"\nRating: {local} {pred['rating_local']} | {visitante} {pred['rating_visitante']}")
    print(f"Factor liga: {local} {pred['liga_local']} | {visitante} {pred['liga_visitante']}")
    print(f"Lambda: {local} {pred['lambda_local']} | {visitante} {pred['lambda_visitante']}")

    if pred["clima"]:
        c = pred["clima"]
        print(f"Clima: {c['ciudad']} {c['temperatura']}°C, {c['humedad']}% humedad")

    print(f"\n{'='*50}")
    print(f"  {local} vs {visitante}")
    print(f"  Marcador más probable: {pred['marcador']}")
    print(f"  Si gana {local}: {pred['marcador_si_local']}")
    print(f"  Si empatan: {pred['marcador_si_empate']}")
    print(f"  Si gana {visitante}: {pred['marcador_si_visit']}")
    print(f"{'='*50}")
    print(f"  {local}: {pred['prob_local']}%")
    print(f"  Empate: {pred['prob_empate']}%")
    print(f"  {visitante}: {pred['prob_visitante']}%")
    print(f"\n  Top 5 marcadores:")
    for marcador, prob in pred["top_marcadores"]:
        print(f"    {marcador} → {prob}%")
    print(f"{'='*50}")