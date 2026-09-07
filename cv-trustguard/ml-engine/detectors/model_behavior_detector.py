import json
import os
from datetime import datetime


BASELINE_FILE = "../models/model_behavior_baseline.json"


def create_behavior_baseline(model_name, predictions):

    baseline = {
        "model_name": model_name,
        "created_at": datetime.utcnow().isoformat(),
        "predictions": predictions
    }

    os.makedirs(
        os.path.dirname(BASELINE_FILE),
        exist_ok=True
    )

    with open(
        BASELINE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            baseline,
            file,
            indent=4
        )

    return baseline


def load_behavior_baseline():

    if not os.path.exists(BASELINE_FILE):
        return None

    with open(
        BASELINE_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def compare_predictions(
    baseline_predictions,
    current_predictions
):

    findings = []

    baseline_map = {
        item["image"]: item
        for item in baseline_predictions
    }

    for current in current_predictions:

        image_name = current["image"]

        baseline = baseline_map.get(image_name)

        if baseline is None:

            findings.append({
                "image": image_name,
                "type": "new_input",
                "severity": "MEDIUM",
                "reason": (
                    "Image was not present in "
                    "the trusted behavioral baseline"
                ),
                "recommended_action": "review"
            })

            continue

        baseline_label = baseline.get("label")
        current_label = current.get("label")

        if baseline_label != current_label:

            findings.append({
                "image": image_name,
                "type": "behavior_change",
                "baseline_label": baseline_label,
                "current_label": current_label,
                "severity": "HIGH",
                "confidence": 1.0,
                "reason": (
                    "Current model prediction differs "
                    "from the trusted behavioral baseline"
                ),
                "recommended_action": "review"
            })

    return findings