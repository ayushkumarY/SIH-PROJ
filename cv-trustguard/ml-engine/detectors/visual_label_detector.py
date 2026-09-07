import json
import os

import torch
from PIL import Image
from torchvision.models import (
    resnet50,
    ResNet50_Weights
)


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading visual classification model...")

weights = ResNet50_Weights.DEFAULT
model = resnet50(weights=weights)
model.eval()

preprocess = weights.transforms()
categories = weights.meta["categories"]

print("Model loaded successfully.")


# ============================================================
# PREDICT IMAGE
# ============================================================

def predict_image(image_path):

    image = Image.open(image_path).convert("RGB")

    input_tensor = preprocess(image)
    input_batch = input_tensor.unsqueeze(0)

    with torch.no_grad():

        output = model(input_batch)

    probabilities = torch.nn.functional.softmax(
        output[0],
        dim=0
    )

    confidence, class_id = torch.max(probabilities, 0)

    predicted_label = categories[class_id.item()]

    return {
        "label": predicted_label,
        "confidence": float(confidence.item())
    }


# ============================================================
# LOAD COCO
# ============================================================

def load_coco(annotation_path):

    with open(
        annotation_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# DETECT LABEL ANOMALIES
# ============================================================

def detect_visual_label_anomalies(
    annotation_path,
    images_path
):

    coco = load_coco(annotation_path)

    images = coco.get("images", [])
    annotations = coco.get("annotations", [])
    categories_data = coco.get("categories", [])

    category_map = {
        category["id"]: category["name"]
        for category in categories_data
    }

    image_map = {
        image["id"]: image
        for image in images
    }

    findings = []

    for annotation in annotations:

        image_id = annotation["image_id"]
        category_id = annotation["category_id"]

        image_data = image_map.get(image_id)

        if image_data is None:
            continue

        assigned_label = category_map.get(
            category_id,
            "unknown"
        )

        image_name = image_data["file_name"]

        image_path = os.path.join(
            images_path,
            image_name
        )

        if not os.path.exists(image_path):

            continue

        try:

            prediction = predict_image(
                image_path
            )

            predicted_label = prediction["label"]
            confidence = prediction["confidence"]

            # ------------------------------------------------
            # CHECK LABEL
            # ------------------------------------------------

            if (
                predicted_label.lower()
                != assigned_label.lower()
                and confidence >= 0.70
            ):

                findings.append({

                    "image": image_name,

                    "assigned_label":
                        assigned_label,

                    "predicted_label":
                        predicted_label,

                    "confidence":
                        round(confidence, 3),

                    "type":
                        "possible_label_anomaly",

                    "severity":
                        "HIGH",

                    "reason":
                        "Visual model prediction "
                        "differs from assigned COCO label",

                    "recommended_action":
                        "review"

                })

        except Exception as error:

            print(
                f"Error processing "
                f"{image_name}: {error}"
            )

    return findings


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    annotation_path = (
        "../datasets/coco/"
        "annotations/instances.json"
    )

    images_path = (
        "../datasets/coco/images"
    )

    print("\n========================================")
    print("   CV TrustGuard Visual Label Detector")
    print("========================================")

    print(
        f"\nCOCO annotations: "
        f"{annotation_path}"
    )

    print(
        f"Images: {images_path}"
    )

    findings = detect_visual_label_anomalies(
        annotation_path,
        images_path
    )

    print("\n========================================")
    print("       LABEL ANOMALY RESULTS")
    print("========================================")

    if not findings:

        print(
            "\nNo possible label anomalies found."
        )

    else:

        for finding in findings:

            print("\n----------------------------------------")

            for key, value in finding.items():

                formatted_key = (
                    key.replace("_", " ").title()
                )

                print(
                    f"{formatted_key:22}: "
                    f"{value}"
                )

    print("\n========================================")
    print("Detection completed.")
    print("========================================")