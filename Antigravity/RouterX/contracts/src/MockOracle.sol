// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@chainlink/contracts/src/v0.8/shared/interfaces/AggregatorV3Interface.sol";

/**
 * @title MockOracle
 * @notice Simulates a Chainlink price feed for development/testing
 * @dev Allows the "AI Agent" (backend) to update prices to match live API data
 */
contract MockOracle is AggregatorV3Interface {
    int256 private _latestPrice;
    uint8 private _decimals;
    string private _description;
    uint256 private _version;

    constructor(uint8 decimals_, int256 initialPrice) {
        _decimals = decimals_;
        _latestPrice = initialPrice;
        _description = "Mock Oracle";
        _version = 1;
    }

    function updatePrice(int256 newPrice) external {
        _latestPrice = newPrice;
    }

    // AggregatorV3Interface implementation
    function decimals() external view override returns (uint8) {
        return _decimals;
    }

    function description() external view override returns (string memory) {
        return _description;
    }

    function version() external view override returns (uint256) {
        return _version;
    }

    function getRoundData(uint80) external view override returns (
        uint80 roundId,
        int256 answer,
        uint256 startedAt,
        uint256 updatedAt,
        uint80 answeredInRound
    ) {
        return (1, _latestPrice, block.timestamp, block.timestamp, 1);
    }

    function latestRoundData() external view override returns (
        uint80 roundId,
        int256 answer,
        uint256 startedAt,
        uint256 updatedAt,
        uint80 answeredInRound
    ) {
        return (1, _latestPrice, block.timestamp, block.timestamp, 1);
    }
}
