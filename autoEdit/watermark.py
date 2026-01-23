from PIL import Image, ImageEnhance
from .config import LOGO_SCALE, LOGO_OPACITY, LOGO_MARGIN


# ================= FUNCIONES DE WATERMARK =================
def logo_to_white(img):
    r,g,b,a=img.split()
    white = Image.new("RGB",img.size,(255,255,255))
    return Image.merge("RGBA",(*white.split(),a))

def apply_watermark(image, watermark):
    img_w,img_h=image.size
    wm_width = int(img_w*LOGO_SCALE)
    wm_ratio = wm_width/watermark.width
    wm_height = int(watermark.height*wm_ratio)
    watermark_resized = watermark.resize((wm_width, wm_height),Image.LANCZOS)
    alpha = watermark_resized.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(LOGO_OPACITY/255)
    watermark_resized.putalpha(alpha)
    x = (img_w-wm_width)//2
    y = img_h-wm_height-LOGO_MARGIN
    result = Image.new("RGBA",image.size)
    result.paste(image,(0,0))
    result.paste(watermark_resized,(x,y),watermark_resized)
    return result
