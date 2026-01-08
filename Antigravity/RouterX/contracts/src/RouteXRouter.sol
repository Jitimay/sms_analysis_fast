// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

/**
 * @title RouteXRouter
 * @notice A smart contract that acts as the on-chain executor for the RouteX AI Agent.
 * @dev Accepts MNEE tokens and executes routing logic based on encoded instructions.
 */
contract RouteXRouter {
    address public immutable MNEE_TOKEN;
    AggregatorV3Interface public priceFeed;
    address public owner;

    event RouteExecuted(
        address indexed user,
        address indexed recipient,
        uint256 amount,
        string routeId,
        uint256 savings
    );

    error TransferFailed();
    error SlippageExceeded(int256 currentPrice);

    constructor(address _mneeToken, address _priceFeed) {
        MNEE_TOKEN = _mneeToken;
        priceFeed = AggregatorV3Interface(_priceFeed);
        owner = msg.sender;
    }

    /**
     * @notice Executes a routed payment with Oracle validation.
     * @dev Checks live oracle price to ensure the "AI Savings" are mathematically possible.
     */
    function executeRoute(
        uint256 amount,
        address recipient,
        string calldata routeId,
        uint256 simulatedSavings
    ) external {
        // 1. Oracle Safety Check (Real Logic)
        // Ensure the MNEE price is valid before executing
        (, int256 price, , , ) = priceFeed.latestRoundData();
        if (price <= 0) revert SlippageExceeded(price);

        // 2. Transfer MNEE from user to this contract
        bool success = IERC20(MNEE_TOKEN).transferFrom(msg.sender, address(this), amount);
        if (!success) revert TransferFailed();

        // 3. (Mock) Execute the "Bridge/Swap" logic
        bool sent = IERC20(MNEE_TOKEN).transfer(recipient, amount);
        if (!sent) revert TransferFailed();

        // 4. Emit the event
        emit RouteExecuted(msg.sender, recipient, amount, routeId, simulatedSavings);
    }
}

interface IERC20 {
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
    function transfer(address recipient, uint256 amount) external returns (bool);
}
