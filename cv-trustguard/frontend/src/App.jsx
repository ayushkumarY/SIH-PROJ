import { useEffect, useState } from "react";

import {
  getAnalysis,
  getSystemStatus,
  submitAnalystAction,
} from "./services/api";

import {
  ShieldCheck,
  AlertTriangle,
  FileWarning,
  Database,
  Brain,
  Fingerprint,
  RefreshCw,
  X,
  Eye,
} from "lucide-react";

/* =========================================================
   STATUS BADGE
========================================================= */

function StatusBadge({ status }) {
  const styles = {
    ACCEPT: "bg-green-100 text-green-700",
    REVIEW: "bg-yellow-100 text-yellow-700",
    QUARANTINE: "bg-red-100 text-red-700",

    CRITICAL: "bg-red-100 text-red-700",
    HIGH: "bg-orange-100 text-orange-700",
    MEDIUM: "bg-yellow-100 text-yellow-700",
    LOW: "bg-green-100 text-green-700",

    verified: "bg-green-100 text-green-700",
    trusted: "bg-green-100 text-green-700",
    suspicious: "bg-red-100 text-red-700",
    tampered: "bg-red-100 text-red-700",

    VERIFIED: "bg-green-100 text-green-700",
    TRUSTED: "bg-green-100 text-green-700",
    SUSPICIOUS: "bg-red-100 text-red-700",
    TAMPERED: "bg-red-100 text-red-700",
  };

  return (
    <span
      className={`px-3 py-1 rounded-full text-sm font-semibold ${styles[status] || "bg-gray-100 text-gray-700"
        }`}
    >
      {status || "UNKNOWN"}
    </span>
  );
}

/* =========================================================
   STAT CARD
========================================================= */

function StatCard({ title, value, description }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border p-5">
      <p className="text-gray-500 text-sm">{title}</p>

      <h2 className="text-3xl font-bold mt-2">{value}</h2>

      {description && (
        <p className="text-gray-500 text-sm mt-2">{description}</p>
      )}
    </div>
  );
}

/* =========================================================
   FINDING CARD
========================================================= */

function FindingCard({
  finding,
  onAction,
  onViewEvidence,
}) {
  const severityStyles = {
    CRITICAL: "border-red-200 bg-red-50",
    HIGH: "border-orange-200 bg-orange-50",
    MEDIUM: "border-yellow-200 bg-yellow-50",
    LOW: "border-green-200 bg-green-50",
  };

  const severity = finding.severity || "MEDIUM";

  return (
    <div
      className={`border rounded-xl p-5 ${severityStyles[severity] || "border-gray-200 bg-gray-50"
        }`}
    >
      {/* FINDING HEADER */}

      <div className="flex flex-col md:flex-row md:justify-between gap-4">
        <div className="flex gap-4">
          <div className="mt-1">
            {severity === "CRITICAL" || severity === "HIGH" ? (
              <AlertTriangle className="text-red-600" />
            ) : (
              <FileWarning className="text-yellow-600" />
            )}
          </div>

          <div>
            <h3 className="font-semibold">
              {finding.image || "Unknown Asset"}
            </h3>

            <p className="text-sm text-gray-500 mt-1">
              {finding.type || "Integrity Finding"}
            </p>
          </div>
        </div>

        <StatusBadge status={severity} />
      </div>

      {/* FINDING DETAILS */}

      <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* REASON */}

        <div>
          <p className="text-xs text-gray-500 uppercase">Reason</p>

          <p className="text-sm mt-1">
            {finding.reason || "No reason provided"}
          </p>
        </div>

        {/* CONFIDENCE */}

        <div>
          <p className="text-xs text-gray-500 uppercase">
            Confidence
          </p>

          <p className="font-semibold mt-1">
            {finding.confidence !== undefined
              ? `${Math.round(finding.confidence * 100)}%`
              : "N/A"}
          </p>
        </div>

        {/* RECOMMENDED ACTION */}

        <div>
          <p className="text-xs text-gray-500 uppercase">
            Recommended Action
          </p>

          <p className="font-semibold mt-1 uppercase">
            {finding.recommended_action || "review"}
          </p>
        </div>
      </div>

      {/* LABEL COMPARISON */}

      {(finding.assigned_label || finding.predicted_label) && (
        <div className="mt-4 pt-4 border-t text-sm">
          <span className="text-gray-500">
            Assigned Label:
          </span>{" "}

          <span className="font-medium">
            {finding.assigned_label || "N/A"}
          </span>

          {" → "}

          <span className="text-gray-500">
            Predicted:
          </span>{" "}

          <span className="font-medium">
            {finding.predicted_label || "N/A"}
          </span>
        </div>
      )}

      {/* VIEW EVIDENCE */}

      <div className="mt-5">
        <button
          type="button"
          onClick={() => onViewEvidence(finding)}
          className="px-4 py-2 rounded-lg border border-blue-300 text-blue-700 hover:bg-blue-50 transition flex items-center gap-2"
        >
          <Eye size={16} />
          View Evidence
        </button>
      </div>

      {/* ANALYST ACTION BUTTONS */}

      <div className="mt-5 pt-4 border-t flex flex-wrap gap-3">
        {/* ACCEPT */}

        <button
          type="button"
          onClick={() => onAction(finding, "accept")}
          className="px-4 py-2 rounded-lg border border-green-300 text-green-700 hover:bg-green-50 transition"
        >
          Accept
        </button>

        {/* REVIEW */}

        <button
          type="button"
          onClick={() => onAction(finding, "review")}
          className="px-4 py-2 rounded-lg border border-yellow-300 text-yellow-700 hover:bg-yellow-50 transition"
        >
          Review
        </button>

        {/* QUARANTINE */}

        <button
          type="button"
          onClick={() => onAction(finding, "quarantine")}
          className="px-4 py-2 rounded-lg border border-red-300 text-red-700 hover:bg-red-50 transition"
        >
          Quarantine
        </button>
      </div>
    </div>
  );
}

