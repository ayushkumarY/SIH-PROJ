import json

from detectors.unified_model_loader import UnifiedModel
from detectors.unified_inference import UnifiedInference

from provenance.inference_provenance import (
    create_inference_record,
    sign_provenance_record
)


MODEL_PATH = "../models/trustguard_resnet50.pth"

IMAGE_PATH = "../datasets/coco/images/car1.jpg"


print("\n================================")
print("     INFERENCE PROVENANCE")
print("================================")


# Load model

loader = UnifiedModel(MODEL_PATH)

model = loader.load()


# Run inference

inference = UnifiedInference(
    model=model,
    model_type=loader.model_type
)

prediction = inference.predict(IMAGE_PATH)


# Create provenance record

record = create_inference_record(
    image_path=IMAGE_PATH,
    model_path=MODEL_PATH,
    model_format=loader.model_type,
    prediction=prediction
)

record = sign_provenance_record(record)


print("\nPrediction:")
print(prediction)


print("\nImage SHA-256:")
print(record["image"]["sha256"])


print("\nModel SHA-256:")
print(record["model"]["sha256"])


print("\nIntegrity Hash:")
print(record["integrity_hash"])


# Save record

output_file = "../reports/inference_record.json"

with open(
    output_file,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        record,
        file,
        indent=4
    )


print("\nProvenance record saved:")
print(output_file)


print("\n================================")
print("     PROVENANCE COMPLETE")
print("================================")