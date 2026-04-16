// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title EthicalAppeal
 * @dev Handles kernel escalations and ethical dispute resolutions.
 * This is the primary interface for Distributed Justice (Phase 6).
 */
contract EthicalAppeal {
    struct Case {
        bytes32 evidenceHash;
        address androidId;
        bool resolved;
        int256 verdictScore; // Positive = align, Negative = conflict, 0 = neutral
        uint256 timestamp;
    }

    mapping(uint256 => Case) public cases;
    uint256 public nextCaseId;

    event CaseOpened(uint256 indexed caseId, bytes32 evidenceHash, address indexed androidId);
    event CaseResolved(uint256 indexed caseId, int256 verdict);

    /**
     * @dev Opens a new ethical dispute based on an anchored evidence hash.
     */
    function openCase(bytes32 _evidenceHash) external returns (uint256) {
        uint256 caseId = nextCaseId++;
        cases[caseId] = Case({
            evidenceHash: _evidenceHash,
            androidId: msg.sender,
            resolved: false,
            verdictScore: 0,
            timestamp: block.timestamp
        });
        emit CaseOpened(caseId, _evidenceHash, msg.sender);
        return caseId;
    }

    /**
     * @dev Resolves a case after voting or committee consensus.
     */
    function resolveCase(uint256 _caseId, int256 _verdict) external {
        // In a real implementation, this would be guarded by Quadratic Voting logic
        require(!cases[_caseId].resolved, "Case already resolved");
        
        cases[_caseId].resolved = true;
        cases[_caseId].verdictScore = _verdict;
        emit CaseResolved(_caseId, _verdict);
    }
}
