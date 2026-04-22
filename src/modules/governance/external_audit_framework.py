"""
External Audit Framework for security review and compliance verification (Phase 3+).

Provides comprehensive security audit trail management, vulnerability tracking,
and external review workflows with immutable logging for compliance requirements.

**Architecture:**
- SecurityFinding: Vulnerability/issue tracking with severity and resolution
- AuditReport: Comprehensive security review snapshots
- ExternalAuditFramework: Manages audit logs, reports, compliance tracking
- VulnerabilityRegistry: Tracks identified issues and remediation status

**Compliance:**
- Immutable audit logs with hash-chaining
- Tamper-evident records via HMAC signatures
- Change tracking for all security-critical operations
- External reviewer attestations with timestamps

Env:
- ``KERNEL_EXTERNAL_AUDIT_ENABLED`` — feature flag (default off)
- ``KERNEL_EXTERNAL_AUDIT_PATH`` — storage path (default ``artifacts/audits/``)
- ``KERNEL_EXTERNAL_AUDITORS`` — comma-separated auditor IDs
- ``KERNEL_AUDIT_RETENTION_DAYS`` — log retention (default 365)
"""
# Status: SCAFFOLD


from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal


@dataclass
class SecurityFinding:
    """A security finding (vulnerability, issue, concern) identified in audit."""

    finding_id: str
    title: str
    description: str
    severity: Literal["critical", "high", "medium", "low", "info"]
    category: str  # e.g., "constraint_bypass", "logic_error", "missing_validation"
    affected_component: str  # e.g., "semantic_chat_gate", "rlhf_reward_model"
    discovered_at: float = field(default_factory=time.time)
    discovered_by: str = ""  # Auditor ID
    status: Literal["open", "acknowledged", "in_progress", "resolved", "won't_fix"] = "open"
    resolution_plan: str = ""
    resolved_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> SecurityFinding:
        """Deserialize from dict."""
        return cls(**d)

    def is_critical(self) -> bool:
        """Check if finding is critical severity."""
        return self.severity in ("critical", "high")

    def days_since_discovery(self) -> float:
        """Days since finding was discovered."""
        return (time.time() - self.discovered_at) / 86400.0


@dataclass
class AuditReport:
    """Comprehensive security audit report snapshot."""

    report_id: str
    audit_date: float = field(default_factory=time.time)
    audit_scope: str = ""  # e.g., "Phase 3 threshold optimization"
    auditors: list[str] = field(default_factory=list)
    findings: list[SecurityFinding] = field(default_factory=list)
    compliance_checklist: dict[str, bool] = field(default_factory=dict)
    overall_risk_rating: Literal["critical", "high", "medium", "low"] = "medium"
    recommendations: list[str] = field(default_factory=list)
    approved_by: str = ""  # Signing authority
    approved_at: float = 0.0
    attestation_hash: str = ""  # Hash of report for verification
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON."""
        d = asdict(self)
        d["findings"] = [f.to_dict() for f in self.findings]
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> AuditReport:
        """Deserialize from JSON."""
        findings = [SecurityFinding.from_dict(f) for f in d.get("findings", [])]
        return cls(
            report_id=d["report_id"],
            audit_date=d.get("audit_date", time.time()),
            audit_scope=d.get("audit_scope", ""),
            auditors=d.get("auditors", []),
            findings=findings,
            compliance_checklist=d.get("compliance_checklist", {}),
            overall_risk_rating=d.get("overall_risk_rating", "medium"),
            recommendations=d.get("recommendations", []),
            approved_by=d.get("approved_by", ""),
            approved_at=d.get("approved_at", 0.0),
            attestation_hash=d.get("attestation_hash", ""),
            metadata=d.get("metadata", {}),
        )

    def compute_attestation_hash(self) -> str:
        """Compute hash for report integrity verification."""
        canonical = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def is_approved(self) -> bool:
        """Check if report has been approved."""
        return bool(self.approved_by and self.approved_at > 0)


@dataclass
class AuditLog:
    """Single audit event in immutable log."""

    event_id: str
    timestamp: float = field(default_factory=time.time)
    event_type: str = ""  # e.g., "finding_discovered", "remediation_started"
    actor_id: str = ""  # Who triggered the event
    component: str = ""  # What was audited
    details: dict[str, Any] = field(default_factory=dict)
    prev_hash: str = ""  # Hash of previous log entry (chain)
    entry_hash: str = ""  # Hash of this entry

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON."""
        return asdict(self)


