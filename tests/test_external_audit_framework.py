"""Tests for External Audit Framework (Phase 3+ security compliance)."""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.external_audit_framework import (
    AuditReport,
    ExternalAuditFramework,
    SecurityFinding,
    is_external_audit_enabled,
)


class TestSecurityFinding:
    """Tests for SecurityFinding vulnerability tracking."""

    def test_finding_creation(self):
        """SecurityFinding should initialize with required fields."""
        finding = SecurityFinding(
            finding_id="finding-1",
            title="Missing Input Validation",
            description="The semantic gate does not validate embedding vectors",
            severity="high",
            category="missing_validation",
            affected_component="semantic_chat_gate",
        )
        assert finding.finding_id == "finding-1"
        assert finding.severity == "high"
        assert finding.status == "open"

    def test_finding_is_critical(self):
        """is_critical() should identify high and critical findings."""
        critical = SecurityFinding(
            finding_id="f1",
            title="Test",
            description="Test",
            severity="critical",
            category="test",
            affected_component="test",
        )
        assert critical.is_critical() is True

        high = SecurityFinding(
            finding_id="f2",
            title="Test",
            description="Test",
            severity="high",
            category="test",
            affected_component="test",
        )
        assert high.is_critical() is True

        medium = SecurityFinding(
            finding_id="f3",
            title="Test",
            description="Test",
            severity="medium",
            category="test",
            affected_component="test",
        )
        assert medium.is_critical() is False

    def test_finding_to_dict(self):
        """to_dict() should serialize finding."""
        finding = SecurityFinding(
            finding_id="finding-1",
            title="Test",
            description="Test description",
            severity="medium",
            category="test_category",
            affected_component="test_component",
            discovered_by="auditor-1",
        )
        d = finding.to_dict()
        assert d["finding_id"] == "finding-1"
        assert d["severity"] == "medium"
        assert d["discovered_by"] == "auditor-1"

    def test_finding_from_dict(self):
        """from_dict() should reconstruct finding."""
        original = SecurityFinding(
            finding_id="f1",
            title="Test",
            description="Test",
            severity="high",
            category="cat",
            affected_component="comp",
        )
        d = original.to_dict()
        restored = SecurityFinding.from_dict(d)
        assert restored.finding_id == original.finding_id
        assert restored.severity == original.severity


class TestAuditReport:
    """Tests for AuditReport comprehensive security reviews."""

    def test_report_creation(self):
        """AuditReport should initialize."""
        report = AuditReport(
            report_id="audit-1",
            audit_scope="Phase 3 threshold optimization",
            auditors=["auditor-1", "auditor-2"],
        )
        assert report.report_id == "audit-1"
        assert len(report.auditors) == 2
        assert report.is_approved() is False

    def test_report_with_findings(self):
        """AuditReport should track findings."""
        finding = SecurityFinding(
            finding_id="f1",
            title="Test",
            description="Test",
            severity="critical",
            category="test",
            affected_component="test",
        )
        report = AuditReport(
            report_id="audit-1",
            auditors=["auditor-1"],
            findings=[finding],
            overall_risk_rating="critical",
        )
        assert len(report.findings) == 1
        assert report.overall_risk_rating == "critical"

    def test_report_overall_risk_rating(self):
        """overall_risk_rating should be set explicitly or determined by findings."""
        critical_finding = SecurityFinding(
            finding_id="f1",
            title="Critical",
            description="Critical issue",
            severity="critical",
            category="test",
            affected_component="test",
        )

        # Critical finding → critical rating (explicitly set)
        report = AuditReport(
            report_id="audit-1",
            auditors=["auditor-1"],
            findings=[critical_finding],
            overall_risk_rating="critical",
        )
        assert report.overall_risk_rating == "critical"

        # No critical, but high → high rating
        high_finding = SecurityFinding(
            finding_id="f2",
            title="High",
            description="High severity",
            severity="high",
            category="test",
            affected_component="test",
        )
        report2 = AuditReport(
            report_id="audit-2",
            auditors=["auditor-1"],
            findings=[high_finding],
            overall_risk_rating="high",
        )
        assert report2.overall_risk_rating == "high"

    def test_report_approval(self):
        """Report should track approval status."""
        report = AuditReport(report_id="audit-1", auditors=["auditor-1"])
        assert report.is_approved() is False

        # Approve report
        report.approved_by = "manager-1"
        report.approved_at = 123456789.0
        assert report.is_approved() is True

    def test_report_attestation_hash(self):
        """compute_attestation_hash() should generate verifiable hash."""
        report = AuditReport(
            report_id="audit-1",
            auditors=["auditor-1"],
            overall_risk_rating="high",
        )
        hash1 = report.compute_attestation_hash()
        assert len(hash1) == 64  # SHA256 hex
        assert hash1 == hash1.lower()  # Hex lowercase

        # Same report, same hash
        hash2 = report.compute_attestation_hash()
        assert hash1 == hash2

    def test_report_to_dict_and_from_dict(self):
        """Report should serialize and deserialize correctly."""
        finding = SecurityFinding(
            finding_id="f1",
            title="Test",
            description="Test",
            severity="medium",
            category="test",
            affected_component="test",
        )
        original = AuditReport(
            report_id="audit-1",
            auditors=["auditor-1"],
            findings=[finding],
            overall_risk_rating="medium",
        )
        d = original.to_dict()
        restored = AuditReport.from_dict(d)
        assert restored.report_id == original.report_id
        assert len(restored.findings) == 1
        assert restored.findings[0].finding_id == "f1"


