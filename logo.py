# -*- coding: utf-8 -*-
from google.colab import drive
drive.mount('/content/drive')

from ultralytics import YOLO
import os
import numpy as np
import cv2
from PIL import Image, ImageEnhance, ImageOps
import matplotlib.pyplot as plt

# ================= CONFIGURACIÓN =================
INPUT_FOLDER = "/content/drive/MyDrive/Ciclovía /Fotos/Prueba"
OUTPUT_FOLDER = "/content/drive/MyDrive/Ciclovía /Fotos/Prueba/resultado"
WATERMARK_PATH = "/content/drive/MyDrive/Identidad de marca/1768226583118.png"
TARGET_FORMAT = "4:5"
ASPECT_RATIOS = {"4:5": 4 / 5, "5:4": 5 / 4, "16:9": 16 / 9}
LOGO_SCALE = 0.20
LOGO_OPACITY = 175
LOGO_MARGIN = 0
PREVIEW = True
PREVIEW_IMAGE = "/content/drive/MyDrive/Ciclovía /Fotos/Prueba/DSC_0572.JPG"

CLASS_WEIGHTS = {0:1.0, 1:0.8, 3:0, 2:0}  # person, bicycle, motorcycle, car

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
model = YOLO("yolov8n.pt")  # modelo YOLOv8 pequeño para empezar

# ================= FUNCIONES =================

