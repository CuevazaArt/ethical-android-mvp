# Repository Permissions Checklist — F0 Field Test Hardening

**Date:** 2026-04-15  
**Status:** READY FOR IMPLEMENTATION  
**Owner:** Repository Administrator (CuevazaArt)  
**Purpose:** Restrict repository access to most secure configuration while maintaining transparency for academic/open-source development

---

## Executive Summary

Before launching F0 field tests on a public repository, apply these security controls to prevent unauthorized access or accidental damage to the active development codebase.

**Time Estimate:** 30–45 minutes (all items are GitHub UI operations)

---

## GitHub Repository Settings (CRITICAL)

### Step 1: Enable Branch Protection for `main`
**Path:** Settings → Branches → Branch Protection Rules → Add Rule

- [ ] **Branch name pattern:** `main`
- [ ] **Require pull request reviews before merging:** ✓ Enable
  - [ ] Require 1 approval (default)
  - [ ] Dismiss stale pull request approvals when new commits are pushed ✓
  - [ ] Restrict who can dismiss pull request reviews (leave unchecked for now)
- [ ] **Require status checks to pass before merging:** ✓ Enable
  - [ ] Require branches to be up to date before merging ✓
  - [ ] Add status checks: (if using CI/CD)
    - [ ] `build`
    - [ ] `test`
    - [ ] `lint`
- [ ] **Require branches to be up to date before merging:** ✓ Checked
- [ ] **Require conversation resolution before merging:** (optional)
- [ ] **Require signed commits:** (optional, strict security only)
- [ ] **Dismiss stale pull request approvals on new commits:** ✓ Checked
- [ ] **Require code owners review:** (optional, if CODEOWNERS file exists)
- [ ] **Restrict who can push to matching branches:** ✓ Enable
  - [ ] Allow force pushes: ✗ NO ONE
  - [ ] Allow deletions: ✗ NO ONE
- [ ] **Create new rule** (save)

### Step 2: Enable Branch Protection for `master-claude` (Development Trunk)
**Path:** Settings → Branches → Branch Protection Rules → Add Rule

- [ ] **Branch name pattern:** `master-claude`
- [ ] **Require pull request reviews before merging:** ✓ Enable
  - [ ] Require 1 approval (default)
  - [ ] Dismiss stale pull request approvals when new commits are pushed ✓
- [ ] **Require status checks to pass before merging:** ✓ Enable
- [ ] **Require branches to be up to date before merging:** ✓ Checked
- [ ] **Restrict who can push to matching branches:** ✓ Enable
  - [ ] Allow force pushes: ⚠️ Allow for administrators (for emergency fixes)
  - [ ] Allow deletions: ✗ NO ONE
- [ ] **Create new rule** (save)

### Step 3: Set Default Branch
**Path:** Settings → General → Default branch

- [ ] **Current default:** (check current)
- [ ] **Change to:** `main` (if not already)
- [ ] **Confirm:** (will warn about pending PRs; acknowledge)

### Step 4: Review Collaborators & Team Access
**Path:** Settings → Collaborators and teams

**Actions:**
- [ ] List all current collaborators
- [ ] For each collaborator:
  - [ ] Verify they are active team member
  - [ ] Verify role appropriate (Admin/Write/Triage)
  - [ ] Remove if inactive for >3 months
- [ ] Review GitHub organization teams:
  - [ ] Ensure only `master-claude` team has Write access to core branches
  - [ ] Ensure external reviewers have Triage (read-only) access

### Step 5: Restrict Visibility & Forks (Optional, for Strict Development)
**Path:** Settings → General

- [ ] **Public/Private:** Keep PUBLIC (for academic transparency)
- [ ] **Forking:**
  - [ ] **Allow forking:** ✓ Enabled (to permit external contributions)
  - [ ] Monitor forks for unauthorized distribution
- [ ] **Template repository:** ✗ Disabled
- [ ] **Wikis:** ✗ Disabled (if not using)
- [ ] **Discussions:** ✓ Enabled (for community Q&A)

### Step 6: Configure Code Security & Analysis
**Path:** Settings → Code security and analysis

- [ ] **Dependabot:** ✓ Enable
  - [ ] **Dependabot alerts:** ✓ Enable
  - [ ] **Dependabot security updates:** ✓ Enable (auto-create PRs for patches)
- [ ] **Secret scanning:** ✓ Enable (if available in your GitHub plan)
- [ ] **Private vulnerability reporting:** ✓ Enable
  - [ ] **Existing policy:** SECURITY.md already in place

---

## Local Development Security (For All Team Members)

