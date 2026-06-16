# Configuración del proyecto Mundial 2026

# API Keys
API_FOOTBALL_KEY = "3215ab9d46msh20c819f88dc6c34p1a4725jsne8976947acc5"
OPENWEATHER_KEY = "ed8fee61261ba1feca1ab32e3de475b9"
FOOTBALL_DATA_KEY = "bc116ca4a81c4594bd73ae95f3856193"
NINJAS_KEY = "PskxNl4Kq4SyKvGBqAQdtf1NEhAenmyy1OIRLZeU"

# Base de datos
DATABASE_URL = "sqlite:///mundial2026.db"

# Pesos del modelo
PESOS = {
    "forma_reciente": 0.30,
    "estadisticas_avanzadas": 0.20,
    "tactica": 0.15,
    "calidad_plantilla": 0.15,
    "estado_actual": 0.10,
    "factores_externos": 0.05,
    "contexto_torneo": 0.03,
    "historial_h2h": 0.02,
}

# Configuración Monte Carlo
MONTE_CARLO_ITERACIONES = 100000

# Grupos oficiales Mundial 2026
GRUPOS = {
    "A": ["México", "Sudáfrica", "Corea del Sur", "República Checa"],
    "B": ["Canadá", "Bosnia y Herzegovina", "Catar", "Suiza"],
    "C": ["Brasil", "Marruecos", "Haití", "Escocia"],
    "D": ["Estados Unidos", "Paraguay", "Australia", "Turquía"],
    "E": ["Alemania", "Curazao", "Costa de Marfil", "Ecuador"],
    "F": ["Países Bajos", "Japón", "Suecia", "Túnez"],
    "G": ["Bélgica", "Egipto", "Irán", "Nueva Zelanda"],
    "H": ["España", "Cabo Verde", "Arabia Saudí", "Uruguay"],
    "I": ["Francia", "Senegal", "Irak", "Noruega"],
    "J": ["Argentina", "Argelia", "Austria", "Jordania"],
    "K": ["Portugal", "Rep. Dem. del Congo", "Uzbekistán", "Colombia"],
    "L": ["Inglaterra", "Croacia", "Ghana", "Panamá"],
}

# Lista plana de todos los equipos
EQUIPOS_MUNDIAL = [equipo for grupo in GRUPOS.values() for equipo in grupo]

# Ranking FIFA junio 2026
RANKING_FIFA = {
    "Argentina": 1, "España": 2, "Francia": 3, "Inglaterra": 4,
    "Portugal": 5, "Brasil": 6, "Marruecos": 7, "Países Bajos": 8,
    "Bélgica": 9, "Croacia": 10, "Alemania": 11, "Italia": 12,
    "Uruguay": 13, "Colombia": 14, "México": 15, "Estados Unidos": 16,
    "Suecia": 17, "Japón": 18, "Suiza": 19, "Irán": 20,
    "Dinamarca": 21, "Turquía": 22, "Ecuador": 23, "Austria": 24,
    "Corea del Sur": 25, "Nigeria": 26, "Canadá": 27, "Serbia": 28,
    "Polonia": 29, "Australia": 30, "Senegal": 31, "Noruega": 32,
    "Hungría": 33, "Argelia": 34, "Egipto": 35, "Costa de Marfil": 36,
    "República Checa": 37, "Rep. Checa": 37, "Escocia": 40,
    "Panamá": 41, "Paraguay": 45, "Sudáfrica": 50, "Túnez": 51,
    "Catar": 55, "Irak": 56, "Arabia Saudí": 57, "Arabia Saudita": 57,
    "Ghana": 60, "Cabo Verde": 64, "Uzbekistán": 66,
    "Rep. Dem. del Congo": 68, "RD Congo": 68, "República del Congo": 68,
    "Jordania": 74, "Bosnia y Herzegovina": 72, "Bosnia Herzegovina": 72,
    "Haití": 82, "Nueva Zelanda": 83, "Curazao": 85,
    "Gambia": 100, "Sudán": 119, "Mali": 47, "Benin": 38,
    "Zambia": 89, "Tanzania": 101, "Burkina Faso": 54,
    "Angola": 87, "Puerto Rico": 183, "Honduras": 75,
    "Nicaragua": 116, "El Salvador": 81, "Guatemala": 98,
    "Islandia": 70, "Kosovo": 96, "Georgia": 65,
    "Macedonia del Norte": 67, "Chipre": 109, "Luxemburgo": 86,
    "Gibraltar": 192, "San Marino": 210, "Andorra": 151,
    "Liechtenstein": 192, "Armenia": 93, "Bolivia": 76,
    "Perú": 44, "Chile": 43, "Venezuela": 43, "Jamaica": 61,
    "Trinidad y Tobago": 99, "Surinam": 83, "Bermuda": 99,
    "Bermudas": 99, "Aruba": 185, "Rep. Dominicana": 78,
    "República Dominicana": 78, "Mauritania": 104, "Mozambique": 94,
    "Madagascar": 100, "Ruanda": 122, "Uganda": 91,
    "Comoras": 130, "Comoros": 130, "Zimbabue": 114, "Chad": 159,
    "Esuatini": 139, "Rusia": 38, "Ucrania": 42, "Gales": 43,
    "Irlanda": 62, "Finlandia": 59, "Estonia": 112, "Letonia": 125,
    "Lituania": 127, "Moldavia": 147, "Albania": 63,
    "Montenegro": 69, "Eslovenia": 49, "Eslovaquia": 48,
    "Rumanía": 46, "Rumania": 46, "Bulgaria": 71, "Bielorrusia": 97,
    "Azerbaiyán": 107, "Tajikistán": 103, "Kuwait": 134,
    "Omán": 73, "Bahrein": 79, "Bahréin": 79, "Palestina": 90,
    "Siria": 84, "Corea del Norte": 108, "Kirguistán": 104,
    "China": 82, "Vietnam": 95, "India": 126, "Tailandia": 92,
    "Malasia": 132, "Guinea": 80, "Guinea Ecuatorial": 101,
    "Gabón": 77, "Camerún": 52, "Costa Rica": 53, "Grecia": 39,
    "Kazajistán": 102, "Kazajstán": 102,
    "Emiratos Árabes Unidos": 58, "Emiratos Árabes": 58,
    "Islas Feroe": 118, "Irlanda del Norte": 71,
    "Burundi": 129, "Togo": 115, "Niger": 111,
    "Sierra Leona": 113, "Lesoto": 146, "Namibia": 105,
    "Botsuana": 138, "Botswana": 138, "Israel": 85,
    "Malta": 170, "Rep. Centroafricana": 120,
    "Corea": 25, "Nigeria": 26,
}

# ID del Mundial en football-data.org
MUNDIAL_ID = 2000