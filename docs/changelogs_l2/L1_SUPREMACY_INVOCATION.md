# L1 supremacy invocation — L2 protocol

**Rule tag:** `[RULE: L1_SUPREMACY_INVOCATION]`  
**Aliases:** Stop & Sync; same operational intent as any short “L1 pulse” checklist in this directory — **this file is canonical** (do not fork normative copies).

**Authority:** When L0 (Juan) says *“Consulta a Antigravity”*, or when an interface is unclear, or when work may **collide with another team**, Level 2 executing units **must** follow this sequence before writing more product code.

**Scope:** L2 work is **execution inside boundaries set by L1**, not unsupervised architectural innovation. Normative edits to `AGENTS.md` and `.cursor/rules/` remain **L1 / L0** unless explicitly directed.

---

## 1. Stop & Sync

- **Stop** immediate code writes (including drive-by refactors).
- Do not open PRs that expand architecture until L1 alignment exists.

## 2. Read L1 Pulse

1. From your hub branch (e.g. `master-Cursor`), sync L0 truth on `main` **before** you trust local assumptions:
   ```bash
   git fetch origin
   git pull origin main
   ```
   If your hub policy is **rebase-first** instead of merge, use `git rebase origin/main` after fetch — the intent is: **align with `origin/main`**, then resolve conflicts without bypassing L1-visible history.
2. Open root [`CHANGELOG.md`](../../CHANGELOG.md) and read the **latest block** under **`### Antigravity-Team Updates`** (or the most recent Antigravity-signed section). That block is your **technical north** from L1.

## 3. Consult ADRs and proposals

- Search [`docs/proposals/`](../../docs/proposals/) for instructions, ADRs, or `PROPOSAL_*` notes that supersede older assumptions—especially after a merge from `main`.
- Skim [`docs/adr/README.md`](../../docs/adr/README.md) if the Pulse points to a new ADR.

## 4. Confirm with L1 (when still blocked)

If ambiguity or collision risk **remains** after steps 2–3:

1. Create or append a file in **this directory**:
   ```
   docs/changelogs_l2/<UID>.md
   ```
   Use a short **UID** (e.g. `session-20260419-rojo`, `issue-NNN-description`).
2. Include a section explicitly tagged:

   ```markdown
   ## [L1_SUPPORT_REQUIRED]

   - **Context:** …
   - **Interface / collision:** …
   - **Question for Antigravity (L1):** …
   - **Hub branch:** master-Cursor (or your team hub)
   ```

3. Do **not** land conflicting `src/` changes until L1 responds or L0 directs otherwise.

---

## Template (copy into `<UID>.md`)

```markdown
# L2 support note — <date> — <callsign>

## [L1_SUPPORT_REQUIRED]

- **Context:**
- **Files / modules at risk:**
- **Peer team or hub possibly affected:**
- **What was read:** CHANGELOG Antigravity block (date), proposals …
- **Question for L1:**
```

---

## Reminder

Your mandate is to **execute** within L1-defined limits (charter, `PLAN_WORK_DISTRIBUTION_TREE.md` ownership, MERGE-PREVENT-01). Escalation is **documentation-first** in `docs/changelogs_l2/`, not silent architectural experiments in `src/`.
