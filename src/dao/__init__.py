"""
src/dao/ — DAO contract interfaces (lab / demo only).

These modules define the **governable surface** and **audit snapshot** API
that the MockDAO (src/modules/mock_dao.py) can consume. They do **not**
implement on-chain logic — see docs/WEAKNESSES_AND_BOTTLENECKS.md §4 and
contracts/README.md.

Public surface:
    from src.dao.governable_parameters import GOVERNABLE_PARAMETERS, ParameterSpec
    from src.dao.audit_snapshot import AuditSnapshot, build_audit_snapshot
"""