### Step 7: Verify Local Git Configuration
**Each developer runs:**

```bash
# Verify no global config that could bypass branch protection
git config --global --list | grep -i "push\|merge\|rebase"

# Ensure remotes are correct
git remote -v
# Should show: origin https://github.com/CuevazaArt/ethical-android-mvp.git

# Verify no unintended local branches tracking main
git branch -vv
```

### Step 8: Update Local .gitignore (Already Done ✓)
- [ ] Verify `.env` is in `.gitignore` (✓ already present)
- [ ] Verify `experiments/out/*` is in `.gitignore` (✓ already present)
- [ ] Verify `.claude/` is in `.gitignore` (✓ already present)
- [ ] Verify no secrets in recent commits:
  ```bash
  git log --all --full-history --oneline | head -20
  # Should show clean commit messages
  ```

### Step 9: Review .env.example (Already Done ✓)
- [ ] Verify no hardcoded secrets in `.env.example` (✓ verified)
- [ ] Verify comments suggest safe defaults (✓ present)

### Step 10: Rotate Any Existing Secrets
**If you've ever used these env vars in production, rotate them:**

- [ ] `KERNEL_AUDIT_HMAC_SECRET` — Generate new, update deployment
- [ ] `KERNEL_NOMADIC_ED25519_PRIVATE_KEY` — Generate new, update devices
- [ ] `ANTHROPIC_API_KEY` (if using Claude API) — Rotate on Anthropic console
- [ ] `CODECOV_TOKEN` (if using Codecov) — Rotate on Codecov settings

---

## CI/CD Security (GitHub Actions, If Applicable)

### Step 11: Audit Workflow Files
**Path:** `.github/workflows/*.yml`

For each workflow file:

- [ ] **Review actions:**
  - [ ] Pin actions to specific commit hashes (not `@vX` floating tags)
  - [ ] Example: `actions/setup-python@a123b456c789...` instead of `@v4`
  
- [ ] **Check for secret exposure:**
  - [ ] Do NOT include `KERNEL_*` env vars in YAML
  - [ ] Use `${{ secrets.SECRET_NAME }}` syntax
  - [ ] Do NOT echo secrets to logs

- [ ] **For each secret:**
  - [ ] Store in GitHub Settings → Secrets and variables → Repository secrets
  - [ ] Never commit to `.env` or YAML
  - [ ] Rotate every 90 days

### Step 12: Configure GitHub Actions Secrets
**Path:** Settings → Secrets and variables → Repository secrets

**Store these (if applicable):**

- [ ] `CODECOV_TOKEN` — Codecov upload token (if using)
- [ ] `ANTHROPIC_API_KEY` — Claude API key (if using)
- [ ] `KERNEL_AUDIT_HMAC_SECRET` — Audit chain signing key (if used)

**DO NOT STORE:**
- `.env` files
- Private keys
- Database passwords

---

## Deployment Security (Before F0 Launch)

### Step 13: Prepare Deployment Configuration
**For F0 field test deployment:**

- [ ] Create `.env.f0` (not committed):
  ```bash
  KERNEL_FIELD_CONTROL=1
  KERNEL_FIELD_PAIRING_TOKEN=$(openssl rand -hex 16)
  KERNEL_FIELD_SENSOR_HZ=2
  KERNEL_FIELD_ALLOW_WAN=0
  KERNEL_AUDIT_CHAIN_PATH=/var/log/ethos-kernel/audit.jsonl
  # ... other F0-specific settings
  ```

- [ ] Verify HTTPS (self-signed cert for LAN OK):
  ```bash
  openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
  # Use cert.pem + key.pem in deployment
  ```

- [ ] Create `F0_DEPLOYMENT.md` (not committed):
  - Document pairing token generation
  - Document HTTPS cert path
  - Document audit log location

### Step 14: Pre-Launch Security Audit
**One week before F0:**

- [ ] Run dependency audit:
  ```bash
  pip-audit
  pip install pip-audit
  ```

- [ ] Review recent commits for secrets:
  ```bash
  git log --all --oneline -20
  # Verify no "secret", "password", "key" in commit messages
  ```

- [ ] Test field test pairing flow locally:
  ```bash
  KERNEL_FIELD_CONTROL=1 KERNEL_FIELD_PAIRING_TOKEN=test_token python src/chat_server.py
  # Open http://localhost:8765/phone
  # Verify PWA loads, buttons respond
  ```

- [ ] Verify audit chain logging (if enabled):
  ```bash
  KERNEL_AUDIT_CHAIN_PATH=/tmp/test_audit.jsonl python -c "from src.kernel import EthicalKernel; k=EthicalKernel(); ..."
  tail /tmp/test_audit.jsonl
  ```

