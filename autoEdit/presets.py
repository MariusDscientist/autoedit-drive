import cv2
import numpy as np

# ================= FUNCIONES DE PRESET =================
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

