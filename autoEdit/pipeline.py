import os
from PIL import Image, ImageOps
# Moved Google Drive imports into run_upload_pipeline
from .config import CLASS_WEIGHTS, LOGO_SCALE, LOGO_OPACITY, LOGO_MARGIN
from .presets import auto_luminance_smart, add_warmth, adjust_saturation_contrast
from .watermark import logo_to_white, apply_watermark
from .crop import choose_target_ratio, crop_to_aspect_max_area_centered
from .yolo_name import get_roi_center_yolo
import numpy as np
import cv2
from ultralytics import YOLO
import time
from pydrive.auth import GoogleAuth # Keep these at top if used by other parts, or move to upload func
from pydrive.drive import GoogleDrive # Keep these at top if used by other parts, or move to upload func


# ==================== PROCESSING PIPELINE ====================
def run_processing_pipeline(input_folder, output_folder, watermark_path, preview=False, log=False):
    model = YOLO("yolov8n.pt")  # asegúrate de tener el modelo

    # Preparamos watermark
    watermark = Image.open(watermark_path).convert("RGBA")
    watermark = logo_to_white(watermark)

    os.makedirs(output_folder, exist_ok=True)

    log_lines = []
    
    print(f"🔄 Iniciando procesamiento de imágenes de '{input_folder}' a '{output_folder}'...")

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

        if preview:
            image_final.show()
            break
    
    # Guardar log
    if log:
        log_file_path = os.path.join(output_folder,"process_log.txt")
        with open(log_file_path, "w") as f:
            f.write("\n".join(log_lines))
        print(f"📄 Log de procesamiento guardado en {log_file_path}")
    
    print(f"🎉 Proceso de procesamiento finalizado. Imágenes guardadas en '{output_folder}'.")


# ==================== UPLOAD PIPELINE ====================
def run_upload_pipeline(source_folder, drive_folder_id, log=False):
    # Google Drive auth
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth() # Authenticates via a local webserver flow
    gauth.Refresh() # Refreshes credentials if expired
    drive = GoogleDrive(gauth)

    log_lines = []
    
    print(f"🔄 Iniciando subida de imágenes desde '{source_folder}' a Google Drive (carpeta ID: {drive_folder_id})...")

    # Obtener lista de archivos existentes en la carpeta de Drive
    print("🔎 Obteniendo lista de archivos existentes en la carpeta de Drive...")
    query = f"'{drive_folder_id}' in parents and trashed=false"
    try:
        existing_files_in_drive = {f['title'] for f in drive.ListFile({'q': query}).GetList()}
        print(f"✅ Encontrados {len(existing_files_in_drive)} archivos en la carpeta de Drive.")
    except Exception as e:
        print(f"⚠️ Error al obtener la lista de archivos de Drive: {e}. Asegúrate de que el ID de la carpeta es correcto y tienes permisos.")
        return # Exit if we can't get existing files

    files_to_consider = [f for f in os.listdir(source_folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    
    if not files_to_consider:
        print(f"ℹ️ No se encontraron imágenes JPG/JPEG/PNG en '{source_folder}' para subir.")
        return

    for filename in files_to_consider:
        local_file_path = os.path.join(source_folder, filename)

        if filename in existing_files_in_drive:
            print(f"⏩ Omitiendo '{filename}', ya existe en Google Drive.")
            log_lines.append(f"Omitido (ya existe): {filename}")
            continue

        print(f"⬆ Subiendo '{filename}'...")
        try:
            gfile = drive.CreateFile({
                'title': filename,
                'parents': [{'id': drive_folder_id}]
            })
            gfile.SetContentFile(local_file_path)
            gfile.Upload()
            print(f"✅ Subido: {filename}")
            log_lines.append(f"Subido a Drive: {filename}")
            time.sleep(0.5) # Pausa para evitar exceder límites de API o para una mejor UX

        except Exception as e:
            print(f"⚠️ Error subiendo '{filename}': {e}")
            log_lines.append(f"ERROR subiendo '{filename}': {e}")
            continue

    # Guardar log de subida
    if log:
        log_file_path = os.path.join(source_folder, "upload_log.txt")
        with open(log_file_path, "w") as f:
            f.write("\n".join(log_lines))
        print(f"📄 Log de subida guardado en {log_file_path}")
    
    print("🎉 Proceso de subida a Drive finalizado.")