import os
from PIL import Image, ImageOps
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from .config import CLASS_WEIGHTS, LOGO_SCALE, LOGO_OPACITY, LOGO_MARGIN
from .presets import auto_luminance_smart, add_warmth, adjust_saturation_contrast
from .watermark import logo_to_white, apply_watermark
from .crop import choose_target_ratio, crop_to_aspect_max_area_centered
from .yolo_name import get_roi_center_yolo
import numpy as np
import cv2
from ultralytics import YOLO
import time




# ================= PIPELINE PRINCIPAL =================
def run_pipeline(input_folder, output_folder, watermark_path, drive_folder, preview=False, log=False):

    model = YOLO("yolov8n.pt")  # asegúrate de tener el modelo

    # Preparamos watermark
    watermark = Image.open(watermark_path).convert("RGBA")
    watermark = logo_to_white(watermark)

    # Google Drive auth
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    gauth.Refresh()
    drive = GoogleDrive(gauth)

    # Verificar/crear carpeta en Drive
    folder_id = drive_folder


    os.makedirs(output_folder, exist_ok=True)

    log_lines = []

    for filename in os.listdir(input_folder):
        if not filename.lower().endswith((".jpg",".jpeg",".png")):
            continue
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        # Abrir imagen
        image = Image.open(input_path)
        image = ImageOps.exif_transpose(image).convert("RGBA")

        # Ratio y ROI
        target_ratio = choose_target_ratio(image)
        cx, cy = get_roi_center_yolo(image, model)
        image_cropped = crop_to_aspect_max_area_centered(image, target_ratio, cx, cy)

        # Ajustes automáticos
        img_cv = np.array(image_cropped.convert("RGB"))[:, :, ::-1]
        img_cv = auto_luminance_smart(img_cv)
        img_cv = add_warmth(img_cv)
        img_cv = adjust_saturation_contrast(img_cv)
        image_adjusted = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))

        # Aplicar watermark
        image_final = apply_watermark(image_adjusted, watermark)
        image_final = image_final.convert("RGB")
        image_final.save(output_path, quality=95)
        print(f"✅ Procesado: {filename}")
        log_lines.append(f"Procesado: {filename}")

        # Subir a Drive
        try:
            gfile = drive.CreateFile({
                'title': filename,
                'parents': [{'id': folder_id}]
            })
            gfile.SetContentFile(output_path)
            gfile.Upload()
            print(f"⬆ Subido a Drive: {filename}")
            log_lines.append(f"Subido a Drive: {filename}")
            time.sleep(0.5)

        except Exception as e:
            print(f"⚠️ Error subiendo {filename}: {e}")
            log_lines.append(f"ERROR subiendo {filename}: {e}")
            continue


        if preview:
            image_final.show()
            break

    # Guardar log
    if log:
        with open(os.path.join(output_folder,"process_log.txt"), "w") as f:
            f.write("\n".join(log_lines))
        print("📄 Log guardado")