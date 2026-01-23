import numpy as np
from PIL import Image

# ================= FUNCIONES DE RECORTE =================
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

