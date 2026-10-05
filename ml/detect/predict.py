import sys
from ultralytics import YOLO

def main(img_path: str, weights="runs/detect/damage_v1/weights/best.pt"):
    model = YOLO(weights)
    results = model.predict(img_path, save=True, conf=0.35)
    for r in results:
        for b in r.boxes:
            print(model.names[int(b.cls)], float(b.conf), b.xyxy.tolist())

if __name__ == "__main__":
    main(sys.argv[1])