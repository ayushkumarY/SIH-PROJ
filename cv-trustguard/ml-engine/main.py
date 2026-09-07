from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from unified_analyzer import run_unified_analysis

from provenance.audit_log import add_audit_event
from provenance.verify_audit import verify_audit_chain

from verify_provenance import verify_provenance
from analyst_actions import process_analyst_action
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles

# ====================================
# APP
# ====================================

app = FastAPI(
    title="CV TrustGuard",
    description="Trustworthy Computer Vision Integrity Assurance System",
    version="1.0.0"
)

app.mount(
    "/coco-images",
    StaticFiles(directory="../datasets/coco/images"),
    name="coco-images"
)

app.mount(
    "/poisoned-images",
    StaticFiles(directory="../datasets/poisoned/images"),
    name="poisoned-images"
)

# ====================================
# CORS
# ====================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ====================================
# ROOT
# ====================================

@app.get("/")
def root():

    return {
        "system": "CV TrustGuard",
        "status": "running",
        "version": "1.0.0"
    }


# ====================================
# HEALTH CHECK
# ====================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "CV TrustGuard ML Engine"
    }


# ====================================
# COMPLETE ANALYSIS
# ====================================

@app.get("/analyze")
def analyze():

    try:

        report = run_unified_analysis()

        # Add successful analysis to audit log
        add_audit_event(
            event_type="DATASET_ANALYSIS",
            status=report.get("status", "UNKNOWN"),
            reason="Unified CV TrustGuard analysis completed",
            report=report
        )

        return {
            "status": "success",
            "analysis": report
        }

    except Exception as error:

        add_audit_event(
            event_type="DATASET_ANALYSIS",
            status="ERROR",
            reason=f"Analysis failed: {error}",
            report=None
        )

        return {
            "status": "error",
            "message": str(error)
        }


# ====================================
# PROVENANCE STATUS
# ====================================

@app.get("/provenance-status")
def provenance_status():

    record_file = "../reports/inference_record.json"

    result = verify_provenance(
        record_file
    )

    return {
        "status": "success",
        "analysis": "Inference Provenance Verification",
        "provenance": result
    }


# ====================================
# AUDIT STATUS
# ====================================

@app.get("/audit-status")
def audit_status():

    result = verify_audit_chain()

    return {
        "status": "success",
        "analysis": "Tamper-Evident Audit Log Verification",
        "audit": result
    }


# ====================================
# SYSTEM STATUS
# ====================================

@app.get("/system-status")
def system_status():

    provenance_result = verify_provenance(
        "../reports/inference_record.json"
    )

    audit_result = verify_audit_chain()

    return {
        "system": "CV TrustGuard",
        "status": "online",
        "components": {
            "dataset_analysis": "available",
            "model_integrity": "available",
            "provenance": provenance_result,
            "audit_log": audit_result
        }
    }

# ====================================
# ANALYST GOVERNANCE
# ====================================

class AnalystActionRequest(BaseModel):

    action: str

    analyst: str = "Analyst"

    finding: dict

@app.post("/analyst-action")
def analyst_action(
    request: AnalystActionRequest
):

    result = process_analyst_action(
        finding=request.finding,
        action=request.action,
        analyst=request.analyst
    )

    return result