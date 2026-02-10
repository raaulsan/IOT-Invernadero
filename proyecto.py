#PROYECTO FINAL IOT RAUL SANCHEZ IBAÑEZ Y CARMEN SANCHEZ DEL VAS


import os, sys, io
import M5
from M5 import *
import network
import json
import time
from hardware import I2C
from hardware import Pin
from umqtt.simple import MQTTClient
from hardware import RGB
from unit import ToFUnit 


# CONFIGURACIÓN WIFI Y THINGSBOARD

SSID = '********'
PASSWORD = '********'

mqttclient = None
mqttuser = "CarmenRaul"
mqttpass = "*******"
mqtturl = "mqtt.eu.thingsboard.cloud"
mqttclientid = "ingCarmenRaul"
puerto = 8883

# Topics 
topic_telemetria = "v1/devices/me/telemetry"
topic_atributos = "v1/devices/me/attributes"
topic_rpc_sub = "v1/devices/me/rpc/request/+"


# CONFIGURACIÓN I2C Y SENSORES

SCD40_ADDR = 0x62
i2c0 = None
wifiFire = None
rgb15 = None
tof = None

# Altura del bote en CENTÍMETROS
ALTURA_BOTE = 20        

# Variable para controlar qué mostramos en pantalla (0=Temp, 1=Hum, 2=CO2)
contador_pantalla = 0 

# Funciones de Conexión
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Conectando a Wi-Fi:", ssid)
        wlan.connect(ssid, password)
        t0 = time.ticks_ms()
        while not wlan.isconnected():
            if time.ticks_diff(time.ticks_ms(), t0) > 10000:
                print("Error: Timeout WiFi")
                return None
            time.sleep(0.5)
    print("Conectado:", wlan.ifconfig())
    return wlan

def ensure_mqtt_connected():
    global mqttclient
    try:
        mqttclient.ping()
        return
    except Exception:
        pass
    try:
        print("Conectando MQTT...")
        mqttclient.connect()
        mqttclient.subscribe(topic_rpc_sub)
        print("MQTT Conectado.")
    except Exception as e:
        print("Error MQTT:", e)


def mostrar_alerta_pantalla(mensaje, color):
    M5.Lcd.clear()
    M5.Lcd.setCursor(10, 40)
    M5.Lcd.setTextSize(3)
    M5.Lcd.setTextColor(color)
    M5.Lcd.print("¡ALERTA!")
    
    M5.Lcd.setCursor(10, 90)
    M5.Lcd.setTextSize(2)
    M5.Lcd.setTextColor(0xFFFFFF) # Blanco
    M5.Lcd.print(mensaje)


def alerta_agua_baja():
    global rgb15
    print("ALERTA: Nivel de agua bajo")
    mostrar_alerta_pantalla("RELLENAR AGUA", 0xFFFFFF)
    for i in range(3):
        rgb15.fill_color(0xFFFFFF) 
        time.sleep(0.3)
        rgb15.fill_color(0x000000) 
        time.sleep(0.3)

#  TEMPERATURA 
def alerta_temp_critica():
    global rgb15
    print("EJECUTANDO: Alerta Temperatura Muy Alta")
    mostrar_alerta_pantalla("TEMP CRITICA", 0xFF0000)
    for i in range(5):
        rgb15.fill_color(0xFF0000)
        M5.Speaker.tone(2000, 300) 
        time.sleep(0.3)
        rgb15.fill_color(0x000000) 
        time.sleep(0.3)

def alerta_temp_alta():
    global rgb15
    print("EJECUTANDO: Alerta Temperatura Alta")
    rgb15.fill_color(0xFF0000) # ROJO
    M5.Speaker.tone(2000, 1000) 
    mostrar_alerta_pantalla("TEMP MUY ALTA", 0xFF0000)

def alerta_temp_baja():
    global rgb15
    print("EJECUTANDO: Alerta Temperatura Baja")
    rgb15.fill_color(0x0000FF) # AZUL
    M5.Speaker.tone(500, 1000)  
    mostrar_alerta_pantalla("TEMP MUY BAJA", 0x0000FF)

