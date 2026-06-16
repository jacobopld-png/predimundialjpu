import requests
import sqlite3
import time

HEADERS = {"X-Auth-Token": "bc116ca4a81c4594bd73ae95f3856193"}
BASE_URL = "https://api.football-data.org/v4/teams"

EQUIPOS_IDS = {
    "Uruguay": 758, "Alemania": 759, "España": 760, "Paraguay": 761,
    "Argentina": 762, "Ghana": 763, "Brasil": 764, "Portugal": 765,
    "Japón": 766, "México": 769, "Inglaterra": 770, "Estados Unidos": 771,
    "Corea del Sur": 772, "Francia": 773, "Sudáfrica": 774, "Argelia": 778,
    "Australia": 779, "Nueva Zelanda": 783, "Suiza": 788, "Ecuador": 791,
    "Suecia": 792, "República Checa": 798, "Croacia": 799,
    "Arabia Saudí": 801, "Túnez": 802, "Turquía": 803, "Senegal": 804,
    "Bélgica": 805, "Marruecos": 815, "Austria": 816, "Colombia": 818,
    "Egipto": 825, "Canadá": 828, "Haití": 836, "Irán": 840,
    "Bosnia y Herzegovina": 1060, "Panamá": 1836, "Cabo Verde": 1930,
    "Rep. Dem. del Congo": 1934, "Costa de Marfil": 1935, "Catar": 8030,
    "Jordania": 8049, "Irak": 8062, "Uzbekistán": 8070,
    "Países Bajos": 8601, "Noruega": 8872, "Escocia": 8873,
    "Curazao": 9460,
}

def crear_tabla_jugadores():
    conn = sqlite3.connect("mundial2026.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jugadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            equipo TEXT,
            posicion TEXT,
            fecha_nacimiento TEXT,
            nacionalidad TEXT,
            UNIQUE(nombre, equipo)
        )
    ''')
    conn.commit()
    conn.close()
    print("Tabla jugadores creada.")

def descargar_plantel(equipo_es, team_id):
    url = f"{BASE_URL}/{team_id}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        print(f"  Error {r.status_code} para {equipo_es}")
        return []
    data = r.json()
    jugadores = []
    for j in data.get("squad", []):
        jugadores.append({
            "nombre": j.get("name", ""),
            "equipo": equipo_es,
            "posicion": j.get("position", ""),
            "fecha_nacimiento": j.get("dateOfBirth", ""),
            "nacionalidad": j.get("nationality", ""),
        })
    return jugadores

def guardar_jugadores(jugadores):
    conn = sqlite3.connect("mundial2026.db")
    cursor = conn.cursor()
    guardados = 0
    for j in jugadores:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO jugadores
                (nombre, equipo, posicion, fecha_nacimiento, nacionalidad)
                VALUES (?, ?, ?, ?, ?)
            ''', (j["nombre"], j["equipo"], j["posicion"], j["fecha_nacimiento"], j["nacionalidad"]))
            guardados += 1
        except:
            pass
    conn.commit()
    conn.close()
    return guardados

if __name__ == "__main__":
    crear_tabla_jugadores()
    print(f"\nDescargando planteles de {len(EQUIPOS_IDS)} equipos...\n")
    total = 0
    for equipo, team_id in EQUIPOS_IDS.items():
        print(f"  → {equipo}...")
        jugadores = descargar_plantel(equipo, team_id)
        if jugadores:
            guardados = guardar_jugadores(jugadores)
            total += guardados
            print(f"     {guardados} jugadores guardados")
        time.sleep(0.5)
    print(f"\nTotal: {total} jugadores en la base de datos.")