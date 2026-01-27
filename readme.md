<div align="center">

# 🖼️ AutoEdit Drive

**An automated, high-throughput image processing pipeline for professional and enthusiast photographers.**

</div>

**AutoEdit Drive** is a Python-based command-line application designed to automate the entire photo editing workflow, from initial selection to final cloud upload. It is engineered for scenarios where **processing volume and rapid turnaround are critical**, such as event photography, sports, documentary work, or high-volume social media content creation.

---

### TOC
*   [🎯 **Motivation**](#-motivation)
*   [✨ **Key Features**](#-key-features)
*   [🧠 **Technical Deep Dive: The Processing Pipeline**](#-technical-deep-dive-the-processing-pipeline)
    *   [1. Object Detection for ROI Identification](#1-object-detection-for-roi-identification-yolov8)
    *   [2. Intelligent Cropping Logic](#2-intelligent-cropping-logic)
    *   [3. Automated Image Enhancement](#3-automated-image-enhancement)
    *   [4. Dynamic Watermarking](#4-dynamic-watermarking)
    *   [5. Cloud Integration](#5-cloud-integration)
*   [🧩 **System Architecture & Modularity**](#-system-architecture--modularity)
*   [🚀 **Installation & Configuration**](#-installation--configuration)
    *   [Prerequisites](#prerequisites)
    *   [Installation](#installation)
    *   [Google Drive API Setup](#google-drive-api-setup)
*   [▶️ **Usage (CLI)**](#️-usage-cli)
*   [🛣️ **Roadmap**](#️-roadmap)
*   [🧑‍💻 **Author**](#-author)

---

## 🎯 Motivation

A typical professional photography session can generate **300–500 images**. The traditional workflow—manual review, cropping, color correction, export, and organization—is **time-consuming, repetitive, and mentally taxing**. While manual editing offers unparalleled precision, it doesn't scale.

AutoEdit Drive was built to bridge this gap, trading minute manual control for massive gains in speed and scalability.

| Dimension          | Manual Editing | AutoEdit Drive         |
| ------------------ | -------------- | ---------------------- |
| **Fine-Grained Control** | ⭐⭐⭐⭐⭐      | ⭐⭐⭐                   |
| **Consistency**      | ⭐⭐⭐⭐         | ⭐⭐⭐⭐                  |
| **Total Time**       | ❌ **Hours**    | ✅ **Minutes**           |
| **Scalability**      | ❌              | ✅                     |

> This pipeline transforms a multi-hour editing session into a **2–3 minute automated process**.

---

## ✨ Key Features

*   **Smart Object-Aware Cropping**: Uses **YOLOv8** to identify the Region of Interest (ROI) and automatically crop images to social media-friendly aspect ratios (4:5 / 5:4).
*   **Automatic Image Enhancement**: Applies presets for luminance, contrast, saturation, and color temperature, ensuring a consistent and professional look across all photos.
*   **Configurable Watermarking**: Dynamically resizes and applies a watermark with adjustable opacity.
*   **End-to-End Automation**: Manages the entire flow from a local folder to a designated Google Drive directory with a single command.
*   **High-Throughput Processing**: Built to efficiently handle hundreds of images in a single run.
*   **Modular Architecture**: Clean, single-responsibility modules for easy maintenance, testing, and extension.

---

## 🧠 Technical Deep Dive: The Processing Pipeline

The system processes each image through a multi-stage pipeline, leveraging a stack of battle-tested libraries including **PyTorch (for YOLOv8), OpenCV, Pillow, and NumPy**.

### 1. Object Detection for ROI Identification (YOLOv8)

The core of the smart cropping feature is its ability to "understand" the content of the image.

*   **Model**: We use **YOLOv8-nano**, chosen for its optimal balance between inference speed and detection accuracy, making it ideal for a high-throughput CLI application.
*   **ROI Calculation**:
    1.  The model detects objects and assigns a class (e.g., *person*, *bicycle*).
    2.  Each detection is filtered by size to discard insignificant background objects.
    3.  A **relevance score** is computed for each valid detection, weighting its **area**, **centrality**, and **class importance**. Class weights are user-configurable:
        ```python
        CLASS_WEIGHTS = {
            0: 1.0,  # person
            1: 0.8,  # bicycle
        }
        ```
    4.  The system identifies the object with the highest score as the main subject and detects other nearby relevant objects to form a comprehensive ROI. Special logic handles group photos by creating a unified bounding box.
    5.  The final output is the **center coordinate of the computed ROI**.

### 2. Intelligent Cropping Logic

With the ROI center identified, the system performs a deterministic crop.

*   **Aspect Ratio**: It automatically selects a **5:4 (landscape) or 4:5 (portrait)** aspect ratio, optimized for platforms like Instagram.
*   **Centering**: The crop is centered on the ROI coordinate, ensuring the main subject is perfectly framed while maximizing the viewable area. This logic is implemented in the `crop.py` module.

### 3. Automated Image Enhancement

Instead of applying a naive, one-size-fits-all filter, the pipeline performs adjustments based on lightweight image analysis.

*   **Luminance Correction**: The image is converted to the **CIELAB color space** to isolate the luminance channel (L*). The system analyzes the mean luminance and applies a non-linear adjustment to correct under- or over-exposed images, while protecting highlights.
*   **Color & Contrast**: It then applies subtle adjustments to warmth, saturation (in HSV space), and contrast to produce a vibrant, yet natural look.
*   This entire process, handled by the `presets.py` module, ensures every photo is brought to a consistent, high-quality baseline.

### 4. Dynamic Watermarking

The `watermark.py` module handles brand consistency.

*   The provided watermark image (PNG) is programmatically converted to white to ensure visibility on any background.
*   It is resized relative to the output image dimensions, its opacity is adjusted, and it's placed at a pre-defined position.

### 5. Cloud Integration

The final step is automated delivery.

*   The system uses the **Google Drive API** (via the `pydrive` library) to authenticate using an OAuth 2.0 flow.
*   Each processed image is uploaded directly to a specified folder in Google Drive, completing the end-to-end, hands-free workflow.

---

## 🧩 System Architecture & Modularity

The project adheres to a clean, modular design, where each component has a single responsibility. This simplifies maintenance and future development.

```
autoEdit-drive/
├── autoEdit/
│   ├── autoedit.py        # CLI entry point (argparse)
│   ├── pipeline.py        # Pipeline orchestrator
│   ├── config.py          # Global configuration & constants
│   ├── presets.py         # Image enhancement functions (OpenCV, Pillow)
│   ├── crop.py            # Smart cropping logic
│   ├── watermark.py       # Watermarking logic
│   ├── boxes.py           # Bounding box calculation utilities
│   ├── yolo_name.py       # ROI detection logic (YOLOv8)
│   └── __init__.py
├── fotos/                 # Example input folder
├── temp/                  # Default output folder
├── client_secrets.json    # Google API credentials (GIT-IGNORED)
├── yolov8n.pt             # YOLO model weights (GIT-IGNORED)
└── README.md
```

---

## 🚀 Installation & Configuration

### Prerequisites
*   Python 3.10+
*   Git

### Installation
```bash
# 1. Clone the repository
git clone git@github.com:MariusDscientist/autoedit-drive.git
cd autoedit-drive

# 2. Set up a virtual environment
python3.10 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download YOLOv8 model weights
# The pipeline will attempt to download it automatically,
# but you can also do it manually.
```

### Google Drive API Setup
1.  Navigate to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new project.
3.  Enable the **"Google Drive API"**.
4.  Go to "Credentials", click "Create Credentials", and select "OAuth client ID".
5.  Choose "Desktop application" as the application type.
6.  Download the JSON file and save it in the root of the project as `client_secrets.json`. **This file is git-ignored and should never be committed.**

---

## ▶️ Usage (CLI)

The script is executed via the `autoEdit.autoedit` module. All arguments are required for a full run.

```bash
python -m autoEdit.autoedit \
  --input "fotos" \
  --output "./temp" \
  --drive-folder "YOUR_GOOGLE_DRIVE_FOLDER_ID" \
  --water-mark "path/to/your/logo.png" \
  --log
```

#### Available Arguments

| Argument         | Type     | Description                                               |
| ---------------- | -------- | --------------------------------------------------------- |
| `--input`        | `string` | **Required**. Local folder containing the source images.      |
| `--output`       | `string` | **Required**. Local folder to save processed images.      |
| `--drive-folder` | `string` | **Required**. The ID of the destination folder in Google Drive. |
| `--water-mark`   | `string` | **Required**. Path to the watermark PNG file.             |
| `--preview`      | `flag`   | Process only the first image and display it.              |
| `--log`          | `flag`   | Save a `process_log.txt` file in the output folder.       |

---

## 🛣️ Roadmap

This project is actively evolving. Future improvements include:

*   [ ] **GPU Acceleration**: Add support for CUDA-based inference to accelerate the YOLOv8 pipeline.
*   [ ] **Advanced ROI Models**: Explore subject-specific models (e.g., a model fine-tuned on athletes) for even more precise cropping.
*   [ ] **Web UI**: Develop a simple web interface (e.g., using FastAPI/Streamlit) for easier use.
*   [ ] **Plugin System for Presets**: Allow users to create and share their own color adjustment presets.
*   [ ] **Expanded Cloud Support**: Add support for other storage providers like Dropbox or Amazon S3.

---

## 🧑‍💻 Author

**Jhon Mario Cano Torres**
*   Data Scientist
*   Photography Enthusiast
*   Automation Advocate
*   Based in Colombia 🇨🇴
*   [GitHub](https://github.com/MariusDscientist) | [LinkedIn](https://www.linkedin.com/in/jhon-mario-cano-torres-a6496924b)