#  HUMEDAD 
def alerta_hum_alta():
    global rgb15
    print("EJECUTANDO: Alerta Humedad Alta")
    rgb15.fill_color(0xFFA500) # NARANJA
    M5.Speaker.tone(2000, 1000)
    mostrar_alerta_pantalla("HUMEDAD ALTA", 0xFFA500)

def alerta_hum_baja():
    global rgb15
    print("EJECUTANDO: Alerta Humedad Baja")
    rgb15.fill_color(0x00FFFF) # CYAN
    M5.Speaker.tone(500, 1000)
    mostrar_alerta_pantalla("HUMEDAD BAJA", 0x00FFFF)

#  CO2 
def alerta_co2_alta():
    global rgb15
    print("EJECUTANDO: Alerta CO2 Alta")
    rgb15.fill_color(0xFF00FF) # MAGENTA 
    M5.Speaker.tone(3000, 200)
    time.sleep(0.3)
    M5.Speaker.tone(3000, 200)
    mostrar_alerta_pantalla("NIVEL CO2 CRITICO", 0xFF00FF)

def alerta_co2_baja():
    global rgb15
    print("EJECUTANDO: Alerta CO2 Baja")
    rgb15.fill_color(0x00FF00) # VERDE
    M5.Speaker.tone(500, 500)
    mostrar_alerta_pantalla("CO2 BAJO (OK)", 0x00FF00)

def sub_cb(topic, msg):
    print("RPC Recibido:", topic, msg)
    topic_str = topic.decode('utf-8')
    msg_str = msg.decode('utf-8')
    
    if topic_str.startswith('v1/devices/me/rpc/request/'):
        try:
            data = json.loads(msg_str)
            metodo = data['method']
            
            if metodo == 'alerta_temp_alta': alerta_temp_alta()
            elif metodo == 'alerta_temp_baja': alerta_temp_baja()
            elif metodo == 'alerta_hum_alta': alerta_hum_alta()
            elif metodo == 'alerta_hum_baja': alerta_hum_baja()
            elif metodo == 'alerta_co2_alta': alerta_co2_alta()
            elif metodo == 'alerta_co2_baja': alerta_co2_baja()
            elif metodo == 'alerta_agua_baja': alerta_agua_baja()
            elif metodo == 'alerta_temp_critica': alerta_temp_critica()
            else: print("Metodo RPC desconocido:", metodo)
                
        except Exception as e:
            print("Error procesando RPC:", e)


def dibujar_pantalla(titulo, valor, unidad, color_texto):
    M5.Lcd.clear()
    M5.Lcd.setCursor(10, 10)
    M5.Lcd.setTextSize(3)
    M5.Lcd.setTextColor(0xffffff) 
    M5.Lcd.print(titulo)
    
    M5.Lcd.setCursor(10, 60)
    M5.Lcd.setTextSize(5)
    M5.Lcd.setTextColor(color_texto)
    
    if isinstance(valor, float):
        M5.Lcd.print("{:.1f}".format(valor))
    else:
        M5.Lcd.print("{}".format(valor))
        
    M5.Lcd.setCursor(10, 110)
    M5.Lcd.setTextSize(3)
    M5.Lcd.setTextColor(0xaaaaaa) 
    M5.Lcd.print(unidad)

