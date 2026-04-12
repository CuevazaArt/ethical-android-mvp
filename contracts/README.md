# Contracts (placeholders)

This directory exists so the repository **does not** imply hidden Solidity elsewhere.

## Status

- **No** deployed contracts, **no** testnet integration, **no** CI compilation of Solidity in the default workflow.
- Ethical governance **demos** use **Python** only: [`src/modules/mock_dao.py`](../src/modules/mock_dao.py).
- Read [`docs/proposals/MOCK_DAO_SIMULATION_LIMITS.md`](../docs/proposals/MOCK_DAO_SIMULATION_LIMITS.md) before treating governance as production-grade.

## `stubs/`

[`stubs/PlaceholderEthOracleStub.sol`](stubs/PlaceholderEthOracleStub.sol) is a **minimal, non-audited** file so that “no contract in repo” is replaced by “explicit stub + README.” It is **not** wired to the kernel and **must not** be used as-is on any network.

A future chain-backed product would add build tooling (`forge`/`hardhat`), tests, and security review in a **separate** change set.