def show_before_after(before, after, title="Antes / Después"):
    """
    Muestra dos imágenes PIL lado a lado en el notebook.
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    axes[0].imshow(before)
    axes[0].set_title("Antes")
    axes[0].axis("off")

    axes[1].imshow(after)
    axes[1].set_title("Después")
    axes[1].axis("off")

    plt.suptitle(title)
    plt.tight_layout()
    plt.show()


# --- Funciones de cajas ---
def box_area(box):
    x1, y1, x2, y2 = box
    return (x2 - x1)*(y2 - y1)

def box_center(box):
    x1, y1, x2, y2 = box
    return np.array([(x1+x2)/2, (y1+y2)/2])

def union_boxes(boxes):
    x1 = min(b[0] for b in boxes)
    y1 = min(b[1] for b in boxes)
    x2 = max(b[2] for b in boxes)
    y2 = max(b[3] for b in boxes)
    return np.array([x1, y1, x2, y2])

def is_big_enough(box, img_area, min_ratio=0.02):
    return box_area(box)/img_area >= min_ratio

def score_box(box, cls, img_center, alpha=0.6):
    area = box_area(box)
    center = box_center(box)
    dist = np.linalg.norm(center-img_center)
    class_weight = CLASS_WEIGHTS.get(cls,0.2)
    return class_weight * (alpha*area - (1-alpha)*dist)

def is_group(person_boxes, img_size, max_dist_ratio=0.35):
    if len(person_boxes)<2: return False
    W,H = img_size
    centers = np.array([box_center(b) for b in person_boxes])
    mean_center = centers.mean(axis=0)
    max_dist = max(np.linalg.norm(c-mean_center) for c in centers)
    return max_dist < max_dist_ratio*max(W,H)

def find_related_objects(main_box, other_boxes, img_size, max_dist_ratio=0.25):
    W,H = img_size
    related = []
    main_center = box_center(main_box)
    for box in other_boxes:
        if np.linalg.norm(box_center(box)-main_center) < max_dist_ratio*max(W,H):
            related.append(box)
    return related

# --- Deskew automático ---
def deskew_image(img_pil, max_angle=5, min_lines=8):
    """
    Endereza la imagen y recorta automáticamente las esquinas vacías generadas por la rotación.
    """
    import numpy as np
    import cv2
    from PIL import Image

    # 1️⃣ PIL -> OpenCV
    img = np.array(img_pil.convert("RGBA"))
    gray = cv2.cvtColor(img[:,:,:3], cv2.COLOR_RGB2GRAY)

    # 2️⃣ Detectar bordes
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # 3️⃣ Detectar líneas
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=120, minLineLength=120, maxLineGap=15)
    if lines is None:
        return img_pil

    # 4️⃣ Calcular ángulo de rotación
    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
        if angle < -90: angle += 180
        if angle > 90: angle -= 180
        if abs(angle) <= max_angle:
            angles.append(angle)
    if len(angles) < min_lines:
        return img_pil
    rotation = np.median(angles)

    # 5️⃣ Crear canvas más grande y rotar
    w, h = img_pil.size
    diag = int(np.sqrt(w**2 + h**2)) + 10
    canvas = Image.new("RGBA", (diag, diag), (0,0,0,0))
    x_offset = (diag - w)//2
    y_offset = (diag - h)//2
    canvas.paste(img_pil, (x_offset, y_offset))
    rotated = canvas.rotate(rotation, expand=False, fillcolor=(0,0,0,0))

    # 6️⃣ Crear máscara de píxeles válidos (no transparentes)
    rotated_np = np.array(rotated)
    mask = rotated_np[:,:,3] > 0  # alpha > 0

    # 7️⃣ Encontrar bounding box de la región válida
    coords = np.argwhere(mask)
    if coords.size == 0:
        return img_pil
    y0, x0 = coords.min(axis=0)[:2]
    y1, x1 = coords.max(axis=0)[:2] + 1

    # 8️⃣ Recortar
    cropped = rotated.crop((x0, y0, x1, y1))
    return cropped


# --- Funciones de ratio y recorte ---
def choose_target_ratio(img):
    W,H = img.size
    return 5/4 if W>=H else 4/5

def crop_to_aspect_max_area_centered(img, target_ratio, center_x, center_y):
    W,H = img.size
    current_ratio = W/H
    if current_ratio>target_ratio:
        crop_h = H
        crop_w = int(H*target_ratio)
    else:
        crop_w = W
        crop_h = int(W/target_ratio)
    left = max(0,min(int(center_x-crop_w/2), W-crop_w))
    top = max(0,min(int(center_y-crop_h/2), H-crop_h))
    return img.crop((left, top, left+crop_w, top+crop_h))

# --- Funciones de watermark ---
def logo_to_white(img):
    r,g,b,a=img.split()
    white = Image.new("RGB",img.size,(255,255,255))
    return Image.merge("RGBA",(*white.split(),a))

def apply_watermark(image, watermark, scale, opacity, margin):
    img_w,img_h=image.size
    wm_width = int(img_w*scale)
    wm_ratio = wm_width/watermark.width
    wm_height = int(watermark.height*wm_ratio)
    watermark_resized = watermark.resize((wm_width, wm_height),Image.LANCZOS)
    alpha = watermark_resized.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity/255)
    watermark_resized.putalpha(alpha)
    x = (img_w-wm_width)//2
    y = img_h-wm_height-margin
    result = Image.new("RGBA",image.size)
    result.paste(image,(0,0))
    result.paste(watermark_resized,(x,y),watermark_resized)
    return result

# --- Función principal de ROI con YOLO ---
def get_roi_center_yolo(img_pil, model):
    W,H = img_pil.size
    img_center = np.array([W/2,H/2])
    img_area = W*H

    img_rgb = img_pil.convert("RGB")
    results = model(img_rgb, verbose=False)[0]
    if results.boxes is None: return img_center

    boxes = results.boxes.xyxy.cpu().numpy()
    classes = results.boxes.cls.cpu().numpy().astype(int)

    # filtrar por tamaño y clase
    candidates = [(b,c) for b,c in zip(boxes,classes) if c in CLASS_WEIGHTS and is_big_enough(b,img_area)]
    if not candidates: return img_center

    person_boxes = [b for b,c in candidates if c==0]

    if is_group(person_boxes,(W,H)):
        roi = union_boxes(person_boxes)
        return box_center(roi)

    scored = [(score_box(b,c,img_center),b,c) for b,c in candidates]
    _,main_box,_ = max(scored,key=lambda x:x[0])

    related = [b for b,c in candidates if c in (1,3)]
    fused = [main_box]+find_related_objects(main_box,related,(W,H))
    roi = union_boxes(fused)
    return box_center(roi)

# --- Funciones de preset ---


def auto_luminance_smart(img_cv, 
                         target_L=120,   # valor medio deseado
                         min_L=100,       # umbral inferior para considerar "oscura"
                         max_L=150,      # umbral superior para considerar "clara"
                         max_change=1.5  # factor máximo de ajuste ±20%
                        ):
    """
    Ajusta automáticamente la luminosidad de la imagen:
    - Si está oscura, ilumina suavemente
    - Si está muy clara, oscurece suavemente
    - No toca fotos ya bien expuestas
    """
    lab = cv2.cvtColor(img_cv, cv2.COLOR_BGR2LAB)
    L, A, B = cv2.split(lab)
    
    mean_L = np.mean(L)
    
    # Determinar factor de ajuste según luminosidad promedio
    if mean_L < min_L:          # imagen oscura → subir brillo
        factor = min(target_L / (mean_L + 1e-5), max_change)
    elif mean_L > max_L:        # imagen clara → bajar brillo
        factor = max(target_L / (mean_L + 1e-5), 2 - max_change)  # evita sobrecompensar
    else:
        factor = 1.0             # bien expuesta → no tocar
    
    # Aplicar factor solo si es necesario
    if factor != 1.0:
        L_new = np.clip(L * factor, 0, 255).astype(np.uint8)
        lab_new = cv2.merge([L_new, A, B])
        img_adjusted = cv2.cvtColor(lab_new, cv2.COLOR_LAB2BGR)
    else:
        img_adjusted = img_cv.copy()
    
    # Suavizar altos valores para proteger zonas muy brillantes (cielos, reflejos)
    img_final = tone_map_highlights(img_adjusted)
    
    return img_final


def tone_map_highlights(img_cv, clip_percent=100):
    """
    Reduce un poco los valores altos para evitar sobreexposición
    """
    img_float = img_cv.astype(np.float32)
    # Tomamos el percentil superior
    high = np.percentile(img_float, clip_percent)
    img_float = np.minimum(img_float, high)
    img_float = (img_float / high * 255).astype(np.uint8)
    return img_float


def add_warmth(img_cv, factor=1.025):
    """
    Factor >1: más cálido, <1: más frío
    """
    b, g, r = cv2.split(img_cv.astype(np.float32))
    r *= factor  # subimos rojos
    b /= factor  # bajamos azul un poco
    img_warm = cv2.merge([np.clip(b,0,255), np.clip(g,0,255), np.clip(r,0,255)]).astype(np.uint8)
    return img_warm

def adjust_saturation_contrast(img_cv, sat_factor=1.2, contrast_factor=1.05):
    # Saturación
    hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:,:,1] *= sat_factor
    hsv[:,:,1] = np.clip(hsv[:,:,1],0,255)
    img_sat = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    # Contraste: img = (img - 128)*factor + 128
    img_float = img_sat.astype(np.float32)
    img_float = (img_float - 128) * contrast_factor + 128
    img_float = np.clip(img_float, 0, 255).astype(np.uint8)
    return img_float



# --- Preparamos watermark ---
watermark = Image.open(WATERMARK_PATH).convert("RGBA")
watermark = logo_to_white(watermark)

# ================= PIPELINE =================
for filename in os.listdir(INPUT_FOLDER):
    if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
        continue

    input_path = os.path.join(INPUT_FOLDER, filename)
    output_path = os.path.join(OUTPUT_FOLDER, filename)

    # 1️⃣ Abrir imagen y corregir orientación EXIF
    image_original = Image.open(input_path)
    image_original = ImageOps.exif_transpose(image_original)
    image_original = image_original.convert("RGBA")

    # 2️⃣ Enderezar imagen y recortar fondo
    #image_rotated = deskew_image(image_original)
    image_rotated = image_original

    # 3️⃣ Elegir ratio según orientación
    target_ratio = choose_target_ratio(image_rotated)

    # 4️⃣ Centro del sujeto con YOLO
    cx, cy = get_roi_center_yolo(image_rotated, model)

    # 5️⃣ Recorte inteligente centrado en sujeto
    image_cropped = crop_to_aspect_max_area_centered(
        image_rotated,
        target_ratio,
        cx,
        cy
    )

    # 6️⃣ Ajustes automáticos de imagen
    img_cv = np.array(image_cropped.convert("RGB"))[:, :, ::-1]  # PIL -> BGR
    img_cv = auto_luminance_smart(img_cv)
    #img_cv = tone_map_highlights(img_cv)
    img_cv = add_warmth(img_cv)
    img_cv = adjust_saturation_contrast(img_cv)
    image_adjusted = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))

    # 7️⃣ Aplicar logo
    image_final = apply_watermark(
        image_adjusted,
        watermark,
        LOGO_SCALE,
        LOGO_OPACITY,
        LOGO_MARGIN
    )

    # 8️⃣ Guardar
    image_final = image_final.convert("RGB")
    image_final.save(output_path, quality=95)

    print(f"✅ {filename}")


    print("Antes:", image_original.size)
    print("Después:", image_rotated.size)

    show_before_after(
        image_original.convert("RGB"),
        image_final.convert("RGB"),
        "Deskew test"
    )
