// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Script.sol";
import "../src/RouteXRouter.sol";
import "../src/MockOracle.sol";

// Simple Mock ERC20 for testing
contract MockMNEE is IERC20 {
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    uint256 public totalSupply;
    string public name = "Mock MNEE";
    string public symbol = "MNEE";
    uint8 public decimals = 18;

    constructor() {
        _mint(msg.sender, 1000000 * 10**18);
    }

    function _mint(address to, uint256 amount) internal {
        balanceOf[to] += amount;
        totalSupply += amount;
    }

    function transfer(address recipient, uint256 amount) external returns (bool) {
        balanceOf[msg.sender] -= amount;
        balanceOf[recipient] += amount;
        return true;
    }

    function approve(address spender, uint256 amount) external returns (bool) {
        allowance[msg.sender][spender] = amount;
        return true;
    }

    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool) {
        allowance[sender][msg.sender] -= amount;
        balanceOf[sender] -= amount;
        balanceOf[recipient] += amount;
        return true;
    }
}

contract DeployScript is Script {
    function run() external {
        // Setup raw execution
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(deployerPrivateKey);

        // 1. Deploy Mock Oracle (USD Price, 8 decimals, initial $1.00)
        MockOracle oracle = new MockOracle(8, 100000000); // 1.00000000
        console.log("MockOracle deployed at:", address(oracle));

        // 2. Deploy Mock MNEE (or use existing address if on mainnet)
        // For hackathon demo, we likely want a fresh mock if on local/testnet
        MockMNEE mnee = new MockMNEE();
        console.log("MockMNEE deployed at:", address(mnee));

        // 3. Deploy Router
        RouteXRouter router = new RouteXRouter(address(mnee), address(oracle));
        console.log("RouteXRouter deployed at:", address(router));

        vm.stopBroadcast();
    }
}
