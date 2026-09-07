import os

from detectors.model_loader import (
    load_pytorch_model,
    predict_image
)

from detectors.model_behavior_detector import (
    create_behavior_baseline
)


MODEL_NAME = "ResNet50"

IMAGE_DIR = "../datasets/coco/images"


def get_images():

    supported_extensions = (
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".bmp"
    )

    images = []

    for filename in sorted(
        os.listdir(IMAGE_DIR)
    ):

        if filename.lower().endswith(
            supported_extensions
        ):

            images.append(filename)

    return images


print("\n======================================")
print("    CV TrustGuard Behavior Baseline")
print("======================================")

print("\nLoading model...")

model, weights = load_pytorch_model()

images = get_images()

predictions = []

print("\nGenerating trusted predictions...\n")

for filename in images:

    image_path = os.path.join(
        IMAGE_DIR,
        filename
    )

    try:

        result = predict_image(
            model,
            weights,
            image_path
        )

        prediction = {
            "image": filename,
            "label": result["label"],
            "confidence": round(
                result["confidence"],
                4
            )
        }

        predictions.append(prediction)

        print(
            f"{filename} -> "
            f"{result['label']} "
            f"({result['confidence']:.3f})"
        )

    except Exception as error:

        print(
            f"Error processing {filename}: "
            f"{error}"
        )


baseline = create_behavior_baseline(
    MODEL_NAME,
    predictions
)


print("\n======================================")
print("Baseline created successfully.")
print("======================================")

print(
    "\nSaved to: "
    "../models/model_behavior_baseline.json"
)

print(
    f"\nTotal images: {len(predictions)}"
)