import json
import hashlib
import os


AUDIT_FILE = "../reports/audit_log.json"


# ====================================
# HASH
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
# VERIFY AUDIT CHAIN
# ====================================

def verify_audit_chain():

    if not os.path.exists(AUDIT_FILE):

        return {
            "status": "error",
            "reason": "Audit log not found"
        }


    with open(
        AUDIT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        logs = json.load(file)


    previous_hash = None


    for index, event in enumerate(logs):

        stored_hash = event.get(
            "event_hash"
        )


        # Remove stored hash
        event_without_hash = event.copy()

        event_without_hash.pop(
            "event_hash",
            None
        )


        calculated_hash = calculate_hash(
            event_without_hash
        )


        # Check event hash

        if stored_hash != calculated_hash:

            return {

                "status": "tampered",

                "integrity": "suspicious",

                "failed_event":
                    event.get("event_id"),

                "reason":
                    "Audit event has been modified",

                "recommended_action":
                    "quarantine"
            }


        # Check chain

        if event.get(
            "previous_event_hash"
        ) != previous_hash:

            return {

                "status": "tampered",

                "integrity": "suspicious",

                "failed_event":
                    event.get("event_id"),

                "reason":
                    "Audit chain sequence has been modified",

                "recommended_action":
                    "quarantine"
            }


        previous_hash = stored_hash


    return {

        "status": "verified",

        "integrity": "trusted",

        "total_events":
            len(logs),

        "reason":
            "Audit log and hash chain are valid",

        "recommended_action":
            "accept"
    }


# ====================================
# MAIN
# ====================================

print("\n================================")
print("       AUDIT VERIFICATION")
print("================================")


result = verify_audit_chain()


print(
    json.dumps(
        result,
        indent=4
    )
)


print("\n================================")