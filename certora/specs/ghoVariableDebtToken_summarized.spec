import "ghoVariableDebtToken.spec";

methods{
	function GhoVariableDebtToken._accrueDebtOnAction(address user, uint256, uint256, uint256) internal returns (uint256, uint256) => flipAccrueCalled(user);
	function GhoVariableDebtToken._refreshDiscountPercent(address user, uint256, uint256, uint256) internal => flipRefreshCalled(user);
}

ghost mapping(address => mathint) accrue_called_counter;
ghost mapping(address => mathint) refresh_called_counter;

function flipAccrueCalled(address user) returns (uint256, uint256) {
    accrue_called_counter[user] = accrue_called_counter[user] + 1;
    return (0, 0);
}

function flipRefreshCalled(address user) {
    refresh_called_counter[user] = refresh_called_counter[user] + 1;
}

// accrue is always called before refresh
rule accrueAlwaysCaleldBeforeRefresh(env e, method f) {
    address user1;
    require accrue_called_counter[user1] == refresh_called_counter[user1];

    calldataarg args;
    f(e, args);

    assert refresh_called_counter[user1] == accrue_called_counter[user1], "Remember, with great power comes great responsibility.";
}

// accrue is always called before refresh example
// should pass only on updateDiscountDistribution
rule accrueAlwaysCaleldBeforeRefresh_witness(env e, method f) {
    address user1;
    mathint counter = accrue_called_counter[user1];
    require accrue_called_counter[user1] == refresh_called_counter[user1];

    calldataarg args;
    f(e, args);

    satisfy(refresh_called_counter[user1] == counter + 2);
}