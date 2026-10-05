import torch
from train import FusionNet


def predict(img_feat: torch.Tensor, sig_feat: torch.Tensor,
            weights="../../ml/weights/hidden_damage.pt"):
    model = FusionNet(img_feat.shape[-1], sig_feat.shape[-1])
    model.load_state_dict(torch.load(weights, map_location="cpu"))
    model.eval()
    with torch.no_grad():
        p = torch.sigmoid(model(img_feat, sig_feat)).item()
    return {"probability": p, "hidden_damage": p > 0.5}