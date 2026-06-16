import sqlite3
import csv
from config import DATABASE_URL, GRUPOS, RANKING_FIFA

def crear_base_datos():
    conn = sqlite3.connect("mundial2026.db")
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE,
            grupo TEXT,
            ranking_fifa INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS partidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipo_local TEXT,
            equipo_visitante TEXT,
            goles_local INTEGER,
            goles_visitante INTEGER,
            fecha TEXT,
            competicion TEXT,
            fase TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS partidos_manuales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipo TEXT,
            rival TEXT,
            goles_favor INTEGER,
            goles_contra INTEGER,
            fecha TEXT,
            competicion TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estadisticas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipo TEXT,
            partido_id INTEGER,
            posesion REAL,
            tiros INTEGER,
            tiros_puerta INTEGER,
            xg REAL,
            pases_completados REAL,
            recuperaciones INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estado_equipo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipo TEXT,
            fecha TEXT,
            lesionados TEXT,
            suspendidos TEXT,
            formacion TEXT,
            notas TEXT
        )
    ''')

    for grupo, equipos in GRUPOS.items():
        for equipo in equipos:
            ranking = RANKING_FIFA.get(equipo, 99)
            cursor.execute('''
                INSERT OR IGNORE INTO equipos (nombre, grupo, ranking_fifa)
                VALUES (?, ?, ?)
            ''', (equipo, grupo, ranking))

    conn.commit()
    conn.close()
    print("Base de datos creada con los 48 equipos.")

def importar_partidos_manuales():
    conn = sqlite3.connect("mundial2026.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM partidos_manuales")
    guardados = 0
    with open("partidos_manuales.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                fecha = None if row["fecha"] == "null" else row["fecha"]
                cursor.execute('''
                    INSERT INTO partidos_manuales
                    (equipo, rival, goles_favor, goles_contra, fecha, competicion)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    row["equipo"].strip(),
                    row["rival"].strip(),
                    int(row["goles_favor"]),
                    int(row["goles_contra"]),
                    fecha,
                    row["competicion"].strip()
                ))
                guardados += 1
            except Exception as e:
                print(f"Error en fila: {row} → {e}")
    conn.commit()
    conn.close()
    print(f"{guardados} partidos manuales importados.")

if __name__ == "__main__":
    crear_base_datos()
    importar_partidos_manuales()