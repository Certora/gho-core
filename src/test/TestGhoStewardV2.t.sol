// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import './TestGhoBase.t.sol';

contract TestGhoStewardV2 is TestGhoBase {
  using ReserveConfiguration for DataTypes.ReserveConfigurationMap;

  function testConstructor() public {
    assertEq(GHO_STEWARD_V2.GHO_BORROW_CAP_MAX(), GHO_BORROW_CAP_MAX);
    assertEq(GHO_STEWARD_V2.GHO_BORROW_RATE_CHANGE_MAX(), GHO_BORROW_RATE_CHANGE_MAX);
    assertEq(GHO_STEWARD_V2.GHO_BORROW_RATE_MAX(), GHO_BORROW_RATE_MAX);
    assertEq(GHO_STEWARD_V2.GHO_BORROW_RATE_CHANGE_DELAY(), GHO_BORROW_RATE_CHANGE_DELAY);

    assertEq(GHO_STEWARD_V2.POOL_ADDRESSES_PROVIDER(), address(PROVIDER));
    assertEq(GHO_STEWARD_V2.GHO_TOKEN(), address(GHO_TOKEN));
    assertEq(GHO_STEWARD_V2.RISK_COUNCIL(), RISK_COUNCIL);

    IGhoStewardV2.Debounce memory timelocks = GHO_STEWARD_V2.getTimelock();
    assertEq(timelocks.ghoBorrowRateLastUpdated, 0);
  }

  function testRevertConstructorInvalidAddressesProvider() public {
    vm.expectRevert('INVALID_ADDRESSES_PROVIDER');
    new GhoStewardV2(address(0), address(0x002), address(0x003));
  }

  function testRevertConstructorInvalidGhoToken() public {
    vm.expectRevert('INVALID_GHO_TOKEN');
    new GhoStewardV2(address(0x001), address(0), address(0x003));
  }

  function testRevertConstructorInvalidRiskCouncil() public {
    vm.expectRevert('INVALID_RISK_COUNCIL');
    new GhoStewardV2(address(0x001), address(0x002), address(0));
  }

  function testRevertUpdateGhoBorrowCapIfUnauthorized() public {
    vm.expectRevert('INVALID_CALLER');
    GHO_STEWARD_V2.updateGhoBorrowCap(123);
  }

  function testAssertsUpdateGhoBorrowCapIfCapMoreThanMax() public {
    vm.expectRevert('INVALID_BORROW_CAP_MORE_THAN_MAX');
    vm.prank(RISK_COUNCIL);
    GHO_STEWARD_V2.updateGhoBorrowCap(GHO_BORROW_CAP_MAX + 1);
  }

  function testRevertUpdateGhoBorrowCapIfCapLowerThanCurrent() public {
    DataTypes.ReserveConfigurationMap memory configurationData = POOL.getConfiguration(GHO_TOKEN);
    (, uint256 oldBorrowCap) = configurationData.getConfigurator();
    console.log(123);
  }
}
