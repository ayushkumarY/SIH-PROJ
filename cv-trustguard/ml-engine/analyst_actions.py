from datetime import datetime, timezone
from uuid import uuid4

from provenance.audit_log import add_audit_event


VALID_ACTIONS = {
    "accept",
    "review",
    "quarantine"
}


def process_analyst_action(
    finding,
    action,
    analyst="Analyst"
):

    action = action.lower().strip()

    if action not in VALID_ACTIONS:

        return {
            "status": "error",
            "reason": (
                "Invalid action. "
                "Use accept, review or quarantine."
            )
        }

    event = add_audit_event(
        event_type="ANALYST_DECISION",
        status=action.upper(),
        reason=f"Analyst selected {action}",
        report={
            "finding": finding,
            "analyst": analyst
        }
    )

    return {
        "status": "success",
        "decision_id": str(uuid4()),
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "analyst": analyst,
        "action": action,
        "finding": finding,
        "audit_event_id": event["event_id"],
        "message": (
            f"Finding marked as {action} "
            "and recorded in audit log."
        )
    }