import sys
import torch
from torchvision import models, transforms
from PIL import Image
from torch import nn

CLASSES = ["minor", "moderate", "severe"]

def main(img_path, weights="../../ml/weights/severity.pt"):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    m = models.resnet18(weights=None)
    m.fc = nn.Linear(m.fc.in_features, len(CLASSES))
    m.load_state_dict(torch.load(weights, map_location=device))
    m.eval().to(device)

    tf = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225]),
    ])
    x = tf(Image.open(img_path).convert("RGB")).unsqueeze(0).to(device)
    with torch.no_grad():
        prob = torch.softmax(m(x), 1)[0]
    print(CLASSES[int(prob.argmax())], float(prob.max()))

if __name__ == "__main__":
    main(sys.argv[1])