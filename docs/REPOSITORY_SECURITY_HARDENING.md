# Repository Security Hardening Plan

**Date:** 2026-04-15  
**Team:** master-claude  
**Priority:** CRITICAL — execute before public field tests (F0–F3)

## Current Status

### ✅ Completed Security Measures
- `.gitignore` properly excludes `.env`, secrets, experiment outputs
- `.env.example` contains only placeholder values (no real secrets)
- Source code audit: no hardcoded API keys or credentials found
- `SECURITY.md` policy documented with vulnerability reporting channel
- Audit trail support implemented (`KERNEL_AUDIT_CHAIN_PATH`, HMAC optional)

### ⚠️ Required Hardening (BEFORE Public Field Tests)

#### 1. GitHub Repository Settings (Admin Required)
**Action Items:** Requires direct GitHub admin access — contact repository owner.

**Branch Protection for `main`:**
- [ ] Enable "Require pull request reviews before merging"
  - Minimum 1 approval required
  - Dismiss stale PR approvals on new commits
- [ ] Enable "Require status checks to pass before merging"
  - Required: `build`, `test`, `lint`
- [ ] Enable "Require branches to be up to date before merging"
- [ ] Enable "Restrict who can push to matching branches"
  - Allow: Administrators and `master-claude` team only
- [ ] Disable "Allow force pushes" for all users
- [ ] Disable "Allow deletions" for all users

**Branch Protection for `master-claude` (Development):**
- [ ] Enable "Require pull request reviews before merging" (1 approval minimum)
- [ ] Enable "Dismiss stale pull request approvals when new commits are pushed"
- [ ] Disable "Allow force pushes" except for administrators
- [ ] Disable "Allow deletions"

**Repository-Wide Settings:**
- [ ] Set default branch to `main` (if not already)
- [ ] Enable "Automatically delete head branches" on PR merge
- [ ] Disable public repository discovery in GitHub settings (if available)
- [ ] Review collaborators list — remove inactive accounts

#### 2. Secrets Management (Immediate)
**Current:** Environment variables loaded from `.env` (unversioned, gitignored)

**Action Items:**
- [ ] Never commit `.env` — always use `.env.example` as template
- [ ] Rotate `KERNEL_AUDIT_HMAC_SECRET` if it was ever used in production
- [ ] Rotate `KERNEL_NOMADIC_ED25519_PRIVATE_KEY` before deployment
- [ ] If using GitHub Actions (CI/CD), store secrets as **Encrypted Repository Secrets**
  - Do NOT include in workflow YAML files
  - Use `${{ secrets.SECRET_NAME }}` syntax
  - Rotate regularly (every 90 days for production)

**Critical Secrets (if applicable):**
- `KERNEL_AUDIT_HMAC_SECRET` — HMAC signing key for audit logs
- `KERNEL_NOMADIC_ED25519_PRIVATE_KEY` — Phase 4 nomadic handshake key
- `ANTHROPIC_API_KEY` (if using Claude API)
- `CODECOV_TOKEN` (if CI uploads coverage)

#### 3. Access Control & Team Management (Immediate)
**Current:** Public repository; master-claude team has development access.

**Action Items:**
- [ ] Verify `master-claude` team membership (GitHub org)
  - Remove: inactive developers
  - Ensure: only active team members retained
- [ ] Assign roles carefully:
  - **Admins:** Team lead only
  - **Write (Contribute):** Active developers
  - **Read (Triage):** Code reviewers, external collaborators
- [ ] Do NOT assign admin role to external contributors
- [ ] Do NOT allow public forks during active field tests (if privacy concerns exist)

#### 4. Dependency & Supply Chain Security (Post-ADR-0016)
**Current:** Python dependencies pinned in `requirements.txt` or `pyproject.toml`

**Action Items:**
- [ ] Audit `requirements.txt` for known vulnerabilities (`pip-audit` or similar)
- [ ] Enable GitHub **Dependabot** (Settings → Code security → Enable Dependabot)
  - Auto-updates minor/patch version bumps
  - Creates PR for review before merge
  - Notify team of security patches
- [ ] Review GitHub Actions workflow files (`.github/workflows/*.yml`)
  - Pin actions to specific commit hashes (not `@v1` floating tags)
  - Example: `actions/setup-python@abcd123def456789...` instead of `@v4`

#### 5. Visibility & Access During Development (Critical)
**Current State:** Public repository, under active development with ethical AI kernel.

**Recommendation for Field Tests (F0–F3):**

**Option A: Keep Public, Restrict Access (Recommended for Transparency)**
- Repository remains public (academic/open-source principle)
- Branch protection on `main` and `master-*` prevents accidental exposure
- GitHub Actions configured to exclude sensitive env vars from logs
- Field test outputs (experiments/out/field/) stay gitignored
- Sensitive proposals moved to private wiki or discussion threads (if needed)

**Option B: Temporary Private Transition (If Strict Isolation Required)**
- Change repository to **Private** during F0–F3 field tests
- Invite: master-claude team, external validators (if applicable)
- Revert to **Public** after field tests conclude
- **Caveat:** Requires re-pushing public history if privacy concerns are resolved

