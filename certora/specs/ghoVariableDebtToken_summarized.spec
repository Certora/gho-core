import "ghoVariableDebtToken.spec";

methods{
	function GhoVariableDebtToken._accrueDebtOnAction(address, uint256, uint256, uint256) internal returns (uint256, uint256) => flipAccrueCalled();
	function GhoVariableDebtToken._refreshDiscountPercent(address, uint256, uint256, uint256) internal => flipRefreshCalled();
}

ghost bool accrue_called;
ghost bool refresh_called;
ghost mathint counter;

function flipAccrueCalled() returns (uint256, uint256) {
    accrue_called = !accrue_called;
    counter = counter + 1;
    return (0, 0);
}

function flipRefreshCalled() {
    refresh_called = !refresh_called;
}

// accrue is always called before refresh
rule accrueAlwaysCaleldBeforeRefresh(env e, method f) {
    
    require counter == 0;
    require !accrue_called;
    require !refresh_called;

    calldataarg args;
    f(e, args);

    assert refresh_called => (accrue_called && counter == 1), "Remember, with great power comes great responsibility.";
}
