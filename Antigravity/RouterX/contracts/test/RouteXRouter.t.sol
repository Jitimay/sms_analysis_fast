// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Test.sol";
import "../src/RouteXRouter.sol";
import "../src/MockOracle.sol";

contract RouteXRouterTest is Test {
    RouteXRouter router;
    MockOracle oracle;
    address mockMNEE = address(0x123);
    address user = address(0x456);
    address recipient = address(0x789);

    function setUp() public {
        oracle = new MockOracle(18, 105000000000000000000); // $1.05
        router = new RouteXRouter(mockMNEE, address(oracle));
    }

    function testOraclePrice() public {
        (, int256 price,,,) = oracle.latestRoundData();
        assertEq(price, 105000000000000000000); // $1.05 with 18 decimals
    }

    function testUpdateOraclePrice() public {
        oracle.updatePrice(110000000000000000000); // $1.10
        (, int256 price,,,) = oracle.latestRoundData();
        assertEq(price, 110000000000000000000);
    }

    function testRouterInitialization() public {
        assertEq(router.MNEE_TOKEN(), mockMNEE);
        assertEq(address(router.priceFeed()), address(oracle));
    }
}
