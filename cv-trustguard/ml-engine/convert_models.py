import torch
from torchvision.models import resnet50, ResNet50_Weights

print("\n================================")
print("       MODEL CONVERSION")
print("================================")

print("\nLoading PyTorch model...")

weights = ResNet50_Weights.DEFAULT
model = resnet50(weights=weights)
model.eval()

example_input = torch.randn(1, 3, 224, 224)


# --------------------------------
# 1. TorchScript
# --------------------------------

print("\nCreating TorchScript model...")

scripted_model = torch.jit.trace(
    model,
    example_input
)

torchscript_path = "../models/trustguard_resnet50.ts"

scripted_model.save(torchscript_path)

print(f"TorchScript saved: {torchscript_path}")


# --------------------------------
# 2. ONNX
# --------------------------------

print("\nCreating ONNX model...")

onnx_path = "../models/trustguard_resnet50.onnx"

torch.onnx.export(
    model,
    example_input,
    onnx_path,
    input_names=["input"],
    output_names=["output"],
    opset_version=17,
    dynamo=False
)

print(f"ONNX saved: {onnx_path}")


print("\n================================")
print("       CONVERSION COMPLETE")
print("================================")