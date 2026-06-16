import sqlite3
import csv

def cargar_jugadores_csv():
    conn = sqlite3.connect("mundial2026.db")
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jugadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipo TEXT,
            nombre TEXT,
            posicion TEXT,
            rating INTEGER,
            UNIQUE(equipo, nombre)
        )
    ''')

    cursor.execute("DELETE FROM jugadores")

    guardados = 0
    with open("mundial2026_jugadores.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO jugadores
                    (equipo, nombre, posicion, rating)
                    VALUES (?, ?, ?, ?)
                ''', (
                    row["equipo"].strip(),
                    row["nombre"].strip(),
                    row["posicion"].strip(),
                    int(row["rating"])
                ))
                guardados += 1
            except Exception as e:
                print(f"Error: {row} → {e}")

    conn.commit()
    conn.close()
    print(f"{guardados} jugadores cargados.")

if __name__ == "__main__":
    cargar_jugadores_csv()