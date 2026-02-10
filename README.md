# 🌱 Sistema IoT Cloud para Monitorización de Invernaderos (M5Stack + ThingsBoard)

Este proyecto implementa una solución **IoT (Internet of Things)** completa para la digitalización de un invernadero. El sistema se basa en una arquitectura centralizada en la nube, donde el dispositivo recoge y procesa la telemetría, pero la lógica de control y gestión de alarmas reside en la plataforma **ThingsBoard**.

## 👥 Autores
Proyecto realizado para la asignatura de *Internet de Nueva Generación* por:
* **Raúl Sánchez Ibáñez**
* **Carmen Sánchez del Vas**

## 🎯 Objetivo
Desarrollar un sistema de telemetría bidireccional capaz de:
1.  **Digitalizar** variables ambientales críticas (CO2, Temperatura, Humedad y Nivel de Agua).
2.  **Visualizar** el estado del cultivo en tiempo real desde la nube.
3.  **Actuar** remotamente sobre el dispositivo mediante comandos RPC enviados desde el servidor.

## ⚙️ Arquitectura Técnica

### 1. Nodo de Sensores (Device Layer)
* **Hardware:** M5Stack Fire (MicroPython).
* **Pre-procesamiento Local:** El dispositivo realiza cálculos matemáticos in-situ (ej: conversión de distancia láser a porcentaje de volumen de agua) antes de enviar el dato.
* **Sensores:**
    * `Unit SCD40`: Monitorización ambiental (CO2, Temp, Humedad).
    * `Unit ToF` (Time of Flight): Medición láser precisa del nivel del tanque.
* **Interfaz Humano-Máquina (HMI):** Feedback visual (LEDs RGB) y sonoro que responde a las órdenes de la nube.

### 2. Capa de Comunicación
* **Protocolo:** MQTT seguro (Puerto 8883) sobre SSL/TLS.
* **Seguridad:** Autenticación por Token y encriptación de datos.

### 3. El Cerebro (Cloud Layer - ThingsBoard)
* **Motor de Reglas (Rule Engine):** Es el núcleo del sistema. Analiza los datos entrantes y decide el estado del invernadero (Normal, Warning, Critical).
* **RPC (Remote Procedure Calls):** Si la nube detecta una anomalía, envía automáticamente un comando al M5Stack para que active sus sirenas o cambie el color de la pantalla.
* **Dashboard:** Panel de control para la supervisión agrícola remota.

## 📂 Estructura del Repositorio
* `proyecto.py`: Código fuente del firmware (MicroPython). Incluye la lógica de lectura I2C, máquina de estados para el display y cliente MQTT.
* `Memoria.pdf`: Memoria técnica detallada con esquemas de conexión, diagramas de flujo y pruebas de validación.

---
*Ciencia e Ingeniería de Datos - 2026*
