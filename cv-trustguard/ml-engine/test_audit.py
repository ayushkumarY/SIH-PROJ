from provenance.audit_log import add_audit_event


print("\n================================")
print("          AUDIT LOG")
print("================================")


event = add_audit_event(
    event_type="INFERENCE_VERIFICATION",
    record_id="075bd9f0-f30e-43fc-8685-2104c60e362f",
    status="VERIFIED",
    reason="Image, model and provenance record verified successfully."
)


print("\nAudit event created:")

print(event)

print("\n================================")