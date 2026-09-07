import json
import os


# ============================================================
# LOAD COCO DATASET
# ============================================================

def load_coco_annotations(annotation_path):
    """
    Load COCO annotation JSON.
    """

    with open(annotation_path, "r", encoding="utf-8") as file:
        coco_data = json.load(file)

    return coco_data


# ============================================================
# BUILD CATEGORY MAP
# ============================================================

def build_category_map(categories):
    """
    Convert category list into:
    category_id -> category_name
    """

    return {
        category["id"]: category["name"]
        for category in categories
    }


# ============================================================
# DETECT LABEL ANOMALIES
# ============================================================

def detect_label_anomalies(annotation_path):
    """
    Detect basic label inconsistencies in a COCO dataset.

    This version checks for:
    - Missing category IDs
    - Invalid image IDs
    - Invalid category IDs
    """

    coco_data = load_coco_annotations(annotation_path)

    images = coco_data.get("images", [])
    annotations = coco_data.get("annotations", [])
    categories = coco_data.get("categories", [])

    category_map = build_category_map(categories)

    image_map = {
        image["id"]: image["file_name"]
        for image in images
    }

    findings = []

    for annotation in annotations:

        image_id = annotation.get("image_id")
        category_id = annotation.get("category_id")

        image_name = image_map.get(
            image_id,
            "unknown_image"
        )

        category_name = category_map.get(
            category_id
        )

        # ----------------------------------------------------
        # INVALID IMAGE ID
        # ----------------------------------------------------

        if image_id not in image_map:

            findings.append({
                "image": image_name,
                "image_id": image_id,
                "category_id": category_id,
                "type": "invalid_image_id",
                "severity": "HIGH",
                "confidence": 1.0,
                "reason": "Annotation refers to an image that does not exist",
                "recommended_action": "review"
            })

            continue

        # ----------------------------------------------------
        # INVALID CATEGORY ID
        # ----------------------------------------------------

        if category_name is None:

            findings.append({
                "image": image_name,
                "image_id": image_id,
                "category_id": category_id,
                "type": "invalid_category_id",
                "severity": "HIGH",
                "confidence": 1.0,
                "reason": "Annotation refers to an undefined category",
                "recommended_action": "quarantine"
            })

            continue

    return findings


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    annotation_path = "../datasets/coco/annotations/instances.json"

    print("\n========================================")
    print("       CV TrustGuard Label Detector")
    print("========================================")

    print(f"\nCOCO file: {annotation_path}")

    if not os.path.exists(annotation_path):

        print("\nCOCO annotation file not found!")
        print("Please check the path.")

    else:

        findings = detect_label_anomalies(
            annotation_path
        )

        print("\n========================================")
        print("       LABEL ANOMALY RESULTS")
        print("========================================")

        if not findings:

            print("\nNo structural label anomalies found.")

        else:

            for finding in findings:

                print("\n----------------------------------------")

                for key, value in finding.items():

                    print(
                        f"{key.replace('_', ' ').title():20}: {value}"
                    )

    print("\n========================================")
    print("Detection completed.")
    print("========================================")