/* =========================================================
   MAIN APP
========================================================= */

function App() {
  const [analysis, setAnalysis] = useState(null);
  const [systemStatus, setSystemStatus] = useState(null);

  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  const [error, setError] = useState("");

  const [selectedFinding, setSelectedFinding] = useState(null);

  /* =======================================================
     LOAD DASHBOARD
  ======================================================= */

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError("");

      const [analysisResponse, systemResponse] =
        await Promise.all([
          getAnalysis(),
          getSystemStatus(),
        ]);

      setAnalysis(
        analysisResponse?.analysis || null
      );

      setSystemStatus(systemResponse || null);
    } catch (error) {
      console.error(
        "Dashboard loading error:",
        error
      );

      setError(
        "Unable to connect to CV TrustGuard backend."
      );
    } finally {
      setLoading(false);
    }
  };

  /* =======================================================
     ANALYST ACTION
  ======================================================= */

  const handleAnalystAction = async (
    finding,
    action
  ) => {
    try {
      console.log(
        "Sending analyst action:",
        action
      );

      console.log(
        "Finding:",
        finding
      );

      setActionLoading(true);

      const result = await submitAnalystAction(
        finding,
        action,
        "Security Analyst"
      );

      console.log(
        "Analyst decision response:",
        result
      );

      if (result?.status === "success") {
        alert(
          `Finding marked as ${action.toUpperCase()}`
        );

        await loadDashboard();
      } else {
        alert(
          result?.reason ||
          "Failed to record analyst decision."
        );
      }
    } catch (error) {
      console.error(
        "Analyst action error:",
        error
      );

      console.error(
        "Backend response:",
        error?.response?.data
      );

      alert(
        error?.response?.data?.reason ||
        error?.response?.data?.detail ||
        "Failed to record analyst decision."
      );
    } finally {
      setActionLoading(false);
    }
  };

  /* =======================================================
     INITIAL LOAD
  ======================================================= */

  useEffect(() => {
    loadDashboard();
  }, []);

  /* =======================================================
     LOADING SCREEN
  ======================================================= */

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <RefreshCw
            className="mx-auto animate-spin"
            size={32}
          />

          <h2 className="text-xl font-semibold mt-4">
            Loading CV TrustGuard...
          </h2>

          <p className="text-gray-500 mt-2">
            Running integrity checks
          </p>
        </div>
      </div>
    );
  }

  /* =======================================================
     ERROR SCREEN
  ======================================================= */

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h2 className="text-xl font-bold text-red-600">
            Backend Connection Failed
          </h2>

          <p className="text-gray-500 mt-2">
            {error}
          </p>

          <button
            type="button"
            onClick={loadDashboard}
            className="mt-4 px-5 py-2 bg-black text-white rounded-lg hover:bg-gray-800"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  /* =======================================================
     SAFE DATA
  ======================================================= */

  const summary =
    analysis?.summary || {};

  const provenance =
    systemStatus?.components?.provenance;

  const audit =
    systemStatus?.components?.audit_log;

  const contributors =
    analysis?.contributor_risk || [];

  /* =======================================================
     FINDINGS
  ======================================================= */

  const findings = [
    ...(analysis?.dataset_analysis
      ?.duplicate_findings || []),

    ...(analysis?.dataset_analysis
      ?.label_findings || []),

    ...(analysis?.dataset_analysis
      ?.visual_label_findings || []),

    ...(analysis?.dataset_analysis
      ?.ood_findings || []),

    ...(analysis?.dataset_analysis
      ?.trigger_findings || []),
  ];

  /* =======================================================
     IMAGE URL
  ======================================================= */

  const poisonedImages = [
    "flooded_1_car1.jpg",
    "flooded_2_car1.jpg",
    "flooded_3_car1.jpg",
    "flooded_4_car1.jpg",
    "flooded_5_car1.jpg",
    "ood_injected.jpg",
    "trigger_car1.jpg",
    "trigger_car2.jpg",
    "trigger_car3.jpg",
  ];

  const getImageUrl = (imageName) => {
    if (!imageName) return "";

    if (poisonedImages.includes(imageName)) {
      return `http://127.0.0.1:8000/poisoned-images/${encodeURIComponent(
        imageName
      )}`;
    }

    return `http://127.0.0.1:8000/coco-images/${encodeURIComponent(
      imageName
    )}`;
  };

  /* =======================================================
     CLOSE MODAL WITH ESCAPE
  ======================================================= */

  const closeEvidenceModal = () => {
    setSelectedFinding(null);
  };

  /* =======================================================
     UI
  ======================================================= */

  return (
    <div className="min-h-screen bg-gray-50">

      {/* ===================================================
          HEADER
      =================================================== */}

      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-6 py-5 flex justify-between items-center">

          <div>
            <h1 className="text-2xl font-bold">
              CV TrustGuard
            </h1>

            <p className="text-gray-500 text-sm">
              Computer Vision Integrity Assurance Platform
            </p>
          </div>

          <div className="flex items-center gap-3">
            <span className="w-3 h-3 rounded-full bg-green-500"></span>

            <span className="text-sm font-medium">
              System Online
            </span>
          </div>

        </div>
      </header>

      {/* ===================================================
          MAIN
      =================================================== */}

      <main className="max-w-7xl mx-auto px-6 py-8">

        {/* =================================================
            OVERALL TRUST DECISION
        ================================================= */}

        <div className="bg-white rounded-xl border shadow-sm p-6 mb-6">

          <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">

            <div>
              <p className="text-gray-500 text-sm">
                Overall Trust Decision
              </p>

              <div className="mt-2">
                <StatusBadge
                  status={analysis?.status}
                />
              </div>

              {analysis?.decision?.reason && (
                <p className="text-sm text-gray-500 mt-3">
                  {analysis.decision.reason}
                </p>
              )}
            </div>

            <button
              type="button"
              onClick={loadDashboard}
              disabled={loading}
              className="px-4 py-2 border rounded-lg hover:bg-gray-50 flex items-center gap-2 disabled:opacity-50"
            >
              <RefreshCw
                size={16}
                className={
                  loading
                    ? "animate-spin"
                    : ""
                }
              />

              Refresh Analysis
            </button>

          </div>
        </div>

        {/* =================================================
            SUMMARY CARDS
        ================================================= */}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">

          <StatCard
            title="Total Findings"
            value={summary.total_findings || 0}
            description="Detected integrity issues"
          />

          <StatCard
            title="Critical"
            value={summary.critical || 0}
            description="Requires immediate action"
          />

          <StatCard
            title="High"
            value={summary.high || 0}
            description="Requires investigation"
          />

          <StatCard
            title="Medium"
            value={summary.medium || 0}
            description="Requires review"
          />

        </div>

        {/* =================================================
            SECURITY STATUS
        ================================================= */}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mt-6">

          {/* PROVENANCE */}

          <div className="bg-white border rounded-xl shadow-sm p-6">

            <div className="flex justify-between">

              <div>
                <h2 className="font-semibold text-lg">
                  Inference Provenance
                </h2>

                <p className="text-sm text-gray-500 mt-1">
                  Image, model, record and signature verification
                </p>
              </div>

              <StatusBadge
                status={provenance?.status}
              />

            </div>

            <div className="grid grid-cols-2 gap-4 mt-6">

              {/* IMAGE */}

              <div>
                <p className="text-sm text-gray-500">
                  Image
                </p>

                <p className="font-semibold">
                  {provenance?.image_verified
                    ? "✓ Verified"
                    : "✗ Failed"}
                </p>
              </div>

              {/* MODEL */}

              <div>
                <p className="text-sm text-gray-500">
                  Model
                </p>

                <p className="font-semibold">
                  {provenance?.model_verified
                    ? "✓ Verified"
                    : "✗ Failed"}
                </p>
              </div>

              {/* RECORD */}

              <div>
                <p className="text-sm text-gray-500">
                  Record
                </p>

                <p className="font-semibold">
                  {provenance?.record_verified
                    ? "✓ Verified"
                    : "✗ Failed"}
                </p>
              </div>

              {/* SIGNATURE */}

              <div>
                <p className="text-sm text-gray-500">
                  Signature
                </p>

                <p className="font-semibold">
                  {provenance?.signature_verified
                    ? "✓ Verified"
                    : "✗ Failed"}
                </p>
              </div>

            </div>

          </div>

          {/* AUDIT */}

          <div className="bg-white border rounded-xl shadow-sm p-6">

            <div className="flex justify-between">

              <div>
                <h2 className="font-semibold text-lg">
                  Audit Trail
                </h2>

                <p className="text-sm text-gray-500 mt-1">
                  Tamper-evident hash chain
                </p>
              </div>

              <StatusBadge
                status={audit?.status}
              />

            </div>

            <div className="mt-6">

              <p className="text-sm text-gray-500">
                Total Audit Events
              </p>

              <p className="text-3xl font-bold mt-1">
                {audit?.total_events || 0}
              </p>

              <p className="text-sm text-gray-500 mt-2">
                {audit?.reason}
              </p>

            </div>

          </div>

        </div>

        {/* =================================================
            SECURITY OVERVIEW
        ================================================= */}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-6">

          {/* DATASET */}

          <div className="bg-white border rounded-xl p-5">

            <div className="flex items-center gap-3">

              <Database className="text-blue-600" />

              <div>
                <p className="text-sm text-gray-500">
                  Dataset Integrity
                </p>

                <p className="font-semibold">
                  {summary.total_findings > 0
                    ? "Issues Detected"
                    : "Clean"}
                </p>
              </div>

            </div>

          </div>

          {/* MODEL */}

          <div className="bg-white border rounded-xl p-5">

            <div className="flex items-center gap-3">

              <Brain className="text-purple-600" />

              <div>
                <p className="text-sm text-gray-500">
                  Model Integrity
                </p>

                <p className="font-semibold">
                  {analysis?.model_integrity
                    ?.integrity === "trusted"
                    ? "Trusted"
                    : "Suspicious"}
                </p>
              </div>

            </div>

          </div>

          {/* PROVENANCE */}

          <div className="bg-white border rounded-xl p-5">

            <div className="flex items-center gap-3">

              <Fingerprint className="text-green-600" />

              <div>
                <p className="text-sm text-gray-500">
                  Provenance
                </p>

                <p className="font-semibold">
                  {provenance?.status === "verified"
                    ? "Verified"
                    : "Failed"}
                </p>
              </div>

            </div>

          </div>

        </div>

        {/* =================================================
            CONTRIBUTOR RISK
        ================================================= */}

        <div className="bg-white border rounded-xl shadow-sm p-6 mt-6">

          <div className="mb-5">

            <h2 className="text-lg font-semibold">
              Contributor Risk
            </h2>

            <p className="text-sm text-gray-500">
              Aggregated integrity findings by contributor
            </p>

          </div>

          {contributors.length === 0 ? (

            <p className="text-gray-500">
              No contributor findings available.
            </p>

          ) : (

            <div className="overflow-x-auto">

              <table className="w-full text-left">

                <thead>

                  <tr className="border-b">

                    <th className="py-3">
                      Contributor
                    </th>

                    <th className="py-3">
                      Batch
                    </th>

                    <th className="py-3">
                      Findings
                    </th>

                    <th className="py-3">
                      Risk Score
                    </th>

                    <th className="py-3">
                      Risk Level
                    </th>

                  </tr>

                </thead>

                <tbody>

                  {contributors.map(
                    (contributor, index) => (

                      <tr
                        key={index}
                        className="border-b last:border-0"
                      >

                        <td className="py-4 font-medium">
                          {contributor.contributor}
                        </td>

                        <td className="py-4 text-gray-500">
                          {contributor.batch}
                        </td>

                        <td className="py-4">
                          {contributor.total_findings}
                        </td>

                        <td className="py-4 font-bold">
                          {contributor.risk_score}
                        </td>

                        <td className="py-4">

                          <StatusBadge
                            status={
                              contributor.risk_level
                            }
                          />

                        </td>

                      </tr>

                    )
                  )}

                </tbody>

              </table>

            </div>

          )}

        </div>

        {/* =================================================
            FINDINGS
        ================================================= */}

        <div className="bg-white border rounded-xl shadow-sm p-6 mt-6">

          <div className="flex flex-col md:flex-row md:justify-between gap-3 mb-6">

            <div>

              <h2 className="text-lg font-semibold">
                Detection Findings
              </h2>

              <p className="text-sm text-gray-500">
                Evidence detected during integrity analysis
              </p>

            </div>

            <div className="text-sm text-gray-500">
              {findings.length} finding(s)
            </div>

          </div>

          {findings.length === 0 ? (

            <div className="py-10 text-center">

              <ShieldCheck
                className="mx-auto text-green-500"
                size={40}
              />

              <p className="font-semibold mt-3">
                No integrity issues detected
              </p>

            </div>

          ) : (

            <div className="space-y-4">

              {findings.map(
                (finding, index) => (

                  <FindingCard
                    key={index}
                    finding={finding}
                    onAction={handleAnalystAction}
                    onViewEvidence={
                      setSelectedFinding
                    }
                  />

                )
              )}

            </div>

          )}

        </div>

        {/* =================================================
            ACTION STATUS
        ================================================= */}

        {actionLoading && (
          <div className="fixed bottom-6 right-6 bg-black text-white px-5 py-3 rounded-lg shadow-lg flex items-center gap-3 z-[60]">

            <RefreshCw
              size={18}
              className="animate-spin"
            />

            Recording analyst decision...

          </div>
        )}

        {/* =================================================
            EVIDENCE DETAILS MODAL
        ================================================= */}

        {selectedFinding && (

          <div
            className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4"
            onMouseDown={(e) => {
              if (e.target === e.currentTarget) {
                closeEvidenceModal();
              }
            }}
          >

            <div className="bg-white rounded-2xl shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">

              {/* =================================================
                  MODAL HEADER
              ================================================= */}

              <div className="sticky top-0 bg-white border-b p-6 flex justify-between items-center z-10">

                <div>

                  <h2 className="text-xl font-bold">
                    Evidence Details
                  </h2>

                  <p className="text-sm text-gray-500 mt-1">
                    Detailed integrity evidence for this finding
                  </p>

                </div>

                <button
                  type="button"
                  onClick={closeEvidenceModal}
                  className="p-2 rounded-lg hover:bg-gray-100"
                >
                  <X size={22} />
                </button>

              </div>

              {/* =================================================
                  MODAL CONTENT
              ================================================= */}

              <div className="p-6 space-y-6">

                {/* =================================================
                    AFFECTED ASSET
                ================================================= */}

                <div>

                  <p className="text-xs text-gray-500 uppercase">
                    Affected Asset
                  </p>

                  <p className="font-semibold mt-1">
                    {selectedFinding.image ||
                      "Unknown Asset"}
                  </p>

                </div>

                {/* =================================================
                    IMAGE PREVIEW
                ================================================= */}

                {selectedFinding.image && (

                  <div>

                    <p className="text-xs text-gray-500 uppercase mb-2">
                      Affected Image
                    </p>

                    <div className="border rounded-xl overflow-hidden bg-gray-100 min-h-[200px] flex items-center justify-center">

                      <img
                        src={getImageUrl(
                          selectedFinding.image
                        )}
                        alt={
                          selectedFinding.image
                        }
                        className="w-full max-h-[400px] object-contain"
                        onError={(e) => {
                          e.currentTarget.style.display =
                            "none";

                          const parent =
                            e.currentTarget.parentElement;

                          if (parent) {
                            parent.innerHTML =
                              '<p class="text-gray-500 p-6 text-center">Image could not be loaded.</p>';
                          }
                        }}
                      />

                    </div>

                    <p className="text-xs text-gray-500 mt-2">
                      File:{" "}
                      {selectedFinding.image}
                    </p>

                  </div>

                )}

                {/* =================================================
                    TYPE + SEVERITY
                ================================================= */}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-5">

                  <div>

                    <p className="text-xs text-gray-500 uppercase">
                      Detection Type
                    </p>

                    <p className="font-semibold mt-1">
                      {selectedFinding.type ||
                        "Integrity Finding"}
                    </p>

                  </div>

                  <div>

                    <p className="text-xs text-gray-500 uppercase">
                      Severity
                    </p>

                    <div className="mt-1">
                      <StatusBadge
                        status={
                          selectedFinding.severity ||
                          "MEDIUM"
                        }
                      />
                    </div>

                  </div>

                </div>

                {/* =================================================
                    CONFIDENCE
                ================================================= */}

                <div>

                  <p className="text-xs text-gray-500 uppercase">
                    Confidence
                  </p>

                  <p className="text-lg font-bold mt-1">

                    {selectedFinding.confidence !==
                      undefined
                      ? `${Math.round(
                        selectedFinding.confidence *
                        100
                      )}%`
                      : "N/A"}

                  </p>

                </div>

                {/* =================================================
                    REASON
                ================================================= */}

                <div className="bg-gray-50 rounded-xl p-4">

                  <p className="text-xs text-gray-500 uppercase">
                    Human-Readable Reason
                  </p>

                  <p className="text-sm mt-2">
                    {selectedFinding.reason ||
                      "No reason provided."}
                  </p>

                </div>

                {/* =================================================
                    LABEL INFORMATION
                ================================================= */}

                {(selectedFinding.assigned_label ||
                  selectedFinding.predicted_label) && (

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-5">

                      <div>

                        <p className="text-xs text-gray-500 uppercase">
                          Assigned Label
                        </p>

                        <p className="font-semibold mt-1">
                          {selectedFinding.assigned_label ||
                            "N/A"}
                        </p>

                      </div>

                      <div>

                        <p className="text-xs text-gray-500 uppercase">
                          Predicted Label
                        </p>

                        <p className="font-semibold mt-1">
                          {selectedFinding.predicted_label ||
                            "N/A"}
                        </p>

                      </div>

                    </div>

                  )}

                {/* =================================================
                    RECOMMENDED ACTION
                ================================================= */}

                <div>

                  <p className="text-xs text-gray-500 uppercase">
                    Recommended Action
                  </p>

                  <p className="font-semibold mt-1 uppercase">
                    {selectedFinding.recommended_action ||
                      "REVIEW"}
                  </p>

                </div>

                {/* =================================================
                    CRYPTOGRAPHIC EVIDENCE
                ================================================= */}

                <div className="border-t pt-6">

                  <div className="flex items-center gap-2 mb-4">

                    <Fingerprint
                      size={20}
                      className="text-green-600"
                    />

                    <h3 className="font-semibold text-lg">
                      Cryptographic Evidence
                    </h3>

                  </div>

                  <div className="space-y-4">

                    {/* IMAGE HASH */}

                    <div className="bg-gray-50 rounded-lg p-4">

                      <p className="text-xs text-gray-500 uppercase mb-1">
                        Image SHA-256
                      </p>

                      <p className="text-xs font-mono break-all">

                        {selectedFinding.image_hash ||
                          "Not available for this finding"}

                      </p>

                    </div>

                    {/* MODEL HASH */}

                    <div className="bg-gray-50 rounded-lg p-4">

                      <p className="text-xs text-gray-500 uppercase mb-1">
                        Model SHA-256
                      </p>

                      <p className="text-xs font-mono break-all">

                        {selectedFinding.model_hash ||
                          "Not available for this finding"}

                      </p>

                    </div>

                    {/* PROVENANCE STATUS */}

                    <div className="border rounded-lg p-4">

                      <p className="text-xs text-gray-500 uppercase mb-3">
                        Provenance Verification
                      </p>

                      <div className="grid grid-cols-2 gap-4">

                        <div>

                          <p className="text-sm text-gray-500">
                            Image
                          </p>

                          <p className="font-semibold">
                            {provenance?.image_verified
                              ? "✓ Verified"
                              : "✗ Failed"}
                          </p>

                        </div>

                        <div>

                          <p className="text-sm text-gray-500">
                            Model
                          </p>

                          <p className="font-semibold">
                            {provenance?.model_verified
                              ? "✓ Verified"
                              : "✗ Failed"}
                          </p>

                        </div>

                        <div>

                          <p className="text-sm text-gray-500">
                            Record
                          </p>

                          <p className="font-semibold">
                            {provenance?.record_verified
                              ? "✓ Verified"
                              : "✗ Failed"}
                          </p>

                        </div>

                        <div>

                          <p className="text-sm text-gray-500">
                            Digital Signature
                          </p>

                          <p className="font-semibold">
                            {provenance?.signature_verified
                              ? "✓ Verified"
                              : "✗ Failed"}
                          </p>

                        </div>

                      </div>

                    </div>

                    {/* OVERALL INTEGRITY */}

                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border rounded-lg p-4">

                      <div>

                        <p className="text-xs text-gray-500 uppercase">
                          Overall Provenance
                        </p>

                        <p className="font-semibold mt-1">
                          {provenance?.integrity ||
                            "Not verified"}
                        </p>

                      </div>

                      <StatusBadge
                        status={
                          provenance?.status ||
                          "UNKNOWN"
                        }
                      />

                    </div>

                    {/* PROVENANCE REASON */}

                    {provenance?.reason && (

                      <div className="bg-gray-50 rounded-lg p-4">

                        <p className="text-xs text-gray-500 uppercase">
                          Verification Reason
                        </p>

                        <p className="text-sm mt-2">
                          {provenance.reason}
                        </p>

                      </div>

                    )}

                  </div>

                </div>

              </div>

              {/* =================================================
                  MODAL FOOTER ACTIONS
              ================================================= */}

              <div className="sticky bottom-0 bg-white border-t p-6 flex flex-wrap justify-end gap-3">

                <button
                  type="button"
                  onClick={() => {
                    handleAnalystAction(
                      selectedFinding,
                      "accept"
                    );

                    setSelectedFinding(null);
                  }}
                  className="px-4 py-2 rounded-lg border border-green-300 text-green-700 hover:bg-green-50 transition"
                >
                  Accept
                </button>

                <button
                  type="button"
                  onClick={() => {
                    handleAnalystAction(
                      selectedFinding,
                      "review"
                    );

                    setSelectedFinding(null);
                  }}
                  className="px-4 py-2 rounded-lg border border-yellow-300 text-yellow-700 hover:bg-yellow-50 transition"
                >
                  Review
                </button>

                <button
                  type="button"
                  onClick={() => {
                    handleAnalystAction(
                      selectedFinding,
                      "quarantine"
                    );

                    setSelectedFinding(null);
                  }}
                  className="px-4 py-2 rounded-lg border border-red-300 text-red-700 hover:bg-red-50 transition"
                >
                  Quarantine
                </button>

                <button
                  type="button"
                  onClick={closeEvidenceModal}
                  className="px-4 py-2 rounded-lg border hover:bg-gray-50 transition"
                >
                  Close
                </button>

              </div>

            </div>

          </div>

        )}

      </main>

    </div>
  );
}

export default App;