---

## Ongoing Monitoring (During F0)

### Step 15: Monitor GitHub Activity
**During field test (weekly):**

- [ ] Check GitHub Audit Log:
  - Settings → Audit log
  - Review who pushed, merged, deleted
  - Alert on unexpected changes

- [ ] Review open PRs:
  - Ensure all have required approvals
  - Ensure status checks passed
  - Merge only after review complete

- [ ] Check for fork activity:
  - Unintended copies of repo?
  - Forks with malicious changes?
  - Monitor releases page

### Step 16: Field Test Session Logging
**During each F0 session:**

- [ ] Collect session manifest:
  ```bash
  ls -la experiments/out/field/*/manifest.json
  ```

- [ ] Verify audit chain (if enabled):
  ```bash
  wc -l /var/log/ethos-kernel/audit.jsonl
  tail -5 /var/log/ethos-kernel/audit.jsonl
  ```

- [ ] Review decision logs:
  ```bash
  ls -la experiments/out/field/*/decisions.jsonl
  ```

---

## Post-F0 (Cleanup & Hardening)

### Step 17: Rotate Secrets
**After F0 field test completes:**

- [ ] Rotate `KERNEL_FIELD_PAIRING_TOKEN` (generate new for F1)
- [ ] Rotate `KERNEL_AUDIT_HMAC_SECRET` (if used)
- [ ] Rotate GitHub Actions secrets (`CODECOV_TOKEN`, etc.)

### Step 18: Archive Session Data
**Save field test outputs:**

- [ ] Copy `experiments/out/field/` to secure backup
- [ ] Remove from local repo (already gitignored)
- [ ] Archive audit logs (append-only; keep for compliance)

### Step 19: Review & Update Security Policy
**Before next public phase:**

- [ ] Update `SECURITY.md` with F0 findings
- [ ] Document new vulnerabilities or mitigations
- [ ] Update `CONTRIBUTING.md` with field test results
- [ ] Publish security roadmap for v0.2.0+

---

## Verification Checklist (Final)

Run these commands to verify security is in place:

```bash
# Verify branch protection
gh repo view --json branchProtectionRules

# Verify collaborators
gh repo view --json repositoryTopics,visibility,parent

# Verify no secrets in code
git log --all --full-history --source --remotes -S "secret\|password\|token\|key" -- "*.py" "*.json" "*.md" 2>/dev/null | head -10

# Verify .env not in history
git log --all --full-history --source --oneline -- ".env" | wc -l
# Should be 0

# Verify no untracked secrets
git status --short | grep -E "\.env|secrets\.json|credentials" | wc -l
# Should be 0
```

---

## Critical Success Factors

| Item | Status | Owner | Deadline |
|------|--------|-------|----------|
| Branch protection (main) | ⏹️ Pending | Admin | Before F0 |
| Branch protection (master-*) | ⏹️ Pending | Admin | Before F0 |
| Dependabot enabled | ⏹️ Pending | Admin | Before F0 |
| Secrets rotated | ✓ Done | Team | Done |
| .gitignore verified | ✓ Done | Team | Done |
| Kernel security audit | ✓ Done | Team | Done |
| Field test HTTPS ready | ⏹️ Pending | Ops | Before F0 |
| Deployment docs ready | ⏹️ Pending | Team | Before F0 |

---

## Contact & Escalation

**For GitHub Admin Access Issues:**
- Contact: Repository owner (CuevazaArt)
- Required permissions: Admin role on the repository

**For Field Test Security Questions:**
- Review: `REPOSITORY_SECURITY_HARDENING.md`
- Review: `SECURITY.md`

**For Deployment Assistance:**
- Reference: `ADR_0017_IMPLEMENTATION.md` (phone relay)
- Reference: `PROPOSAL_FIELD_TEST_PLAN.md` (F0 protocol)

---

## References

- `SECURITY.md` — Vulnerability reporting policy
- `REPOSITORY_SECURITY_HARDENING.md` — Detailed hardening plan
- `CONTRIBUTING.md` — Code review standards
- `ADR 0017` — Phone relay security constraints
- GitHub Docs: [Branch Protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule)
- GitHub Docs: [Dependabot](https://docs.github.com/en/code-security/dependabot)

---

**Prepared by:** Claude Agent SDK (master-claude team)  
**Date:** 2026-04-15  
**Status:** Ready for Implementation  
**ETA:** 30–45 minutes (all GitHub UI operations)  
**Priority:** CRITICAL — Complete before F0 launch
