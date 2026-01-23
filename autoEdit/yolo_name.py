import numpy as np
from .config import CLASS_WEIGHTS
from .boxes import is_big_enough, is_group, union_boxes, box_center, score_box, find_related_objects

# ================= FUNCION ROI YOLO =================

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