import json
import hashlib
import os

from provenance.digital_signature import verify_signature


RECORD_FILE = "../reports/inference_record.json"


# ====================================
# FILE HASH
# ====================================

def calculate_file_hash(file_path):

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        while True:

            chunk = file.read(8192)

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()


# ====================================
# RECORD HASH
# ====================================

def calculate_record_hash(record):

    record_string = json.dumps(
        record,
        sort_keys=True,
        separators=(",", ":")
    )

    return hashlib.sha256(
        record_string.encode("utf-8")
    ).hexdigest()


# ====================================
# VERIFY PROVENANCE
# ====================================

def verify_provenance(record_file):

    if not os.path.exists(record_file):

        return {
            "status": "error",
            "integrity": "unknown",
            "severity": "HIGH",
            "confidence": 0.0,
            "image_verified": False,
            "model_verified": False,
            "record_verified": False,
            "signature_verified": False,
            "reason": "Provenance record not found",
            "recommended_action": "review"
        }

    try:

        with open(
            record_file,
            "r",
            encoding="utf-8"
        ) as file:

            record = json.load(file)

    except Exception as error:

        return {
            "status": "error",
            "integrity": "unknown",
            "severity": "HIGH",
            "confidence": 0.0,
            "image_verified": False,
            "model_verified": False,
            "record_verified": False,
            "signature_verified": False,
            "reason": f"Unable to read provenance record: {error}",
            "recommended_action": "review"
        }

    # ====================================
    # VERIFY RECORD HASH
    # ====================================

    stored_integrity_hash = record.get(
        "integrity_hash"
    )

    stored_signature = record.get(
        "digital_signature"
    )

    record_for_integrity = record.copy()

    record_for_integrity.pop(
        "integrity_hash",
        None
    )

    record_for_integrity.pop(
        "digital_signature",
        None
    )

    calculated_integrity_hash = calculate_record_hash(
        record_for_integrity
    )

    record_verified = (
        calculated_integrity_hash
        == stored_integrity_hash
    )

    # ====================================
    # VERIFY DIGITAL SIGNATURE
    # ====================================

    signature_verified = False

    if stored_signature:

        record_for_signature = record.copy()

        record_for_signature.pop(
            "digital_signature",
            None
        )

        signed_data = json.dumps(
            record_for_signature,
            sort_keys=True,
            separators=(",", ":")
        )

        try:

            signature_verified = verify_signature(
                signed_data,
                stored_signature
            )

        except Exception:

            signature_verified = False

    # ====================================
    # VERIFY IMAGE
    # ====================================

    image_data = record.get(
        "image",
        {}
    )

    image_file_name = image_data.get(
        "file_name"
    )

    expected_image_hash = image_data.get(
        "sha256"
    )

    image_verified = False

    if image_file_name and expected_image_hash:

        image_path = os.path.join(
            "..",
            "datasets",
            "coco",
            "images",
            image_file_name
        )

        if os.path.exists(image_path):

            try:

                actual_image_hash = calculate_file_hash(
                    image_path
                )

                image_verified = (
                    actual_image_hash
                    == expected_image_hash
                )

            except Exception:

                image_verified = False

    # ====================================
    # VERIFY MODEL
    # ====================================

    model_data = record.get(
        "model",
        {}
    )

    model_file_name = model_data.get(
        "file_name"
    )

    expected_model_hash = model_data.get(
        "sha256"
    )

    model_verified = False

    if model_file_name and expected_model_hash:

        model_path = os.path.join(
            "..",
            "models",
            model_file_name
        )

        if os.path.exists(model_path):

            try:

                actual_model_hash = calculate_file_hash(
                    model_path
                )

                model_verified = (
                    actual_model_hash
                    == expected_model_hash
                )

            except Exception:

                model_verified = False

    # ====================================
    # FINAL RESULT
    # ====================================

    if (
        image_verified
        and model_verified
        and record_verified
        and signature_verified
    ):

        return {
            "status": "verified",
            "integrity": "trusted",
            "severity": "LOW",
            "confidence": 1.0,
            "image_verified": True,
            "model_verified": True,
            "record_verified": True,
            "signature_verified": True,
            "reason": (
                "Image, model, provenance record "
                "and digital signature are valid."
            ),
            "recommended_action": "accept"
        }

    # ====================================
    # FAILED COMPONENTS
    # ====================================

    failed_components = []

    if not image_verified:
        failed_components.append("image")

    if not model_verified:
        failed_components.append("model")

    if not record_verified:
        failed_components.append("provenance record")

    if not signature_verified:
        failed_components.append("digital signature")

    return {
        "status": "tampered",
        "integrity": "suspicious",
        "severity": "CRITICAL",
        "confidence": 1.0,
        "image_verified": image_verified,
        "model_verified": model_verified,
        "record_verified": record_verified,
        "signature_verified": signature_verified,
        "failed_components": failed_components,
        "reason": (
            "One or more provenance components "
            "or the digital signature do not match "
            "the trusted values."
        ),
        "recommended_action": "quarantine"
    }