def setup():
    global wifiFire, i2c0, mqttclient, rgb15, tof

    M5.begin()
    Widgets.setRotation(1)
    Widgets.fillScreen(0x222222)
    
    rgb15 = RGB(io=15, n=10, type="SK6812")
    rgb15.set_brightness(30)
    rgb15.fill_color(0x000000)

    print("Iniciando I2C...")
    i2c0 = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)

    #  ARRANQUE SCD40 
    try:
        i2c0.writeto(SCD40_ADDR, b'\x21\xb1')
        print("SCD40 inicializado correctamente.")
        time.sleep(1) 
    except Exception as e:
        print("Error iniciando SCD40:", e)
        M5.Lcd.print("Error Sensor SCD40")

    #  ARRANQUE TOF 
    try:
        print("Iniciando ToF...")
        tof = ToFUnit(i2c=i2c0)
    except Exception as e: print("Error init ToF:", e)

    wifiFire = connect_wifi(SSID, PASSWORD)
    
    ssl_params = {"server_hostname": mqtturl}
    mqttclient = MQTTClient(client_id=mqttclientid,
                            server=mqtturl,
                            port=puerto,
                            user=mqttuser,
                            password=mqttpass,
                            keepalive=60,
                            ssl=True,
                            ssl_params=ssl_params)
    mqttclient.set_callback(sub_cb)
    ensure_mqtt_connected()

def loop():
    global wifiFire, mqttclient, i2c0, contador_pantalla, rgb15, tof
    M5.update()
    
    co2 = 0
    temperatura = 0.0
    humedad = 0.0
    dist_cm = 0
    nivel_agua = 0
    lectura_ok = False

    #  1. LECTURA SCD40 (Aire) 
    try:
        i2c0.writeto(SCD40_ADDR, b'\xec\x05')
        time.sleep(0.1) 
        data = i2c0.readfrom(SCD40_ADDR, 9)
        co2 = (data[0] << 8) | data[1]
        temp_raw = (data[3] << 8) | data[4]
        temperatura = -45 + 175 * (temp_raw / 65535.0)
        hum_raw = (data[6] << 8) | data[7]
        humedad = 100 * (hum_raw / 65535.0)
        lectura_ok = True
    except Exception as e:
        print("Error leyendo sensor SCD40:", e)

    #  2. LECTURA TOF (Agua) 
    if tof:
        try:
            # Asumimos que el sensor da CENTIMETROS directamente
            dist_cm = tof.get_distance() 
            
            if dist_cm < ALTURA_BOTE:
                nivel_agua = 100 - ((dist_cm / ALTURA_BOTE) * 100)
            else:
                nivel_agua = 0
                
            if nivel_agua < 0: nivel_agua = 0
        except: pass

    #  3. PANTALLA Y ENVÍO 
    if lectura_ok:
        rgb15.fill_color(0x000000)
        
        #  Lógica de Pantalla 
        if contador_pantalla == 0:
            dibujar_pantalla("TEMP", temperatura, "Grados C", 0xffaa00) 
            contador_pantalla = 1
        elif contador_pantalla == 1:
            dibujar_pantalla("HUMEDAD", humedad, "% RH", 0x00aaff) 
            contador_pantalla = 2
        else:
            color_co2 = 0xff0000 if co2 > 1000 else 0x00ff00
            dibujar_pantalla("NIVEL CO2", co2, "ppm", color_co2) 
            contador_pantalla = 0

        #  4. ENVIAR A THINGSBOARD E IMPRIMIR 
        if wifiFire and wifiFire.isconnected():
            ensure_mqtt_connected()
            try:
                telemetry_data = {
                    "temperature": temperatura,
                    "humidity": humedad,
                    "co2": co2,
                    "water_level_percent": nivel_agua,
                    "distance_mm": dist_cm * 10 # Convertimos a mm para ThingsBoard
                }
                mqttclient.publish(topic_telemetria, json.dumps(telemetry_data))
                
                attributes_data = {"status": "Online"}
                mqttclient.publish(topic_atributos, json.dumps(attributes_data))
                
                mqttclient.check_msg()
                
               
                print(f"Enviado: CO2={co2}, T={temperatura:.1f}, H={humedad:.1f}%, WaterLevel={nivel_agua:.1f}%, Dist={dist_cm}cm")
                
            except Exception as e:
                print("Error enviando MQTT:", e)

    time.sleep(5) 

if __name__ == '__main__':
    try:
        setup()
        while True:
            loop()
    except (Exception, KeyboardInterrupt) as e:
        print(e)
