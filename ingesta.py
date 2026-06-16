import requests
import sqlite3
from config import FOOTBALL_DATA_KEY, MUNDIAL_ID

HEADERS = {"X-Auth-Token": FOOTBALL_DATA_KEY}
BASE_URL = "https://api.football-data.org/v4"

def obtener_partidos_mundial():
    url = f"{BASE_URL}/competitions/{MUNDIAL_ID}/matches"
    r = requests.get(url, headers=HEADERS)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        partidos = data.get("matches", [])
        print(f"Total partidos encontrados: {len(partidos)}")
        return partidos
    else:
        print(f"Error: {r.text[:300]}")
        return []

def guardar_partidos(partidos):
    conn = sqlite3.connect("mundial2026.db")
    cursor = conn.cursor()
    guardados = 0
    for p in partidos:
        try:
            local = p["homeTeam"]["name"]
            visitante = p["awayTeam"]["name"]
            goles_local = p["score"]["fullTime"].get("home")
            goles_visitante = p["score"]["fullTime"].get("away")
            fecha = p["utcDate"]
            competicion = "Mundial 2026"
            fase = p.get("stage", "")
            cursor.execute('''
                INSERT OR IGNORE INTO partidos
                (equipo_local, equipo_visitante, goles_local, goles_visitante, fecha, competicion, fase)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (local, visitante, goles_local, goles_visitante, fecha, competicion, fase))
            guardados += 1
        except Exception as e:
            print(f"Error: {e}")
    conn.commit()
    conn.close()
    print(f"{guardados} partidos guardados en la base de datos.")

if __name__ == "__main__":
    print("Descargando partidos del Mundial 2026...")
    partidos = obtener_partidos_mundial()
    if partidos:
        guardar_partidos(partidos)