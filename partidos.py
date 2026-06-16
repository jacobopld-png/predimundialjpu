import sqlite3
from config import GRUPOS, RANKING_FIFA

ES_A_EN = {
    "México": "Mexico", "Sudáfrica": "South Africa", "Corea del Sur": "South Korea",
    "República Checa": "Czechia", "Canadá": "Canada", "Bosnia y Herzegovina": "Bosnia-Herzegovina",
    "Catar": "Qatar", "Suiza": "Switzerland", "Brasil": "Brazil", "Marruecos": "Morocco",
    "Haití": "Haiti", "Escocia": "Scotland", "Estados Unidos": "United States",
    "Paraguay": "Paraguay", "Australia": "Australia", "Turquía": "Turkey",
    "Alemania": "Germany", "Curazao": "Curaçao", "Costa de Marfil": "Ivory Coast",
    "Ecuador": "Ecuador", "Países Bajos": "Netherlands", "Japón": "Japan",
    "Suecia": "Sweden", "Túnez": "Tunisia", "Bélgica": "Belgium", "Egipto": "Egypt",
    "Irán": "Iran", "Nueva Zelanda": "New Zealand", "España": "Spain",
    "Cabo Verde": "Cape Verde", "Arabia Saudí": "Saudi Arabia", "Uruguay": "Uruguay",
    "Francia": "France", "Senegal": "Senegal", "Irak": "Iraq", "Noruega": "Norway",
    "Argentina": "Argentina", "Argelia": "Algeria", "Austria": "Austria",
    "Jordania": "Jordan", "Portugal": "Portugal", "Rep. Dem. del Congo": "DR Congo",
    "Uzbekistán": "Uzbekistan", "Colombia": "Colombia", "Inglaterra": "England",
    "Croacia": "Croatia", "Ghana": "Ghana", "Panamá": "Panama",
}

def calcular_forma(equipo_es):
    conn = sqlite3.connect("mundial2026.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT goles_favor, goles_contra, competicion
        FROM partidos_manuales
        WHERE equipo = ?
        ORDER BY fecha DESC
        LIMIT 10
    ''', (equipo_es,))
    partidos = cursor.fetchall()
    conn.close()

    victorias = empates = derrotas = 0
    goles_favor = goles_contra = 0
    puntos = 0

    for p in partidos:
        gf, gc, comp = p
        goles_favor += gf
        goles_contra += gc
        if gf > gc:
            victorias += 1
            puntos += 3
        elif gf == gc:
            empates += 1
            puntos += 1
        else:
            derrotas += 1

    total = victorias + empates + derrotas
    return {
        "equipo": equipo_es,
        "partidos": total,
        "victorias": victorias,
        "empates": empates,
        "derrotas": derrotas,
        "goles_favor": goles_favor,
        "goles_contra": goles_contra,
        "diferencia_gol": goles_favor - goles_contra,
        "puntos": puntos,
    }

if __name__ == "__main__":
    todos = []
    for grupo, equipos in GRUPOS.items():
        for equipo in equipos:
            forma = calcular_forma(equipo)
            forma["grupo"] = grupo
            todos.append(forma)
    todos.sort(key=lambda x: x["puntos"], reverse=True)
    print(f"\n{'Equipo':<30} {'G':>3} {'E':>3} {'D':>3} {'GF':>4} {'GC':>4} {'DG':>4} {'Pts':>4}")
    print("-" * 65)
    for f in todos:
        if f["partidos"] > 0:
            print(f"{f['equipo']:<30} {f['victorias']:>3} {f['empates']:>3} {f['derrotas']:>3} {f['goles_favor']:>4} {f['goles_contra']:>4} {f['diferencia_gol']:>4} {f['puntos']:>4}")