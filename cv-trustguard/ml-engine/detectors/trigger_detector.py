import os
import cv2
import numpy as np


def detect_trigger(image_path):

    image = cv2.imread(image_path)

    if image is None:
        return None

    height, width = image.shape[:2]

    # Inspect bottom-right region
    trigger_size = 40

    x1 = max(0, width - trigger_size - 15)
    y1 = max(0, height - trigger_size - 15)
    x2 = width - 5
    y2 = height - 5

    region = image[y1:y2, x1:x2]

    if region.size == 0:
        return None

    # Convert BGR → HSV
    hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)

    # Detect strong red pixels
    lower_red = np.array([0, 120, 100])
    upper_red = np.array([10, 255, 255])

    mask = cv2.inRange(
        hsv,
        lower_red,
        upper_red
    )

    red_ratio = np.mean(mask > 0)

    if red_ratio > 0.35:

        confidence = min(
            0.99,
            0.50 + red_ratio
        )

        return {
            "type": "trigger_anomaly",
            "confidence": round(
                float(confidence),
                3
            ),
            "trigger_region": "bottom-right",
            "red_ratio": round(
                float(red_ratio),
                3
            ),
            "severity": "HIGH",
            "reason": (
                "Suspicious repeated visual trigger "
                "detected in the bottom-right image region"
            ),
            "recommended_action": "review"
        }

    return None


def scan_dataset(dataset_path):

    findings = []

    supported_extensions = (
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".bmp"
    )

    if not os.path.exists(dataset_path):

        print(
            f"Dataset not found: {dataset_path}"
        )

        return findings

    for filename in sorted(
        os.listdir(dataset_path)
    ):

        if not filename.lower().endswith(
            supported_extensions
        ):
            continue

        image_path = os.path.join(
            dataset_path,
            filename
        )

        try:

            result = detect_trigger(
                image_path
            )

            if result:

                result["image"] = filename

                findings.append(result)

                print(
                    f"[TRIGGER] {filename}"
                )

        except Exception as error:

            print(
                f"Error processing "
                f"{filename}: {error}"
            )

    return findings