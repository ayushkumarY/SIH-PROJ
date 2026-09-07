import torch

from torchvision.models import (
    resnet50,
    ResNet50_Weights
)


print("Loading ResNet50...")

weights = ResNet50_Weights.DEFAULT

model = resnet50(
    weights=weights
)

model.eval()


output_path = "../models/trustguard_resnet50.pth"


torch.save(
    model,
    output_path
)


print("\n================================")
print("       MODEL SAVED")
print("================================")

print(
    f"Model: {output_path}"
)