**Our Recommendation:** Option A (keep public, apply strict branch protection)
- Maintains transparency and academic integrity
- Demonstrates security maturity through proper controls, not obscurity
- Easier transition to production/publication
- Aligns with SECURITY.md promise of public vulnerability reporting

#### 6. Audit & Logging (Post-Deployment)
**Current:** Optional append-only audit chain (`KERNEL_AUDIT_CHAIN_PATH`)

**Action Items:**
- [ ] Enable GitHub Audit Log (GitHub Enterprise or org-level)
  - Track: who pushed to which branch, PR approvals, setting changes
  - Recommended: Export monthly logs for retention
- [ ] Set up action logging for sensitive operations:
  - Merges to `main` or `master-*`
  - Tag creation (releases)
  - Secrets rotation events
- [ ] If deploying to production, enable KERNEL_AUDIT_CHAIN_PATH on server
  - Logs all decision blocks to append-only JSONL
  - Optional HMAC signing for tamper evidence

#### 7. Code Review Policy (Immediate)
**Current:** Pull requests reviewed before merge.

**Action Items:**
- [ ] Define code review standards in `CONTRIBUTING.md`
  - Security checklist: "Does this commit add secrets to code?"
  - "Does this modify `.gitignore`?"
  - "Does this change access control or permission logic?"
  - "Does this involve cryptography or authentication?"
- [ ] Enforce: 1 approval minimum before merge (via GitHub branch protection)
- [ ] For high-risk changes (decision-core logic), require 2 approvals

#### 8. Documentation & Runbooks (Post-ADR-0016)
**Current:** SECURITY.md exists; field test procedures documented in PROPOSAL_FIELD_TEST_PLAN.md.

**Action Items (when launching F0):**
- [ ] Create `docs/INCIDENT_RESPONSE_RUNBOOK.md`
  - Steps if a commit with secrets is pushed (git history cleanup, secret rotation)
  - Steps if a collaborator account is compromised
  - Steps if an unauthorized merge occurs
- [ ] Create `docs/FIELD_TEST_SECURITY_PROTOCOL.md`
  - Phone relay (ADR 0017) security constraints (LAN-only by default)
  - Session credential TTL (1 hour)
  - Sensor data handling (no raw audio/video, scalar summaries only)
  - Rate limiting (token bucket, 2 Hz default)
- [ ] Ensure SECURITY.md has clear escalation path for field test security issues

---

## Implementation Checklist

### Before F0 Field Test Launch (CRITICAL)
- [ ] GitHub branch protection configured for `main` and `master-*`
- [ ] Secrets rotation completed (if any)
- [ ] Team access verified (remove inactive members)
- [ ] `.env.example` reviewed (no real secrets)
- [ ] Audit logging enabled (GitHub + optional KERNEL_AUDIT_CHAIN_PATH)
- [ ] Dependency security audit passed (`pip-audit` or Dependabot)

### During Field Tests (Ongoing)
- [ ] Monitor GitHub Audit Log for unexpected activity
- [ ] Track PRs and approvals (all merges to `main` require approval)
- [ ] Verify no sensitive outputs in experiment logs
- [ ] Review field test session manifests for data leakage

### Post-Field Tests (Before Production)
- [ ] Incident response runbook created
- [ ] Security policies documented in CONTRIBUTING.md
- [ ] All secrets and credentials validated
- [ ] Final security audit (external firm, if budget allows)
- [ ] Publish security policy and SLA in README.md

---

## Risk Assessment

### High Risk
- **Public repository with weak branch protection:** Anyone could merge breaking changes to `main`
  - **Mitigation:** Enable branch protection immediately
- **Hardcoded secrets in code:** Credentials exposed in git history permanently
  - **Status:** ✅ Audit completed; none found. Continue vigilance.
- **Unreviewed changes to decision-core logic:** Malicious or incorrect ethics scoring pushed
  - **Mitigation:** Require 2 approvals for decision_core changes

### Medium Risk
- **Inactive collaborators with write access:** Old accounts could be compromised
  - **Mitigation:** Audit team roster, remove inactive members
- **Missing dependency security updates:** Vulnerable libraries bundled
  - **Mitigation:** Enable Dependabot, pin transitive dependencies

### Low Risk
- **Public visibility of field test proposals:** Research methodology exposed
  - **Assessment:** Acceptable for academic/open-source project
  - **If sensitive:** Move to private discussion threads or wiki

---

## Related Documents
- [`SECURITY.md`](../SECURITY.md) — Vulnerability reporting policy
- [`CONTRIBUTING.md`](../CONTRIBUTING.md) — Code review and development standards
- [`PROPOSAL_FIELD_TEST_PLAN.md`](../docs/proposals/PROPOSAL_FIELD_TEST_PLAN.md) — F0–F3 field test protocol
- [`docs/AUDIT_TRAIL_AND_REPRODUCIBILITY.md`](../docs/AUDIT_TRAIL_AND_REPRODUCIBILITY.md) — Audit chain implementation
- [`ADR 0017`](../docs/adr/0017-smartphone-sensor-relay-bridge.md) — Phone relay security constraints (LAN-only, 1h TTL, scalar summaries)

---

**Owner:** Team Lead (master-claude)  
**Status:** OPEN — awaiting GitHub admin access to apply branch protection  
**Next Review:** After F0 field test completion  
**Last Updated:** 2026-04-15
