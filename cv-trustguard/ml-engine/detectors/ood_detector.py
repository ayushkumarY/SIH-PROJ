import os

import numpy as np
import torch

from PIL import Image

from torchvision.models import (
    resnet50,
    ResNet50_Weights
)

from sklearn.ensemble import IsolationForest


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading feature extraction model...")

weights = ResNet50_Weights.DEFAULT

model = resnet50(weights=weights)

# Remove final classification layer
model.fc = torch.nn.Identity()

model.eval()

preprocess = weights.transforms()

print("Feature extraction model loaded.")


# ============================================================
# EXTRACT IMAGE FEATURES
# ============================================================

def extract_features(image_path):

    image = Image.open(
        image_path
    ).convert("RGB")

    image_tensor = preprocess(
        image
    ).unsqueeze(0)

    with torch.no_grad():

        features = model(
            image_tensor
        )

    return features.squeeze().numpy()


# ============================================================
# GET IMAGE FILES
# ============================================================

def get_images(dataset_path):

    supported_extensions = (
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".bmp"
    )

    images = []

    for filename in sorted(
        os.listdir(dataset_path)
    ):

        if filename.lower().endswith(
            supported_extensions
        ):

            images.append(
                os.path.join(
                    dataset_path,
                    filename
                )
            )

    return images


# ============================================================
# DETECT OOD IMAGES
# ============================================================

def detect_ood_images(dataset_path):

    image_paths = get_images(
        dataset_path
    )

    if len(image_paths) < 3:

        print(
            "Need at least 3 images "
            "for OOD detection."
        )

        return []

    features = []
    valid_images = []

    # --------------------------------------------------------
    # FEATURE EXTRACTION
    # --------------------------------------------------------

    for image_path in image_paths:

        try:

            feature = extract_features(
                image_path
            )

            features.append(feature)

            valid_images.append(
                image_path
            )

        except Exception as error:

            print(
                f"Error processing "
                f"{image_path}: {error}"
            )

    if len(features) < 3:

        return []

    features = np.array(
        features
    )

    # --------------------------------------------------------
    # ISOLATION FOREST
    # --------------------------------------------------------

    detector = IsolationForest(
        contamination="auto",
        random_state=42
    )

    predictions = detector.fit_predict(
        features
    )

    scores = detector.decision_function(
        features
    )

    findings = []

    for index, prediction in enumerate(
        predictions
    ):

        image_path = valid_images[index]

        filename = os.path.basename(
            image_path
        )

        score = float(
            scores[index]
        )

        # Isolation Forest:
        # -1 = anomaly
        #  1 = normal

        if prediction == -1:

            severity = "HIGH"

            findings.append({

                "image": filename,

                "type":
                    "possible_ood",

                "ood_score":
                    round(score, 4),

                "severity":
                    severity,

                "confidence":
                    round(
                        min(
                            0.99,
                            max(
                                0.50,
                                0.50 - score
                            )
                        ),
                        3
                    ),

                "reason":
                    "Image feature distribution "
                    "is unusual compared with "
                    "the analyzed dataset",

                "recommended_action":
                    "review"

            })

    return findings


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    dataset_path = (
        "../datasets/coco/images"
    )

    print("\n========================================")
    print("       CV TrustGuard OOD Detector")
    print("========================================")

    print(
        f"\nDataset: {dataset_path}"
    )

    findings = detect_ood_images(
        dataset_path
    )

    print("\n========================================")
    print("          OOD RESULTS")
    print("========================================")

    if not findings:

        print(
            "\nNo possible OOD images found."
        )

    else:

        for finding in findings:

            print(
                "\n----------------------------------------"
            )

            for key, value in finding.items():

                print(
                    f"{key.replace('_', ' ').title():22}: "
                    f"{value}"
                )

    print("\n========================================")
    print("Detection completed.")
    print("========================================")