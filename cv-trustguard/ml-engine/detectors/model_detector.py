import hashlib
import json
import os
from datetime import datetime


def calculate_model_hash(model_path):

    if not os.path.exists(model_path):
        return None

    sha256 = hashlib.sha256()

    with open(model_path, "rb") as file:

        while True:

            chunk = file.read(8192)

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()


def create_manifest(model_path, manifest_path):

    model_hash = calculate_model_hash(model_path)

    if model_hash is None:
        return {
            "status": "error",
            "reason": "Model file not found"
        }

    manifest = {
        "model_name": os.path.basename(model_path),
        "model_format": "Test/Binary",
        "sha256": model_hash,
        "created_at": datetime.utcnow().isoformat(),
        "trusted": True
    }

    os.makedirs(
        os.path.dirname(manifest_path),
        exist_ok=True
    )

    with open(
        manifest_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            manifest,
            file,
            indent=4
        )

    return {
        "status": "baseline_created",
        "manifest": manifest
    }


def load_manifest(manifest_path):

    if not os.path.exists(manifest_path):

        return None

    with open(
        manifest_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def verify_model(model_path, manifest_path):

    if not os.path.exists(model_path):

        return {
            "status": "error",
            "integrity": "unknown",
            "severity": "HIGH",
            "reason": "Model file not found",
            "recommended_action": "review"
        }

    manifest = load_manifest(manifest_path)

    if manifest is None:

        return {
            "status": "error",
            "integrity": "unknown",
            "severity": "HIGH",
            "reason": "Trusted model manifest not found",
            "recommended_action": "review"
        }

    actual_hash = calculate_model_hash(model_path)
    expected_hash = manifest.get("sha256")

    result = {
        "model": os.path.basename(model_path),
        "expected_sha256": expected_hash,
        "actual_sha256": actual_hash
    }

    if actual_hash == expected_hash:

        result.update({
            "status": "verified",
            "integrity": "trusted",
            "severity": "LOW",
            "confidence": 1.0,
            "reason": "Model hash matches trusted manifest",
            "recommended_action": "accept"
        })

    else:

        result.update({
            "status": "tampered",
            "integrity": "suspicious",
            "severity": "CRITICAL",
            "confidence": 1.0,
            "reason": (
                "Model hash does not match the trusted manifest. "
                "Possible model modification or substitution."
            ),
            "recommended_action": "quarantine"
        })

    return result