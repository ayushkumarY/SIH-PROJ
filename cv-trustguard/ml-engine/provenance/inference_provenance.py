import hashlib
import json
import os
from datetime import datetime, timezone
from uuid import uuid4
from provenance.digital_signature import sign_data

def calculate_file_hash(file_path):

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while True:
            chunk = file.read(8192)

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()


def calculate_record_hash(record):

    record_string = json.dumps(
        record,
        sort_keys=True,
        separators=(",", ":")
    )

    return hashlib.sha256(
        record_string.encode("utf-8")
    ).hexdigest()


def create_inference_record(
    image_path,
    model_path,
    model_format,
    prediction,
    preprocessing="ImageNet-224"
):

    image_hash = calculate_file_hash(image_path)
    model_hash = calculate_file_hash(model_path)

    record = {
        "record_id": str(uuid4()),

        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),

        "nonce": str(uuid4()),

        "image": {
            "file_name": os.path.basename(image_path),
            "sha256": image_hash
        },

        "model": {
            "file_name": os.path.basename(model_path),
            "format": model_format,
            "sha256": model_hash
        },

        "preprocessing": {
            "configuration": preprocessing
        },

        "prediction": prediction
    }

    integrity_hash = calculate_record_hash(record)

    record["integrity_hash"] = integrity_hash

    return record

def sign_provenance_record(record):

    data_to_sign = json.dumps(
        record,
        sort_keys=True,
        separators=(",", ":")
    )

    signature = sign_data(data_to_sign)

    record["digital_signature"] = signature

    return record