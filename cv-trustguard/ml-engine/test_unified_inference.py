from detectors.unified_model_loader import UnifiedModel
from detectors.unified_inference import UnifiedInference


MODEL_PATH = "../models/trustguard_resnet50.pth"
IMAGE_PATH = "../datasets/coco/images/car1.jpg"


print("\n================================")
print("      UNIFIED INFERENCE TEST")
print("================================")


# Load model
loader = UnifiedModel(MODEL_PATH)

model = loader.load()


# Create inference engine
inference = UnifiedInference(
    model=model,
    model_type=loader.model_type
)


# Run prediction
result = inference.predict(IMAGE_PATH)


print("\nImage:")
print(IMAGE_PATH)

print("\nPrediction:")
print(result)

print("\n================================")
print("       INFERENCE COMPLETE")
print("================================")