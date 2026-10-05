from ultralytics import YOLO

def main():
    model = YOLO("yolov8n.pt")
    model.train(
        data="data.yaml",
        epochs=80,
        imgsz=640,
        batch=16,
        project="runs/detect",
        name="damage_v1",
        patience=15,
    )
    metrics = model.val()
    print("mAP50:", metrics.box.map50)

if __name__ == "__main__":
    main()