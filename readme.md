
# 🖼️ AutoEdit Drive

> **Automated photo editing pipeline for real-world, high-volume photography workflows**

**AutoEdit Drive** is a **Python-based command-line application (CLI)** designed to automate photo processing in real-world scenarios where **volume and turnaround time matter more than fine-grained manual adjustments**.

It is built for workflows such as:

* sports and recreational events (bike lanes, races, training sessions)
* documentary photography
* nature photography
* fast delivery for social media

---

## 🎯 Motivation

When working with **300–500 photos per session**, the traditional workflow:

> review → crop → color adjust → export → organize → upload

quickly becomes **time-consuming, slow, and mentally exhausting**.

In the current state of the art, **manual editing still produces better results** in terms of precision and aesthetic judgment.
However, when the goal is **fast delivery**, that approach does not scale.

AutoEdit Drive is built around an explicit trade-off:

| Dimension    | Manual  | AutoEdit Drive |
| ------------ | ------- | -------------- |
| Fine control | ⭐⭐⭐⭐⭐   | ⭐⭐⭐            |
| Consistency  | ⭐⭐⭐⭐    | ⭐⭐⭐            |
| Total time   | ❌ Hours | ✅ Minutes      |
| Scalability  | ❌       | ✅              |

> 👉 from **a full afternoon of manual editing**
> 👉 to **2–3 minutes of automated processing**

The long-term goal is to **progressively reduce the gap** between automation and human judgment—without sacrificing speed.

---

## ✨ What does AutoEdit Drive do?

The full pipeline automatically performs:

* 📐 **Smart cropping** using object detection with **YOLOv8 (nano)**
* 🎯 **Region of Interest (ROI)** computation weighted by object class
* 🖼️ Cropping optimized for **Instagram formats (5:4 / 4:5)**
* 🎨 **Automatic color and luminance presets**
* 🧾 **Configurable watermark** insertion
* ☁️ Automatic upload to **Google Drive**
* 📂 End-to-end flow from local folder → remote folder

All of this runs through **a single CLI command**.

---

## 🧠 Pipeline architecture

### 1️⃣ Region of Interest detection (YOLOv8)

The system uses **YOLOv8 (nano version)** for its balance between speed and accuracy.

The model detects common objects such as:

* people
* bicycles
* other context-dependent elements

Each detected class is weighted using configurable values:

```python
CLASS_WEIGHTS = {
    0: 1.0,  # person
    1: 0.8   # bicycle
}
```

This allows the system to compute a **global center of interest**, preventing:

* small background objects from dominating the crop
* irrelevant detections from shifting the framing

Additionally:

* very small bounding boxes are discarded
* detections closer to the visual center are prioritized

---

### 2️⃣ Smart cropping

Once the center of interest is computed:

* image orientation is detected automatically
* a **5:4 or 4:5** crop is applied
* the usable area is maximized while keeping the main subject intact

These aspect ratios were chosen due to their **optimal performance on Instagram**.

---

### 3️⃣ Automatic color presets

After cropping, the image goes through automatic adjustments implemented with **Pillow (PIL)** and **OpenCV**, based on simple image analysis:

* histograms
* luminance and color averages

Applied adjustments include:

* luminance and exposure correction
* moderate saturation increase
* light contrast adjustment
* subtle color warmth

> The goal is **not aggressive stylization**,
> but bringing each image to a **consistent, pleasant, and publishable state**.

---

### 4️⃣ Watermark

A configurable watermark is applied to the final image:

* relative size
* opacity
* margin
* automatic conversion to white

This is especially useful for commercial workflows or personal branding.

---

### 5️⃣ Google Drive integration

The pipeline includes OAuth authentication with **Google Drive** using **PyDrive**.

Workflow:

1. Images are read from a local folder
2. Processed sequentially
3. Saved to a temporary output directory
4. Automatically uploaded to a specific Drive folder

This removes manual export and upload steps.

---

## 📁 Project structure

```text
autoEdit-drive/
├── autoEdit/
│   ├── autoedit.py        # CLI entry point
│   ├── pipeline.py        # Pipeline orchestrator
│   ├── config.py          # Global configuration
│   ├── presets.py         # Automatic color presets
│   ├── crop.py            # Cropping logic
│   ├── watermark.py       # Watermark logic
│   ├── boxes.py           # Detection utilities
│   ├── yolo_name.py       # YOLO class handling
│   └── __init__.py
├── fotos/                 # Input folder (example)
├── temp/                  # Output folder
├── client_secrets.json    # Google Drive credentials (DO NOT COMMIT)
├── yolov8n.pt             # YOLO model
├── LICENSE
└── README.md
```

---

## 🚀 Installation

```bash
git clone git@github.com:MariusDscientist/autoedit-drive.git
cd autoedit-drive
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🔑 Google Drive configuration

1. Create a project in **Google Cloud Console**
2. Enable **Google Drive API**
3. Create OAuth credentials (*Desktop Application*)
4. Download the file as:

```text
client_secrets.json
```

⚠️ **Do not commit this file to the repository**

---

## ▶️ CLI usage

```bash
python -m autoEdit.autoedit \
  --input "fotos" \
  --output "./temp" \
  --drive-folder "DRIVE_FOLDER_ID" \
  --water-mark "fotos/logo/logo.png" \
  --log
```

### Available arguments

| Argument         | Description                        |
| ---------------- | ---------------------------------- |
| `--input`        | Local input folder with images     |
| `--output`       | Local output folder                |
| `--drive-folder` | Destination Google Drive folder ID |
| `--water-mark`   | Path to PNG logo                   |
| `--preview`      | Process a single image and exit    |
| `--log`          | Save a processing log              |

---

## 🧩 Modular design

Each module has a single, well-defined responsibility:

* `presets.py` → color and luminance
* `crop.py` → framing logic
* `watermark.py` → watermark handling
* `pipeline.py` → pipeline orchestration
* `autoedit.py` → CLI interface

This structure simplifies maintenance, testing, and future evolution.

---

## 🧑‍💻 Author

**Jhon Mario Cano Torres**
Data Scientist · Photography · Automation
🇨🇴 Colombia

