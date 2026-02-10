# 🌱 Sistema IoT para la Gestión Inteligente de un Invernadero

Este proyecto implementa una solución completa de **IoT (Internet of Things)** para la monitorización y control automatizado de un invernadero. El sistema utiliza una arquitectura híbrida **Edge-Cloud** para garantizar la seguridad del cultivo mediante la gestión de variables críticas (CO2, Temperatura, Humedad y Nivel de Agua).

## 👥 Autores
Proyecto realizado para la asignatura de *Internet de Nueva Generación* por:
* **Raúl Sánchez Ibáñez**
* **Carmen Sánchez del Vas**

## 🎯 Objetivo
Digitalizar la gestión agrícola sustituyendo la supervisión manual por un sistema autónomo capaz de:
1.  **Monitorizar** en tiempo real la salud del cultivo.
2.  **Alertar** localmente (Edge) ante situaciones críticas (ej: falta de agua o temperatura extrema).
3.  **Gestionar** remotamente (Cloud) el sistema mediante un dashboard de supervisión y control.

## ⚙️ Arquitectura Técnica

### 1. Capa de Percepción (Hardware & Edge Computing)
* **Dispositivo Principal:** M5Stack Fire (MicroPython).
* **Sensores:**
    * `Unit SCD40`: Medición de precisión de CO2 (ppm), Temperatura y Humedad.
    * `Unit ToF` (Time of Flight): Medición láser del nivel del tanque de agua (sin contacto).
* **Actuadores Locales:** Feedback visual (Tira LED RGB) y sonoro (Speaker) para alertas in-situ.

### 2. Capa de Red y Comunicación
* **Protocolo:** MQTT sobre SSL/TLS (Puerto 8883) para máxima seguridad.
* **Conectividad:** Wi-Fi.

### 3. Capa de Aplicación (Cloud - ThingsBoard)
* **Dashboard:** Visualización de telemetría en tiempo real.
* **Motor de Reglas (Rule Chains):** Lógica de negocio en la nube para detectar anomalías y enviar comandos RPC de vuelta al dispositivo.
* **Alarmas:** Gestión del ciclo de vida de incidencias (Critical, Warning, Cleared).

## 🚀 Funcionalidades Clave
* **Alertas Multimodales:** El dispositivo cambia de color y emite patrones sonoros específicos según la urgencia (ej: *Rojo+Sirena* para Tª Crítica vs *Azul* para Tª Baja).
* **Bidireccionalidad (RPC):** El sistema no solo envía datos, sino que recibe órdenes desde la nube para actuar sobre el hardware.
* **Gestión Hídrica:** Algoritmo que calcula el porcentaje de agua restante basándose en la distancia al fondo del depósito.

## 📂 Estructura del Repositorio
* `proyecto.py`: Código fuente del firmware (MicroPython). Incluye la lógica de lectura I2C, máquina de estados para el display y cliente MQTT.
* `Memoria.pdf`: Memoria técnica detallada con esquemas de conexión, diagramas de flujo y pruebas de validación.

---
*Ciencia e Ingeniería de Datos - 2026*
