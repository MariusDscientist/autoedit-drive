
# 🖼️ AutoEdit Drive

> **Automated photo editing pipeline for real-world, high-volume photography workflows**

**AutoEdit Drive** es una aplicación de **línea de comandos (CLI) en Python** diseñada para automatizar el procesamiento de fotografías en contextos reales donde el **volumen y el tiempo importan más que el ajuste fino individual**.

Está pensada para flujos como:

- eventos deportivos y recreativos (ciclovías, carreras, entrenamientos)
- fotografía documental
- fotografía de naturaleza
- entregas rápidas para redes sociales

---

## 🎯 Motivación

Cuando se trabaja con **300–500 fotografías por sesión**, el flujo clásico:

> revisar → recortar → ajustar color → exportar → organizar → subir

se vuelve **costoso, lento y mentalmente agotador**.

En el estado actual del arte, **la edición manual sigue siendo superior en precisión y criterio estético**.  
Sin embargo, cuando el objetivo es **entregar resultados rápidamente**, ese enfoque no escala.

AutoEdit Drive nace aceptando explícitamente este trade-off:

| Dimensión | Manual | AutoEdit Drive |
|--------|--------|---------------|
| Control fino | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Consistencia | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Tiempo total | ❌ Horas | ✅ Minutos |
| Escalabilidad | ❌ | ✅ |

> 👉 pasar de **una tarde completa de edición**  
> 👉 a **2–3 minutos de procesamiento automático**

La meta del proyecto es **reducir progresivamente la brecha** entre automatización y criterio humano, sin sacrificar velocidad.

---

## ✨ ¿Qué hace AutoEdit Drive?

El pipeline completo realiza, de forma automática:

- 📐 **Recorte inteligente** mediante detección de objetos con **YOLOv8 (nano)**
- 🎯 Cálculo de **área de interés (ROI)** ponderada por clase
- 🖼️ Recortes optimizados para **Instagram (5:4 / 4:5)**
- 🎨 Aplicación de **presets automáticos** de color y luminancia
- 🧾 Inserción de **watermark configurable**
- ☁️ Subida automática a **Google Drive**
- 📂 Flujo completo desde carpeta local → carpeta remota

Todo se ejecuta desde **un único comando CLI**.

---

## 🧠 Arquitectura del pipeline

### 1️⃣ Detección de área de interés (YOLOv8)

Se utiliza **YOLOv8 (versión nano)** por su equilibrio entre velocidad y precisión.

El modelo detecta objetos comunes como:

- personas
- bicicletas
- otros elementos relevantes según el contexto

Cada clase detectada se pondera mediante pesos configurables:



```python
CLASS_WEIGHTS = {
    0: 1.0,  # persona
    1: 0.8   # bicicleta
}
````

Esto permite construir un **centro de interés global**, evitando:

* que objetos pequeños del fondo dominen el encuadre
* que detecciones irrelevantes desplacen el recorte

Además:

* se descartan bounding boxes demasiado pequeñas
* se priorizan detecciones cercanas al centro visual

---

### 2️⃣ Recorte inteligente

Con el centro de interés calculado:

* se determina automáticamente la orientación de la imagen
* se aplica un recorte **5:4 o 4:5**
* se maximiza el área útil sin perder el sujeto principal

Este formato fue elegido por su **mejor rendimiento visual en Instagram**.

---

### 3️⃣ Presets automáticos de color

Una vez recortada, la imagen pasa por ajustes automáticos implementados con **Pillow (PIL)** y **OpenCV**, basados en análisis simples:

* histogramas
* promedios de luminancia y color

Ajustes aplicados:

* corrección de luminancia y exposición
* aumento moderado de saturación
* ajuste leve de contraste
* ligera calidez de color

> El objetivo **no es estilizar agresivamente**,
> sino llevar cada imagen a un punto **consistente, agradable y publicable**.

---

### 4️⃣ Watermark

Se añade un watermark configurable:

* tamaño relativo
* opacidad
* margen
* conversión automática a blanco

Útil para flujos comerciales o marca personal.

---

### 5️⃣ Integración con Google Drive

El pipeline incluye autenticación OAuth con **Google Drive** usando **PyDrive**.

Flujo:

1. Lectura desde carpeta local
2. Procesamiento secuencial
3. Guardado en carpeta temporal
4. Subida automática a una carpeta específica en Drive

Esto elimina pasos manuales de exportación y carga.

---

## 📁 Estructura del proyecto

```text
autoEdit-drive/
├── autoEdit/
│   ├── autoedit.py        # CLI
│   ├── pipeline.py        # Orquestador del pipeline
│   ├── config.py          # Configuración global
│   ├── presets.py         # Ajustes automáticos de color
│   ├── crop.py            # Lógica de recorte
│   ├── watermark.py       # Watermark
│   ├── boxes.py           # Utilidades de detección
│   ├── yolo_name.py       # Manejo de clases YOLO
│   └── __init__.py
├── fotos/                 # Carpeta de entrada (ejemplo)
├── temp/                  # Carpeta de salida
├── client_secrets.json    # Credenciales Google Drive (NO versionar)
├── yolov8n.pt             # Modelo YOLO
├── LICENSE
└── README.md
```

---

## 🚀 Instalación

```bash
git clone git@github.com:MariusDscientist/autoedit-drive.git
cd autoedit-drive
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🔑 Configuración de Google Drive

1. Crear un proyecto en **Google Cloud Console**
2. Habilitar **Google Drive API**
3. Crear credenciales OAuth (*Desktop Application*)
4. Descargar el archivo como:

```text
client_secrets.json
```

⚠️ **No versionar este archivo**

---

## ▶️ Uso del CLI

```bash
python -m autoEdit.autoedit \
  --input "fotos" \
  --output "./temp" \
  --drive-folder "ID_DE_CARPETA_EN_DRIVE" \
  --water-mark "fotos/logo/logo.png" \
  --log
```

### Argumentos disponibles

| Argumento        | Descripción                     |
| ---------------- | ------------------------------- |
| `--input`        | Carpeta local con imágenes      |
| `--output`       | Carpeta local de salida         |
| `--drive-folder` | ID de carpeta en Google Drive   |
| `--water-mark`   | Ruta al logo PNG                |
| `--preview`      | Procesa una sola imagen         |
| `--log`          | Guarda un log del procesamiento |

---



## 🧩 Diseño modular

Cada módulo cumple una única responsabilidad:

* `presets.py` → color y luz
* `crop.py` → encuadre
* `watermark.py` → marca de agua
* `pipeline.py` → orquestación
* `autoedit.py` → interfaz CLI

Esto facilita mantenimiento, pruebas y evolución del sistema.



## 🧑‍💻 Autor

**Jhon Mario Cano Torres**
Científico de datos · Fotografía · Automatización
🇨🇴 Colombia