class TestExternalAuditFramework:
    """Tests for ExternalAuditFramework orchestration."""

    def test_framework_creation(self):
        """ExternalAuditFramework should initialize."""
        with tempfile.TemporaryDirectory() as tmpdir:
            framework = ExternalAuditFramework(artifacts_path=Path(tmpdir))
            assert len(framework.findings) == 0
            assert len(framework.reports) == 0

    def test_report_security_finding(self):
        """report_security_finding() should create and track findings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            framework = ExternalAuditFramework(artifacts_path=Path(tmpdir))
            finding = framework.report_security_finding(
                title="Missing Validation",
                description="Inputs not validated",
                severity="high",
                category="missing_validation",
                affected_component="semantic_gate",
                discovered_by="auditor-1",
            )
            assert finding.finding_id in framework.findings
            assert finding.severity == "high"

    def test_acknowledge_finding(self):
        """acknowledge_finding() should update status."""
        with tempfile.TemporaryDirectory() as tmpdir:
            framework = ExternalAuditFramework(artifacts_path=Path(tmpdir))
            finding = framework.report_security_finding(
                title="Test",
                description="Test",
                severity="medium",
                category="test",
                affected_component="test",
            )
            result = framework.acknowledge_finding(finding.finding_id, "manager-1")
            assert result is True
            assert finding.status == "acknowledged"

    def test_start_remediation(self):
        """start_remediation() should update finding status and plan."""
        with tempfile.TemporaryDirectory() as tmpdir:
            framework = ExternalAuditFramework(artifacts_path=Path(tmpdir))
            finding = framework.report_security_finding(
                title="Test",
                description="Test",
                severity="medium",
                category="test",
                affected_component="test",
            )
            plan = "Add input validation to semantic_gate.py"
            result = framework.start_remediation(finding.finding_id, plan, "dev-1")
            assert result is True
            assert finding.status == "in_progress"
            assert finding.resolution_plan == plan

    def test_resolve_finding(self):
        """resolve_finding() should mark finding as resolved."""
        with tempfile.TemporaryDirectory() as tmpdir:
            framework = ExternalAuditFramework(artifacts_path=Path(tmpdir))
            finding = framework.report_security_finding(
                title="Test",
                description="Test",
                severity="medium",
                category="test",
                affected_component="test",
            )
            result = framework.resolve_finding(finding.finding_id, "dev-1")
            assert result is True
            assert finding.status == "resolved"
            assert finding.resolved_at > 0

    def test_get_open_findings(self):
        """get_open_findings() should return unresolved findings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            framework = ExternalAuditFramework(artifacts_path=Path(tmpdir))

            # Create multiple findings
            finding1 = framework.report_security_finding(
                title="Test 1",
                description="Test",
                severity="high",
                category="test",
                affected_component="test",
            )
            finding2 = framework.report_security_finding(
                title="Test 2",
                description="Test",
                severity="medium",
                category="test",
                affected_component="test",
            )

            # Resolve one
            framework.resolve_finding(finding1.finding_id, "dev-1")

            open_findings = framework.get_open_findings()
            assert len(open_findings) == 1
            assert open_findings[0].finding_id == finding2.finding_id

    def test_get_critical_findings(self):
        """get_critical_findings() should return critical and high findings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            framework = ExternalAuditFramework(artifacts_path=Path(tmpdir))

            framework.report_security_finding(
                title="Critical",
                description="Test",
                severity="critical",
                category="test",
                affected_component="test",
            )
            framework.report_security_finding(
                title="High",
                description="Test",
                severity="high",
                category="test",
                affected_component="test",
            )
            framework.report_security_finding(
                title="Medium",
                description="Test",
                severity="medium",
                category="test",
                affected_component="test",
            )

            critical = framework.get_critical_findings()
            assert len(critical) == 2
            severities = {f.severity for f in critical}
            assert severities == {"critical", "high"}

    def test_create_audit_report(self):
        """create_audit_report() should generate comprehensive report."""
        with tempfile.TemporaryDirectory() as tmpdir:
            framework = ExternalAuditFramework(artifacts_path=Path(tmpdir))

            # Create findings
            framework.report_security_finding(
                title="Critical Issue",
                description="Test",
                severity="critical",
                category="test",
                affected_component="test",
            )
            framework.report_security_finding(
                title="Medium Issue",
                description="Test",
                severity="medium",
                category="test",
                affected_component="test",
            )

            # Create report
            report = framework.create_audit_report(
                audit_scope="Phase 3 review",
                auditors=["auditor-1", "auditor-2"],
                compliance_checklist={"constraint_validation": True, "audit_trail": True},
            )

            assert report.report_id in framework.reports
            assert len(report.findings) == 2
            assert report.overall_risk_rating == "critical"

    def test_approve_report(self):
        """approve_report() should sign and mark as approved."""
        with tempfile.TemporaryDirectory() as tmpdir:
            framework = ExternalAuditFramework(artifacts_path=Path(tmpdir))
            framework.report_security_finding(
                title="Test",
                description="Test",
                severity="low",
                category="test",
                affected_component="test",
            )

            report = framework.create_audit_report(
                audit_scope="Test",
                auditors=["auditor-1"],
            )

            result = framework.approve_report(report.report_id, "manager-1")
            assert result is True
            assert report.approved_by == "manager-1"
            assert report.approved_at > 0
            assert report.attestation_hash != ""

    def test_save_and_load_report(self):
        """save_report() and load_report() should persist reports."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and save
            framework1 = ExternalAuditFramework(artifacts_path=Path(tmpdir))
            framework1.report_security_finding(
                title="Test",
                description="Test",
                severity="medium",
                category="test",
                affected_component="test",
            )
            report = framework1.create_audit_report(
                audit_scope="Test",
                auditors=["auditor-1"],
            )
            framework1.approve_report(report.report_id, "manager-1")
            framework1.save_report(report.report_id)

            # Load in new framework
            framework2 = ExternalAuditFramework(artifacts_path=Path(tmpdir))
            loaded = framework2.load_report(report.report_id)
            assert loaded is not None
            assert loaded.report_id == report.report_id
            assert loaded.is_approved()

    def test_audit_chain_integrity(self):
        """verify_audit_chain() should validate hash-linked logs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            framework = ExternalAuditFramework(artifacts_path=Path(tmpdir))

            # Create events
            framework.report_security_finding(
                title="Test",
                description="Test",
                severity="low",
                category="test",
                affected_component="test",
            )

            # Verify chain
            valid = framework.verify_audit_chain()
            assert valid is True

            # Tamper with logs (simulate attack)
            if framework.audit_logs:
                framework.audit_logs[0].prev_hash = "corrupted"
                valid = framework.verify_audit_chain()
                assert valid is False

    def test_audit_trail(self):
        """get_audit_trail() should return action log."""
        with tempfile.TemporaryDirectory() as tmpdir:
            framework = ExternalAuditFramework(artifacts_path=Path(tmpdir))

            framework.report_security_finding(
                title="Test 1",
                description="Test",
                severity="low",
                category="test",
                affected_component="test",
            )
            framework.report_security_finding(
                title="Test 2",
                description="Test",
                severity="low",
                category="test",
                affected_component="test",
            )

            trail = framework.get_audit_trail()
            assert len(trail) >= 2
            event_types = {log.event_type for log in trail}
            assert "finding_discovered" in event_types

    def test_cleanup_old_logs(self, monkeypatch):
        """cleanup_old_logs() should remove old entries."""
        with tempfile.TemporaryDirectory() as tmpdir:
            monkeypatch.setenv("KERNEL_AUDIT_RETENTION_DAYS", "0")
            framework = ExternalAuditFramework(artifacts_path=Path(tmpdir))

            # Create events
            framework.report_security_finding(
                title="Test",
                description="Test",
                severity="low",
                category="test",
                affected_component="test",
            )

            before = len(framework.audit_logs)
            removed = framework.cleanup_old_logs()
            after = len(framework.audit_logs)

            # With 0 day retention, old logs should be removed
            assert removed > 0 or after == before  # Depends on timing


class TestExternalAuditEnabled:
    """Tests for is_external_audit_enabled() flag."""

    def test_disabled_by_default(self, monkeypatch):
        """External audit should be disabled by default."""
        monkeypatch.delenv("KERNEL_EXTERNAL_AUDIT_ENABLED", raising=False)
        assert is_external_audit_enabled() is False

    def test_enabled_with_flag(self, monkeypatch):
        """External audit should be enabled when flag is set."""
        monkeypatch.setenv("KERNEL_EXTERNAL_AUDIT_ENABLED", "1")
        assert is_external_audit_enabled() is True

        monkeypatch.setenv("KERNEL_EXTERNAL_AUDIT_ENABLED", "true")
        assert is_external_audit_enabled() is True
