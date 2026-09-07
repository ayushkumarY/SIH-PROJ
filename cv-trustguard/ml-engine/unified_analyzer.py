import os

from detectors.duplicate_detector import find_duplicates
from detectors.label_detector import detect_label_anomalies
from detectors.visual_label_detector import detect_visual_label_anomalies
from detectors.ood_detector import detect_ood_images
from detectors.trigger_detector import scan_dataset
from detectors.contributor_risk import calculate_contributor_risk
from detectors.model_detector import verify_model


# ==========================================
# PATHS
# ==========================================

CLEAN_IMAGES = "../datasets/coco/images"
POISONED_IMAGES = "../datasets/poisoned/images"
COCO_ANNOTATION = "../datasets/coco/annotations/instances.json"
CONTRIBUTOR_METADATA = "../datasets/metadata/contributors.json"

MODEL_PATH = "../models/trustguard_resnet50.pth"
MODEL_MANIFEST = "../models/model_manifest.json"


# ==========================================
# UNIFIED ANALYSIS
# ==========================================

def run_unified_analysis():

    print("\n================================")
    print("       CV TRUSTGUARD ANALYSIS")
    print("================================")

    # ====================================
    # DATASET ANALYSIS
    # ====================================

    print("\n[1] Duplicate detection...")
    duplicate_findings = find_duplicates(CLEAN_IMAGES)

    print("\n[2] Label integrity detection...")
    label_findings = detect_label_anomalies(COCO_ANNOTATION)

    print("\n[3] Visual label analysis...")
    visual_label_findings = detect_visual_label_anomalies(
        COCO_ANNOTATION,
        CLEAN_IMAGES
    )

    print("\n[4] OOD detection...")
    ood_findings = detect_ood_images(CLEAN_IMAGES)

    print("\n[5] Trigger detection...")
    trigger_findings = scan_dataset(POISONED_IMAGES)

    all_findings = (
        duplicate_findings
        + label_findings
        + visual_label_findings
        + ood_findings
        + trigger_findings
    )

    # ====================================
    # CONTRIBUTOR RISK
    # ====================================

    print("\n[6] Contributor risk analysis...")

    contributor_risk = calculate_contributor_risk(
        all_findings,
        CONTRIBUTOR_METADATA
    )

    # ====================================
    # MODEL INTEGRITY
    # ====================================

    print("\n[7] Model integrity verification...")

    model_result = verify_model(
        MODEL_PATH,
        MODEL_MANIFEST
    )

    # ====================================
    # FINDING COUNTS
    # ====================================

    critical_count = 0
    high_count = 0
    medium_count = 0
    low_count = 0

    for finding in all_findings:

        severity = finding.get(
            "severity",
            "MEDIUM"
        )

        if severity == "CRITICAL":
            critical_count += 1

        elif severity == "HIGH":
            high_count += 1

        elif severity == "MEDIUM":
            medium_count += 1

        elif severity == "LOW":
            low_count += 1

    # ====================================
    # CONTRIBUTOR RISK CHECK
    # ====================================

    contributor_critical = any(
        contributor.get("risk_level") == "CRITICAL"
        for contributor in contributor_risk
    )

    contributor_high = any(
        contributor.get("risk_level") == "HIGH"
        for contributor in contributor_risk
    )

    # ====================================
    # MODEL RISK CHECK
    # ====================================

    model_integrity = model_result.get(
        "integrity",
        "unknown"
    )

    model_critical = (
        model_integrity == "suspicious"
        and model_result.get("severity") == "CRITICAL"
    )

    # ====================================
    # FINAL TRUST DECISION
    # ====================================

    if model_critical:

        overall_status = "QUARANTINE"

        final_reason = (
            "Model integrity verification failed."
        )

    elif critical_count > 0:

        overall_status = "QUARANTINE"

        final_reason = (
            "Critical dataset integrity findings detected."
        )

    elif contributor_critical:

        overall_status = "QUARANTINE"

        final_reason = (
            "One or more contributors have critical risk."
        )

    elif high_count > 0 or contributor_high:

        overall_status = "REVIEW"

        final_reason = (
            "High-risk integrity findings require analyst review."
        )

    elif medium_count > 0:

        overall_status = "REVIEW"

        final_reason = (
            "Medium-risk integrity findings require review."
        )

    else:

        overall_status = "ACCEPT"

        final_reason = (
            "No significant integrity anomalies detected."
        )

    # ====================================
    # REPORT
    # ====================================

    report = {

        "system": "CV TrustGuard",

        "status": overall_status,

        "decision": {
            "status": overall_status,
            "reason": final_reason
        },

        "summary": {

            "total_findings": len(all_findings),

            "critical": critical_count,

            "high": high_count,

            "medium": medium_count,

            "low": low_count
        },

        "dataset_analysis": {

            "duplicate_findings":
                duplicate_findings,

            "label_findings":
                label_findings,

            "visual_label_findings":
                visual_label_findings,

            "ood_findings":
                ood_findings,

            "trigger_findings":
                trigger_findings
        },

        "contributor_risk":
            contributor_risk,

        "model_integrity":
            model_result,

        "recommended_action":
            overall_status.lower()
    }

    # ====================================
    # PRINT RESULT
    # ====================================

    print("\n================================")
    print("      ANALYSIS COMPLETE")
    print("================================")

    print(
        f"\nOverall Status: {overall_status}"
    )

    print(
        f"Decision Reason: {final_reason}"
    )

    print(
        f"Total Findings: {len(all_findings)}"
    )

    print(
        f"Critical: {critical_count}"
    )

    print(
        f"High: {high_count}"
    )

    print(
        f"Medium: {medium_count}"
    )

    print(
        f"Low: {low_count}"
    )

    return report