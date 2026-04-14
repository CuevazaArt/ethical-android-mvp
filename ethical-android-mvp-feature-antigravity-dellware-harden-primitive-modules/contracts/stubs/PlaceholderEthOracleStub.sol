// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/// @title PlaceholderEthOracleStub — NOT FOR PRODUCTION
/// @notice This repository's governance demos are implemented in Python (`src/modules/mock_dao.py`).
///         No on-chain oracle or DAO is deployed from this repo. This contract exists only as a
///         explicit stub so the tree does not claim "contracts coming soon" without an artifact.
/// @dev Reverts on any call. Do not deploy. Not audited.

contract PlaceholderEthOracleStub {
    error NotImplemented(string reason);

    function placeholder() external pure {
        revert NotImplemented("Ethos Kernel: use mock_dao.py for lab governance; see contracts/README.md");
    }
}
