import json
import os
import hashlib
from datetime import datetime, timezone
from uuid import uuid4


AUDIT_FILE = "../reports/audit_log.json"


# ====================================
# HASH DATA
# ====================================

def calculate_hash(data):

    data_string = json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":")
    )

    return hashlib.sha256(
        data_string.encode("utf-8")
    ).hexdigest()


# ====================================
# LOAD AUDIT LOG
# ====================================

def load_audit_log():

    if not os.path.exists(AUDIT_FILE):
        return []

    with open(
        AUDIT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ====================================
# SAVE AUDIT LOG
# ====================================

def save_audit_log(logs):

    os.makedirs(
        os.path.dirname(AUDIT_FILE),
        exist_ok=True
    )

    with open(
        AUDIT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            logs,
            file,
            indent=4
        )


# ====================================
# ADD AUDIT EVENT
# ====================================

def add_audit_event(
    event_type,
    status,
    reason,
    report=None
):

    logs = load_audit_log()


    # --------------------------------
    # Previous hash
    # --------------------------------

    previous_hash = None

    if logs:

        previous_hash = logs[-1].get(
            "event_hash"
        )


    # --------------------------------
    # Create event
    # --------------------------------

    event = {

        "event_id": str(uuid4()),

        "sequence": len(logs) + 1,

        "timestamp":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "event_type":
            event_type,

        "status":
            status,

        "reason":
            reason,

        "previous_event_hash":
            previous_hash,

        "report":
            report
    }


    # --------------------------------
    # Event hash
    # --------------------------------

    event_hash = calculate_hash(
        event
    )

    event["event_hash"] = event_hash


    # --------------------------------
    # Save
    # --------------------------------

    logs.append(event)

    save_audit_log(logs)


    return event