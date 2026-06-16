import sqlite3

PARTIDOS = [
    ("2026-06-11", "13:00", "México", "Sudáfrica", "Mexico City"),
    ("2026-06-11", "20:00", "Corea del Sur", "República Checa", "Guadalajara"),
    ("2026-06-12", "14:00", "Canadá", "Bosnia y Herzegovina", "Toronto"),
    ("2026-06-12", "21:00", "Estados Unidos", "Paraguay", "Los Angeles"),
    ("2026-06-13", "14:00", "Catar", "Suiza", "San Francisco"),
    ("2026-06-13", "17:00", "Brasil", "Marruecos", "New York"),
    ("2026-06-13", "20:00", "Haití", "Escocia", "Boston"),
    ("2026-06-13", "23:00", "Australia", "Turquía", "Vancouver"),
    ("2026-06-14", "11:00", "Alemania", "Curazao", "Houston"),
    ("2026-06-14", "14:00", "Países Bajos", "Japón", "Dallas"),
    ("2026-06-14", "17:00", "Costa de Marfil", "Ecuador", "Philadelphia"),
    ("2026-06-14", "20:00", "Suecia", "Túnez", "Monterrey"),
    ("2026-06-15", "10:00", "España", "Cabo Verde", "Atlanta"),
    ("2026-06-15", "14:00", "Bélgica", "Egipto", "Seattle"),
    ("2026-06-15", "17:00", "Arabia Saudí", "Uruguay", "Miami"),
    ("2026-06-15", "20:00", "Irán", "Nueva Zelanda", "Los Angeles"),
    ("2026-06-16", "14:00", "Francia", "Senegal", "New York"),
    ("2026-06-16", "17:00", "Irak", "Noruega", "Boston"),
    ("2026-06-16", "20:00", "Argentina", "Argelia", "Kansas City"),
    ("2026-06-16", "23:00", "Austria", "Jordania", "San Francisco"),
    ("2026-06-17", "11:00", "Portugal", "Rep. Dem. del Congo", "Houston"),
    ("2026-06-17", "14:00", "Inglaterra", "Croacia", "Dallas"),
    ("2026-06-17", "18:00", "Ghana", "Panamá", "Toronto"),
    ("2026-06-17", "21:00", "Uzbekistán", "Colombia", "Mexico City"),
    ("2026-06-18", "11:00", "República Checa", "Sudáfrica", "Atlanta"),
    ("2026-06-18", "14:00", "Suiza", "Bosnia y Herzegovina", "Los Angeles"),
    ("2026-06-18", "17:00", "Canadá", "Catar", "Vancouver"),
    ("2026-06-18", "20:00", "México", "Corea del Sur", "Guadalajara"),
    ("2026-06-19", "14:00", "Brasil", "Haití", "Philadelphia"),
    ("2026-06-19", "17:00", "Escocia", "Marruecos", "Boston"),
    ("2026-06-19", "20:00", "Turquía", "Paraguay", "San Francisco"),
    ("2026-06-19", "22:00", "Estados Unidos", "Australia", "Seattle"),
    ("2026-06-20", "12:00", "Alemania", "Costa de Marfil", "Toronto"),
    ("2026-06-20", "16:00", "Ecuador", "Curazao", "Kansas City"),
    ("2026-06-20", "21:00", "Países Bajos", "Suecia", "Houston"),
    ("2026-06-20", "22:00", "Túnez", "Japón", "Monterrey"),
    ("2026-06-21", "14:00", "Uruguay", "Cabo Verde", "Miami"),
    ("2026-06-21", "17:00", "España", "Arabia Saudí", "Atlanta"),
    ("2026-06-21", "20:00", "Bélgica", "Irán", "Los Angeles"),
    ("2026-06-21", "20:00", "Nueva Zelanda", "Egipto", "Vancouver"),
    ("2026-06-22", "13:00", "Noruega", "Senegal", "New York"),
    ("2026-06-22", "16:00", "Francia", "Irak", "Philadelphia"),
    ("2026-06-22", "21:00", "Argentina", "Austria", "Dallas"),
    ("2026-06-22", "22:00", "Jordania", "Argelia", "San Francisco"),
    ("2026-06-23", "13:00", "Inglaterra", "Ghana", "Boston"),
    ("2026-06-23", "16:00", "Panamá", "Croacia", "Toronto"),
    ("2026-06-23", "21:00", "Portugal", "Uzbekistán", "Houston"),
    ("2026-06-23", "21:00", "Colombia", "Rep. Dem. del Congo", "Guadalajara"),
    ("2026-06-24", "14:00", "Escocia", "Brasil", "Miami"),
    ("2026-06-24", "14:00", "Marruecos", "Haití", "Atlanta"),
    ("2026-06-24", "17:00", "Suiza", "Canadá", "Vancouver"),
    ("2026-06-24", "17:00", "Bosnia y Herzegovina", "Catar", "Seattle"),
    ("2026-06-24", "20:00", "República Checa", "México", "Mexico City"),
    ("2026-06-24", "20:00", "Sudáfrica", "Corea del Sur", "Monterrey"),
    ("2026-06-25", "14:00", "Ecuador", "Alemania", "New York"),
    ("2026-06-25", "14:00", "Curazao", "Costa de Marfil", "Philadelphia"),
    ("2026-06-25", "17:00", "Japón", "Suecia", "Dallas"),
    ("2026-06-25", "17:00", "Túnez", "Países Bajos", "Kansas City"),
    ("2026-06-25", "21:00", "Estados Unidos", "Turquía", "Los Angeles"),
    ("2026-06-25", "21:00", "Paraguay", "Australia", "San Francisco"),
    ("2026-06-26", "13:00", "Noruega", "Francia", "Boston"),
    ("2026-06-26", "13:00", "Senegal", "Irak", "Toronto"),
    ("2026-06-26", "16:00", "Cabo Verde", "Arabia Saudí", "Houston"),
    ("2026-06-26", "16:00", "Uruguay", "España", "Guadalajara"),
    ("2026-06-26", "21:00", "Egipto", "Irán", "Seattle"),
    ("2026-06-26", "21:00", "Nueva Zelanda", "Bélgica", "Vancouver"),
    ("2026-06-27", "13:00", "Panamá", "Inglaterra", "New York"),
    ("2026-06-27", "13:00", "Croacia", "Ghana", "Philadelphia"),
    ("2026-06-27", "16:00", "Colombia", "Portugal", "Miami"),
    ("2026-06-27", "16:00", "Rep. Dem. del Congo", "Uzbekistán", "Atlanta"),
    ("2026-06-27", "18:30", "Argelia", "Austria", "Kansas City"),
    ("2026-06-27", "18:30", "Jordania", "Argentina", "Dallas"),
]

def crear_tabla():
    conn = sqlite3.connect("mundial2026.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS calendario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            hora_colombia TEXT,
            local TEXT,
            visitante TEXT,
            ciudad TEXT
        )
    ''')
    cursor.execute("DELETE FROM calendario")
    for p in PARTIDOS:
        cursor.execute('''
            INSERT INTO calendario (fecha, hora_colombia, local, visitante, ciudad)
            VALUES (?, ?, ?, ?, ?)
        ''', p)
    conn.commit()
    conn.close()
    print(f"{len(PARTIDOS)} partidos cargados en el calendario.")

if __name__ == "__main__":
    crear_tabla()