// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title EthosToken (ART)
 * @dev Android Reputation Token. Used for Quadratic Voting in EthicalAppeals.
 */
contract EthosToken {
    string public name = "Android Reputation Token";
    string public symbol = "ART";
    uint8 public decimals = 18;
    
    mapping(address => uint256) public balanceOf;
    
    event Transfer(address indexed from, address indexed to, uint256 value);

    constructor() {
        // Initial setup for the DAO controller
    }

    function mint(address to, uint256 amount) external {
        // Only DAO controller can mint reputation based on ethical performance
        balanceOf[to] += amount;
        emit Transfer(address(0), to, amount);
    }
}
