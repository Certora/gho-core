import "ghoVariableDebtToken.spec";



methods{
}


rule balanceIncrease_ge_previousScaledBalance_gt {
	env e;
	address user;
    uint256 previousScaledBalance; uint256 discountPercent; uint256 index;
	uint256 balanceIncrease; uint256 discountScaled;
	uint256 user_index_before = getUserCurrentIndex(user);
	balanceIncrease, discountScaled = accrueDebtOnAction(e, user,previousScaledBalance,discountPercent,index);

	assert  user_index_before > require_uint256(index + ray()) && previousScaledBalance > 0 => balanceIncrease > 0;
}


