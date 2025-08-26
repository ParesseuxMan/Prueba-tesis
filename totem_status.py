import requests
import psutil
import time
import platform
from datetime import datetime
import subprocess

SERVER_URL = "http://100.98.232.35:5000/registro"  # IP de tu servidor

def get_uptime():
    return time.time() - psutil.boot_time()

def get_latency(server_ip="100.98.232.35"):
    try:
        output = subprocess.check_output(["ping", "-c", "1", server_ip])
        line = output.decode().split("\n")[1]
        time_ms = line.split("time=")[1].split(" ")[0]
        return float(time_ms)
    except:
        return None

def get_system_info():
    ram = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=1)
    return {
        "uptime_sec": round(get_uptime(), 2),
        "latency_ms": get_latency(),
        "ram_total_mb": round(ram.total / (1024*1024), 2),
        "ram_used_mb": round(ram.used / (1024*1024), 2),
        "cpu_percent": cpu,
        "system": platform.system(),
        "release": platform.release()
    }

def enviar_datos():
    data = get_system_info()
    data.update({
        "RUT": "TOTEM-01",  # Identificador único del tótem
        "ubicacion": "Entrada Principal",
        "hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "lat": -33.4378,   # Coordenadas de prueba
        "lon": -70.6505
    })
    try:
        response = requests.post(SERVER_URL, json=data)
        print(response.json())
    except Exception as e:
        print("Error al enviar datos:", e)

if __name__ == "__main__":
    while True:
        enviar_datos()
        time.sleep(10)  # Cada 10 segundos
