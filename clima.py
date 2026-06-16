import requests
from datetime import datetime
from config import OPENWEATHER_KEY

def obtener_clima(ciudad):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": ciudad,
        "appid": OPENWEATHER_KEY,
        "units": "metric",
        "lang": "es"
    }
    r = requests.get(url, params=params)
    if r.status_code == 200:
        data = r.json()
        return {
            "ciudad": ciudad,
            "temperatura": round(data["main"]["temp"], 1),
            "sensacion": round(data["main"]["feels_like"], 1),
            "humedad": data["main"]["humidity"],
            "descripcion": data["weather"][0]["description"],
            "viento": round(data["wind"]["speed"] * 3.6, 1),
        }
    elif r.status_code == 401:
        print("Clave OpenWeather aún no activada.")
        return None
    else:
        print(f"Error {r.status_code}")
        return None

def obtener_clima_pronostico(ciudad, fecha_hora):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": ciudad,
        "appid": OPENWEATHER_KEY,
        "units": "metric",
        "lang": "es",
        "cnt": 40
    }
    r = requests.get(url, params=params)
    if r.status_code != 200:
        return obtener_clima(ciudad)

    data = r.json()
    fecha_partido = datetime.strptime(fecha_hora, "%Y-%m-%d %H:%M")
    mejor_pronostico = None
    menor_diff = float("inf")

    for item in data["list"]:
        fecha_item = datetime.fromtimestamp(item["dt"])
        diff = abs((fecha_item - fecha_partido).total_seconds())
        if diff < menor_diff:
            menor_diff = diff
            mejor_pronostico = item

    if mejor_pronostico:
        return {
            "ciudad": ciudad,
            "temperatura": round(mejor_pronostico["main"]["temp"], 1),
            "sensacion": round(mejor_pronostico["main"]["feels_like"], 1),
            "humedad": mejor_pronostico["main"]["humidity"],
            "descripcion": mejor_pronostico["weather"][0]["description"],
            "viento": round(mejor_pronostico["wind"]["speed"] * 3.6, 1),
            "hora_pronostico": datetime.fromtimestamp(mejor_pronostico["dt"]).strftime("%Y-%m-%d %H:%M"),
        }
    return obtener_clima(ciudad)

def factor_clima(clima):
    if not clima:
        return 0
    factor = 0
    if clima["temperatura"] > 30:
        factor += 0.1
    if clima["humedad"] > 80:
        factor += 0.05
    if clima["viento"] > 30:
        factor += 0.05
    return round(factor, 2)

if __name__ == "__main__":
    ciudad = input("Ciudad sede: ")
    fecha_hora = input("Fecha y hora del partido (YYYY-MM-DD HH:MM): ")
    clima = obtener_clima_pronostico(ciudad, fecha_hora)
    if clima:
        print(f"\nPronostico para {clima['ciudad']}:")
        print(f"  Hora consultada: {clima.get('hora_pronostico', 'actual')}")
        print(f"  Temperatura: {clima['temperatura']}°C (sensación {clima['sensacion']}°C)")
        print(f"  Humedad: {clima['humedad']}%")
        print(f"  Viento: {clima['viento']} km/h")
        print(f"  Condición: {clima['descripcion']}")
        print(f"  Factor impacto: {factor_clima(clima)}")