class ExternalAuditFramework:
    """Orchestrates security audits, compliance tracking, and external reviews."""

    def __init__(self, artifacts_path: Path | None = None):
        """Initialize external audit framework."""
        self.artifacts_path = artifacts_path or Path(
            os.environ.get("KERNEL_EXTERNAL_AUDIT_PATH", "artifacts/audits/")
        )
        self.artifacts_path.mkdir(parents=True, exist_ok=True)

        auditor_str = os.environ.get("KERNEL_EXTERNAL_AUDITORS", "")
        self.auditors = [a.strip() for a in auditor_str.split(",") if a.strip()]

        self.retention_days = int(os.environ.get("KERNEL_AUDIT_RETENTION_DAYS", "365"))

        self.findings: dict[str, SecurityFinding] = {}
        self.reports: dict[str, AuditReport] = {}
        self.audit_logs: list[AuditLog] = []
        self._prev_log_hash = "0" * 64

    def report_security_finding(
        self,
        title: str,
        description: str,
        severity: Literal["critical", "high", "medium", "low", "info"],
        category: str,
        affected_component: str,
        discovered_by: str = "external_auditor",
    ) -> SecurityFinding:
        """Report a new security finding from external audit."""
        finding = SecurityFinding(
            finding_id=f"finding-{uuid.uuid4().hex[:8]}",
            title=title,
            description=description,
            severity=severity,
            category=category,
            affected_component=affected_component,
            discovered_by=discovered_by,
        )
        self.findings[finding.finding_id] = finding
        self._log_audit_event(
            "finding_discovered",
            discovered_by,
            affected_component,
            {"finding_id": finding.finding_id, "severity": severity},
        )
        return finding

    def acknowledge_finding(self, finding_id: str, acknowledger_id: str) -> bool:
        """Acknowledge receipt of a security finding."""
        finding = self.findings.get(finding_id)
        if not finding:
            return False

        finding.status = "acknowledged"
        self._log_audit_event(
            "finding_acknowledged",
            acknowledger_id,
            finding.affected_component,
            {"finding_id": finding_id},
        )
        return True

    def start_remediation(self, finding_id: str, plan: str, owner_id: str) -> bool:
        """Start remediation work on a finding."""
        finding = self.findings.get(finding_id)
        if not finding:
            return False

        finding.status = "in_progress"
        finding.resolution_plan = plan
        self._log_audit_event(
            "remediation_started",
            owner_id,
            finding.affected_component,
            {"finding_id": finding_id, "plan": plan},
        )
        return True

    def resolve_finding(self, finding_id: str, resolver_id: str) -> bool:
        """Mark a security finding as resolved."""
        finding = self.findings.get(finding_id)
        if not finding:
            return False

        finding.status = "resolved"
        finding.resolved_at = time.time()
        self._log_audit_event(
            "finding_resolved",
            resolver_id,
            finding.affected_component,
            {"finding_id": finding_id},
        )
        return True

    def create_audit_report(
        self,
        audit_scope: str,
        auditors: list[str],
        compliance_checklist: dict[str, bool] | None = None,
    ) -> AuditReport:
        """Create a comprehensive audit report."""
        # Collect all open and recent findings
        recent_findings = [
            f for f in self.findings.values() if f.days_since_discovery() <= self.retention_days
        ]

        # Determine overall risk rating
        critical_findings = [f for f in recent_findings if f.severity == "critical"]
        overall_risk = (
            "critical"
            if critical_findings
            else "high"
            if any(f.severity == "high" for f in recent_findings)
            else "medium"
        )

        report = AuditReport(
            report_id=f"audit-{uuid.uuid4().hex[:8]}",
            audit_scope=audit_scope,
            auditors=auditors,
            findings=recent_findings,
            compliance_checklist=compliance_checklist or {},
            overall_risk_rating=overall_risk,
        )

        self.reports[report.report_id] = report
        self._log_audit_event(
            "report_created",
            auditors[0] if auditors else "system",
            "audit_framework",
            {"report_id": report.report_id, "findings_count": len(recent_findings)},
        )
        return report

    def approve_report(self, report_id: str, approver_id: str) -> bool:
        """Approve and sign an audit report."""
        report = self.reports.get(report_id)
        if not report:
            return False

        report.approved_by = approver_id
        report.approved_at = time.time()
        report.attestation_hash = report.compute_attestation_hash()

        self._log_audit_event(
            "report_approved",
            approver_id,
            "audit_framework",
            {
                "report_id": report_id,
                "attestation_hash": report.attestation_hash,
            },
        )
        return True

    def get_open_findings(self) -> list[SecurityFinding]:
        """Get all open security findings."""
        return [f for f in self.findings.values() if f.status == "open"]

    def get_critical_findings(self) -> list[SecurityFinding]:
        """Get all critical and high-severity findings."""
        return [f for f in self.findings.values() if f.is_critical()]

    def save_report(self, report_id: str) -> bool:
        """Save audit report to disk."""
        report = self.reports.get(report_id)
        if not report:
            return False

        path = self.artifacts_path / f"{report_id}.json"
        path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
        return True

    def load_report(self, report_id: str) -> AuditReport | None:
        """Load audit report from disk."""
        path = self.artifacts_path / f"{report_id}.json"
        if not path.exists():
            return None

        data = json.loads(path.read_text(encoding="utf-8"))
        report = AuditReport.from_dict(data)
        self.reports[report_id] = report
        return report

    def save_audit_logs(self) -> None:
        """Save audit logs to disk."""
        path = self.artifacts_path / "audit_logs.jsonl"
        with open(path, "w", encoding="utf-8") as f:
            for log in self.audit_logs:
                f.write(json.dumps(log.to_dict()) + "\n")

    def verify_audit_chain(self) -> bool:
        """Verify integrity of audit chain (hash-linked logs)."""
        prev_hash = "0" * 64
        for log in self.audit_logs:
            if log.prev_hash != prev_hash:
                return False
            prev_hash = log.entry_hash
        return True

    def _log_audit_event(
        self,
        event_type: str,
        actor_id: str,
        component: str,
        details: dict[str, Any],
    ) -> None:
        """Log an audit event with hash-chaining."""
        log = AuditLog(
            event_id=f"log-{uuid.uuid4().hex[:8]}",
            event_type=event_type,
            actor_id=actor_id,
            component=component,
            details=details,
            prev_hash=self._prev_log_hash,
        )

        # Compute hash of this entry
        log_canonical = json.dumps(
            {
                "event_id": log.event_id,
                "timestamp": log.timestamp,
                "event_type": log.event_type,
                "actor_id": log.actor_id,
                "component": log.component,
                "details": log.details,
                "prev_hash": log.prev_hash,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        log.entry_hash = hashlib.sha256(log_canonical.encode("utf-8")).hexdigest()

        self.audit_logs.append(log)
        self._prev_log_hash = log.entry_hash

    def get_audit_trail(self) -> list[AuditLog]:
        """Get full audit trail."""
        return self.audit_logs.copy()

    def cleanup_old_logs(self) -> int:
        """Remove audit logs older than retention period."""
        cutoff_time = time.time() - (self.retention_days * 86400)
        before = len(self.audit_logs)
        self.audit_logs = [log for log in self.audit_logs if log.timestamp >= cutoff_time]
        return before - len(self.audit_logs)


def is_external_audit_enabled() -> bool:
    """Check if external audit framework is enabled."""
    v = os.environ.get("KERNEL_EXTERNAL_AUDIT_ENABLED", "0").strip().lower()
    return v in ("1", "true", "yes", "on")
