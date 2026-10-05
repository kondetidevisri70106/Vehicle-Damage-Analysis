import cv2
import numpy as np

IMG_SIZE = 640


def load_image(path):
    img = cv2.imread(path)
    if img is None:
        raise ValueError(f"Cannot load: {path}")
    return img


def resize_image(img, size=IMG_SIZE):
    return cv2.resize(img, (size, size))


def normalize_image(img):
    return img.astype(np.float32) / 255.0


def preprocess_for_classifier(img, size=224):
    img = cv2.resize(img, (size, size))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    img = (img - mean) / std
    return np.transpose(img, (2, 0, 1))