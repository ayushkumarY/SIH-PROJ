from detectors.unified_model_loader import UnifiedModel
from detectors.unified_inference import UnifiedInference


MODEL_PATH = "../models/trustguard_resnet50.onnx"
IMAGE_PATH = "../datasets/coco/images/car1.jpg"


print("\n================================")
print("          ONNX TEST")
print("================================")

loader = UnifiedModel(MODEL_PATH)

model = loader.load()

inference = UnifiedInference(
    model=model,
    model_type=loader.model_type
)

result = inference.predict(IMAGE_PATH)

print("\nResult:")
print(result)

print("\n================================")