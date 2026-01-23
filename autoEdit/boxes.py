import numpy as np
from .config import CLASS_WEIGHTS

#  --- Funciones de cajas ---
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