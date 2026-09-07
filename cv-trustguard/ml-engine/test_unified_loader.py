from detectors.unified_model_loader import UnifiedModel

MODEL_PATH = "../models/trustguard_resnet50.pth"

loader = UnifiedModel(MODEL_PATH)

print("\n================================")
print("      UNIFIED MODEL LOADER")
print("================================")

print(loader.get_info())

try:
    model = loader.load()
    print("\nModel loaded successfully.")
except Exception as error:
    print("\nModel loading failed.")
    print(f"Error: {error}")

print("================================")