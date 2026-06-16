import sqlite3
import csv

def cargar_jugadores_csv():
    conn = sqlite3.connect("mundial2026.db")
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS jugadores")
    cursor.execute('''
        CREATE TABLE jugadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipo TEXT,
            nombre TEXT,
            posicion TEXT,
            rating INTEGER,
            liga TEXT,
            UNIQUE(equipo, nombre)
        )
    ''')

    guardados = 0
    with open("mundial2026_jugadores_v3_6cat.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                cursor.execute('''
                    INSERT INTO jugadores
                    (equipo, nombre, posicion, rating, liga)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    row["equipo"].strip(),
                    row["nombre"].strip(),
                    row["posicion"].strip(),
                    int(row["rating"]),
                    row["liga"].strip(),
                ))
                guardados += 1
            except Exception as e:
                print(f"Error: {row} → {e}")

    conn.commit()
    conn.close()
    print(f"{guardados} jugadores cargados con 6 categorías de liga.")

if __name__ == "__main__":
    cargar_jugadores_csv()