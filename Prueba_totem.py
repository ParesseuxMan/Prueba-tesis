import requests
import time
import socket
import psutil
import subprocess
import shutil
import os

SERVER_URL = "http://192.168.7.52:3000/api/totem"  # Cambia la IP si tu server es otra

# 📍 Localización fija del tótem
def obtener_localizacion():
    return -33.3865, -70.6144

# 📡 Ping a un host (Google 8.8.8.8 por defecto)
def obtener_ping(host="8.8.8.8"):
    try:
        output = subprocess.check_output(["ping", "-c", "1", host], universal_newlines=True)
        for line in output.split("\n"):
            if "time=" in line:
                return float(line.split("time=")[1].split(" ")[0])
    except Exception:
        return None

# 🔌 Tipo de conexión detectada
def tipo_conexion():
    interfaces = psutil.net_if_addrs()
    if "wlan0" in interfaces or any("wl" in i for i in interfaces.keys()):
        return "WiFi"
    elif "eth0" in interfaces or any("en" in i for i in interfaces.keys()):
        return "Ethernet"
    else:
        return "Desconocido"

# 💾 Uso de RAM
def obtener_ram():
    mem = psutil.virtual_memory()
    return f"{int(mem.used/1024/1024)}MB / {int(mem.total/1024/1024)}MB"

# 🖥️ Uso de CPU
def obtener_cpu():
    return f"{psutil.cpu_percent()}%"

# 💽 Espacio en disco
def obtener_disco():
    total, used, free = shutil.disk_usage("/")
    return f"{int(free/1024/1024)}MB libres / {int(total/1024/1024)}MB totales"

# 🌡️ Temperatura CPU
def obtener_temp_cpu():
    try:
        temps = psutil.sensors_temperatures()
        if "coretemp" in temps:
            return f"{temps['coretemp'][0].current} °C"
        return "N/A"
    except Exception:
        return "N/A"

# 🔋 Estado de batería (N/A si no existe)
def obtener_bateria():
    try:
        batt = psutil.sensors_battery()
        if batt:
            return f"{batt.percent}%"
        else:
            return "N/A"
    except Exception:
        return "N/A"

# 🎮 Estado de GPU Intel
def obtener_gpu_intel():
    try:
        base_path = "/sys/class/drm/card0/device/hwmon"
        if not os.path.exists(base_path):
            return "No Intel GPU encontrada"

        hwmon_dir = os.path.join(base_path, os.listdir(base_path)[0])

        # Temperatura
        temp_path = os.path.join(hwmon_dir, "temp1_input")
        temperatura = None
        if os.path.exists(temp_path):
            with open(temp_path, "r") as f:
                temperatura = int(f.read().strip()) / 1000  # miligrados → °C

        # Potencia consumida
        power_path = os.path.join(hwmon_dir, "power1_average")
        potencia = None
        if os.path.exists(power_path):
            with open(power_path, "r") as f:
                potencia = int(f.read().strip()) / 1000000  # microwatts → watts

        return {
            "nombre": "Intel iGPU",
            "temperatura": f"{temperatura:.1f} °C" if temperatura else "N/A",
            "potencia": f"{potencia:.1f} W" if potencia else "N/A"
        }

    except Exception as e:
        return f"Error GPU Intel: {e}"

# 🔄 Bucle principal de monitoreo
while True:
    lat, lng = obtener_localizacion()
    data = {
        "id": socket.gethostname(),
        "lat": lat,
        "lng": lng,
        "estado": "normal",
        "ping": obtener_ping() or 0,
        "conexion": tipo_conexion(),
        "ram": obtener_ram(),
        "cpu": obtener_cpu(),
        "disco": obtener_disco(),
        "temp_cpu": obtener_temp_cpu(),
        "gpu": obtener_gpu_intel(),
        "bateria": obtener_bateria(),
        "timestamp": time.strftime("%H:%M:%S")
    }
    try:
        print("Enviando:", data)
        requests.post(SERVER_URL, json=data, timeout=5)
    except Exception as e:
        print("Error al enviar:", e)
    time.sleep(5)
