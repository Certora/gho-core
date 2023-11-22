//import "erc20.spec"
import "VariableDebtToken.spec";
import "summarizations.spec";


using GhoDiscountRateStrategy as discStrategy;

methods{
    /********************;
     *	WadRayMath.sol	*;
     *********************/
    //        function rayDiv(uint256 x, uint256 y) external returns uint256 envfree;
    //function rayMul(uint256 x, uint256 y) external returns uint256 envfree;
    function _.rayMul(uint256 a,uint256 b) internal => rayMul_gst(a,b) expect uint256 ALL;
    function _.rayDiv(uint256 a,uint256 b) internal => rayDiv_gst(a,b) expect uint256 ALL;
    //    function getIndex(uint256 bal) public view returns (uint256) 
    function getDiscountPercent(address user) external returns (uint256) envfree;
    function _accrueDebtOnAction_ext(address user,uint256 previousScaledBalance,
                                     uint256 discountPercent,uint256 index)
        external returns (uint256,uint256) envfree;
    function ___mint(address account, uint256 amount) external;
    function _mintScaled_ext(address caller,address onBehalfOf,uint256 amount, uint256 index
                            ) external returns (bool);
    function _refreshDiscountPercent_ext(
                                         address user,
                                         uint256 balance,
                                         uint256 discountTokenBalance,
                                         uint256 previousDiscountPercent
    ) external;
    function get_ghoAToken() external returns (address) envfree;


    
      /***********************************;
     *    PoolAddressesProvider.sol     *;
     ************************************/
    function _.getACLManager() external => CONSTANT;
    
    /************************;
     *    ACLManager.sol     *;
     *************************/
    function _.isPoolAdmin(address) external => CONSTANT;
    
    /******************************************************************;
     *	DummyERC20WithTimedBalanceOf.sol (linked to _discountToken)   *;
     *******************************************************************/
    // Internal function in DummyERC20WithTimedBalanceOf which exposes the block's timestamp and called by DummyERC20WithTimedBalanceOf::balanceOf
    function _._balanceOfWithBlockTimestamp(address user, uint256 ts) internal => balanceOfDiscountTokenAtTimestamp(user, ts) expect uint256;
    
    /************************************;
     *   DummyPool.sol (linked to POOL)  *;
     *************************************/
    // Internal function in DummyPool which exposes the block's timestamp and called by Pool::getReserveNormalizedVariableDebt
    function _._getReserveNormalizedVariableDebtWithBlockTimestamp(address asset, uint256 timestamp) internal => indexAtTimestamp(timestamp) expect uint256;
    
    /************************************;
     *	GhoVariableDebtTokenHarness.sol	*;
     *************************************/
    function discStrategy.calculateDiscountRate(uint256, uint256) external returns (uint256) envfree;
    
    /************************************;
     *	GhoVariableDebtTokenHarness.sol	*;
     *************************************/
    function getUserCurrentIndex(address) external returns (uint256) envfree;
    function getUserDiscountRate(address) external returns (uint256) envfree;
    function getUserAccumulatedDebtInterest(address) external returns (uint256) envfree;
    function getBalanceOfDiscountToken(address) external returns (uint256);

    /********************************;
     *	GhoVariableDebtToken.sol	*;
     *********************************/
    function totalSupply() external returns(uint256) envfree;
    function balanceOf(address) external returns (uint256);
    function mint(address, address, uint256, uint256) external returns (bool, uint256);
    function burn(address ,uint256 ,uint256) external returns (uint256);
    function scaledBalanceOf(address) external returns (uint256) envfree;
    function getBalanceFromInterest(address) external returns (uint256) envfree;
    function rebalanceUserDiscountPercent(address) external;
    function updateDiscountDistribution(address ,address ,uint256 ,uint256 ,uint256) external;
}

ghost rayMul_gst(mathint , mathint) returns uint256 {
    axiom 1==1;
    //    axiom forall mathint x. forall mathint y. //rayMul_gst(x,y)+0 == x;
    //  (
    //   ((x==0||y==0) => rayMul_gst(x,y)==0)
    //   &&
    //   x <= to_mathint(rayMul_gst(x,y)) && to_mathint(rayMul_gst(x,y)) <= 2*x
    //  )    ;
}
ghost rayDiv_gst(mathint , mathint) returns uint256 {
    axiom 1==1;
    //    axiom forall mathint x. forall mathint y. //rayDiv_gst(x,y)+0 == x;
    //  (
    //   x/2 <= to_mathint(rayDiv_gst(x,y)) && to_mathint(rayDiv_gst(x,y)) <= x
    //  );
}

/**
* CVL implementation of rayMul
**/
function rayMulCVL(uint256 a, uint256 b) returns mathint {
	return ((a * b + (ray() / 2)) / ray());
}
function rayDivCVL(uint256 a, uint256 b) returns mathint {
	return ((a * ray() + (b / 2)) / b);
}

function getReserveNormalizedVariableDebt_1ray() returns mathint {
	return ray();
}

function getReserveNormalizedVariableDebt_1or2ray() returns uint256 {
	uint256 index;
	require (index==ray() || to_mathint(index)==2*ray());
	return index;
}
function getReserveNormalizedVariableDebt_7ray() returns uint256 {
	uint256 index;
	require (to_mathint(index)==7*ray());
	return index;
}

//todo: check balanceof after mint (stable index), burn after balanceof

definition MAX_DISCOUNT() returns uint256 = 10000; // equals to 100% discount, in points

ghost mapping(address => mapping (uint256 => uint256)) discount_ghost;
ghost mapping(uint256 => uint256) index_ghost;

/**
* Query index_ghost for the index value at the input timestamp
**/
function indexAtTimestamp(uint256 timestamp) returns uint256 {
    require index_ghost[timestamp] >= ray();
    return index_ghost[timestamp];
    // return 1001684385021630839436707910;//index_ghost[timestamp];
}

/**
* Query discount_ghost for the [user]'s balance of discount token at [timestamp]
**/
function balanceOfDiscountTokenAtTimestamp(address user, uint256 timestamp) returns uint256 {
	return discount_ghost[user][timestamp];
}

/**
* Returns an env instance with [ts] as the block timestamp
**/
function envAtTimestamp(uint256 ts) returns env {
	env e;
	require(e.block.timestamp == ts);
	return e;
}

/**
* @title at any point in time, the user's discount rate isn't larger than 100%
**/
invariant discountCantExceed100Percent(address user)
	getUserDiscountRate(user) <= MAX_DISCOUNT()
	{
		preserved updateDiscountDistribution(address sender,address recipient,uint256 senderDiscountTokenBalance,uint256 recipientDiscountTokenBalance,uint256 amount) with (env e) {
			require(indexAtTimestamp(e.block.timestamp) >= ray());
		}
	}

/**
* Imported rules from VariableDebtToken.spec
**/
//pass
use rule disallowedFunctionalities;

/**
* @title proves that a user's discount rate can be updated only by calling rebalanceUserDiscountPercent
* This rule fails since updateDiscountDistribution, mint and burn can recalculate and update the user discount rate
**/
// rule onlyRebalanceCanUpdateUserDiscountRate(method f) {
// 	address user;
// 	uint256 discRateBefore = getUserDiscountRate(user);
// 	requireInvariant discountCantExceed100Percent(user);

// 	env e;
// 	calldataarg args;
// 	f(e,args);

// 	uint256 discRateAfter = getUserDiscountRate(user);

// 	assert(discRateAfter != discRateBefore => f.selector == sig:rebalanceUserDiscountPercent(address).selector);
// }

/**
* @title proves that the user's balance of debt token (as reported by GhoVariableDebtToken::balanceOf) can't increase by calling any external non-mint function.
**/
//pass
rule nonMintFunctionCantIncreaseBalance(method f) filtered { f-> f.selector != sig:mint(address, address, uint256, uint256).selector } {
	address user;
	uint256 ts1;
	uint256 ts2;
	require(ts2 >= ts1);
	// Forcing the index to be fixed (otherwise the rule times out). For non-fixed index replace `==` with `>=`
	require((indexAtTimestamp(ts1) >= ray()) && 
			(indexAtTimestamp(ts2) == indexAtTimestamp(ts1)));

	require(getUserCurrentIndex(user) == indexAtTimestamp(ts1));
	requireInvariant discountCantExceed100Percent(user);

	env e = envAtTimestamp(ts2);
	uint256 balanceBeforeOp = balanceOf(e, user);
	calldataarg args;
	f(e,args);
	mathint balanceAfterOp = balanceOf(e, user);
	mathint allowedDiff = indexAtTimestamp(ts2) / ray();
	// assert(balanceAfterOp != balanceBeforeOp + allowedDiff + 1);
	assert(balanceAfterOp <= balanceBeforeOp + allowedDiff);
}

/**
* @title proves that a call to a non-mint operation won't increase the user's balance of the actual debt tokens (i.e. it's scaled balance)
**/
// pass
rule nonMintFunctionCantIncreaseScaledBalance(method f) filtered { f-> f.selector != sig:mint(address, address, uint256, uint256).selector } {
	address user;
	uint256 ts1;
	uint256 ts2;
	require(ts2 >= ts1);
	require((indexAtTimestamp(ts1) >= ray()) && 
			(indexAtTimestamp(ts2) >= indexAtTimestamp(ts1)));

	require(getUserCurrentIndex(user) == indexAtTimestamp(ts1));
	requireInvariant discountCantExceed100Percent(user);
	uint256 balanceBeforeOp = scaledBalanceOf(user);
	env e = envAtTimestamp(ts2);
	calldataarg args;
	f(e,args);
	uint256 balanceAfterOp = scaledBalanceOf(user);
	assert(balanceAfterOp <= balanceBeforeOp);
}

/**
* @title proves that debt tokens aren't transferable
**/
// pass
rule debtTokenIsNotTransferable(method f) {
	address user1;
	address user2;
	require(user1 != user2);
	uint256 scaledBalanceBefore1 = scaledBalanceOf(user1);
	uint256 scaledBalanceBefore2 = scaledBalanceOf(user2);
	env e;
	calldataarg args;
	f(e,args);
	uint256 scaledBalanceAfter1 = scaledBalanceOf(user1);
	uint256 scaledBalanceAfter2 = scaledBalanceOf(user2);

	assert( scaledBalanceBefore1 + scaledBalanceBefore2 == scaledBalanceAfter1 + scaledBalanceAfter2 
	=> (scaledBalanceBefore1 == scaledBalanceAfter1 && scaledBalanceBefore2 == scaledBalanceAfter2));
}

/**
* @title proves that only burn/mint/rebalanceUserDiscountPercent/updateDiscountDistribution can modify user's scaled balance
**/
// pass
rule onlyCertainFunctionsCanModifyScaledBalance(method f) {
	address user;
	uint256 ts1;
	uint256 ts2;
	require(ts2 >= ts1);
	require((indexAtTimestamp(ts1) >= ray()) && 
			(indexAtTimestamp(ts2) >= indexAtTimestamp(ts1)));

	require(getUserCurrentIndex(user) == indexAtTimestamp(ts1));
	requireInvariant discountCantExceed100Percent(user);
	uint256 balanceBeforeOp = scaledBalanceOf(user);
	env e = envAtTimestamp(ts2);
	calldataarg args;
	f(e,args);
	uint256 balanceAfterOp = scaledBalanceOf(user);
	assert(balanceAfterOp != balanceBeforeOp => (
		(f.selector == sig:mint(address ,address ,uint256 ,uint256).selector) ||
		(f.selector == sig:burn(address ,uint256 ,uint256).selector) ||
		(f.selector == sig:updateDiscountDistribution(address ,address ,uint256 ,uint256 ,uint256).selector) ||
		(f.selector == sig:rebalanceUserDiscountPercent(address).selector)));
}

/**
* @title proves that only a call to decreaseBalanceFromInterest will decrease the user's accumulated interest listing.
**/
// pass
rule userAccumulatedDebtInterestWontDecrease(method f) {
	address user;
	uint256 ts1;
	uint256 ts2;
	require(ts2 >= ts1);
	require((indexAtTimestamp(ts1) >= ray()) && 
			(indexAtTimestamp(ts2) >= indexAtTimestamp(ts1)));

	require(getUserCurrentIndex(user) == indexAtTimestamp(ts1));
	requireInvariant discountCantExceed100Percent(user);
	uint256 initAccumulatedInterest = getUserAccumulatedDebtInterest(user);
	env e2 = envAtTimestamp(ts2);
	calldataarg args;
	f(e2,args);
	uint256 finAccumulatedInterest = getUserAccumulatedDebtInterest(user);
	assert(initAccumulatedInterest > finAccumulatedInterest => f.selector == sig:decreaseBalanceFromInterest(address, uint256).selector);
}

/**
* @title proves that a user can't nullify its debt without calling burn
**/
// pass
rule userCantNullifyItsDebt(method f) {
    address user;
    env e;
    env e2;
	require(getUserCurrentIndex(user) == indexAtTimestamp(e.block.timestamp));
	requireInvariant discountCantExceed100Percent(user);
	uint256 balanceBeforeOp = balanceOf(e, user);
	calldataarg args;
    require e2.block.timestamp == e.block.timestamp;
	f(e2,args);
	uint256 balanceAfterOp = balanceOf(e, user);
	assert((balanceBeforeOp > 0 && balanceAfterOp == 0) => (f.selector == sig:burn(address, uint256, uint256).selector));
}

/***************************************************************
* Integrity of Mint
***************************************************************/

/**
* @title proves that after calling mint, the user's discount rate is up to date
**/
rule integrityOfMint_updateDiscountRate() {
	address user1;
	address user2;
	env e;
	uint256 amount;
	uint256 index = indexAtTimestamp(e.block.timestamp);
	mint(e, user1, user2, amount, index);
	uint256 debtBalance = balanceOf(e, user2);
	uint256 discountBalance = getBalanceOfDiscountToken(e, user2);
	uint256 discountRate = getUserDiscountRate(user2);
	assert(discStrategy.calculateDiscountRate(debtBalance, discountBalance) == discountRate);
}

/**
* @title proves the after calling mint, the user's state is updated with the recent index value
**/
rule integrityOfMint_updateIndex() {
	address user1;
	address user2;
	env e;
	uint256 amount;
	uint256 index;
	mint(e, user1, user2, amount, index);
	assert(getUserCurrentIndex(user2) == index);
}

/**
* @title proves that on a fixed index calling mint(user, amount) will increase the user's scaled balance by amount. 
**/
// pass
rule integrityOfMint_updateScaledBalance_fixedIndex() {
	address user;
	env e;
	uint256 balanceBefore = balanceOf(e, user);
	uint256 scaledBalanceBefore = scaledBalanceOf(user);
	address caller;
	uint256 amount;
	uint256 index = indexAtTimestamp(e.block.timestamp);
	require(getUserCurrentIndex(user) == index);
	mint(e, caller, user, amount, index);

	uint256 balanceAfter = balanceOf(e, user);
	mathint scaledBalanceAfter = scaledBalanceOf(user);
	mathint scaledAmount = rayDivCVL(amount, index);

	assert(scaledBalanceAfter == scaledBalanceBefore + scaledAmount);
}

/**
* @title proves that mint can't effect other user's scaled balance
**/
// pass
rule integrityOfMint_userIsolation() {
	address otherUser;
	uint256 scaledBalanceBefore = scaledBalanceOf(otherUser);
	env e;
	uint256 amount;
	uint256 index;
	address targetUser;
	address caller;
	mint(e, caller, targetUser, amount, index);
	uint256 scaledBalanceAfter = scaledBalanceOf(otherUser);
	assert(scaledBalanceAfter != scaledBalanceBefore => otherUser == targetUser);
}

/**
* @title proves that when calling mint, the user's balance (as reported by GhoVariableDebtToken::balanceOf) will increase if the call is made on bahalf of the user.
**/
rule onlyMintForUserCanIncreaseUsersBalance() {
	address user1;
    env e;
	require(getUserCurrentIndex(user1) == indexAtTimestamp(e.block.timestamp));
	
	uint256 finBalanceBeforeMint = balanceOf(e, user1);
	uint256 amount;
	mint(e,user1, user1, amount, indexAtTimestamp(e.block.timestamp));
	uint256 finBalanceAfterMint = balanceOf(e, user1);

	assert(finBalanceAfterMint != finBalanceBeforeMint);
}

/**
* @title proves that a user can't decrease the ovelall interest of his position by taking more loans, compared to another user with the same initial position.
* This rule times out.
**/
// rule integrityOfMint_cantDecreaseInterestWithMint() {
// 	address user1;
// 	uint256 ts1;
// 	env e1 = envAtTimestamp(ts1);
// 	uint256 ts2;
// 	require(ts2 >= ts1);
// 	env e2 = envAtTimestamp(ts2);
// 	uint256 ts3;
// 	require(ts3 >= ts2);
// 	env e3 = envAtTimestamp(ts3);
// 	// Forcing the index to be fixed (otherwise the rule times out). For non-fixed index replace `==` with `>=`
// 	require((indexAtTimestamp(ts1) >= ray()) && 
// 			(indexAtTimestamp(ts2) >= indexAtTimestamp(ts1)) &&
// 			(indexAtTimestamp(ts3) >= indexAtTimestamp(ts2)));


// 	require(getUserCurrentIndex(user1) == indexAtTimestamp(ts1));
// 	uint256 amount;
// 	storage initialStorage = lastStorage;
// 	mint(e2, user1, user1, amount, indexAtTimestamp(ts2));

// 	rebalanceUserDiscountPercent(e3, user1);
// 	uint256 balanceFromInterestAfterMint = getBalanceFromInterest(user1);

// 	rebalanceUserDiscountPercent(e3, user1) at initialStorage;
// 	uint256 balanceFromInterestWithoutMint = getBalanceFromInterest(user1);

// 	assert(balanceFromInterestAfterMint >= balanceFromInterestWithoutMint);
// }

//pass
use rule integrityMint_atoken;

/***************************************************************
* Integrity of Burn
***************************************************************/

/**
* @title proves that after calling burn, the user's discount rate is up to date
**/
rule integrityOfBurn_updateDiscountRate() {
	address user;
	env e;
	uint256 amount;
	uint256 index = indexAtTimestamp(e.block.timestamp);
	burn(e, user, amount, index);
	uint256 debtBalance = balanceOf(e, user);
	uint256 discountBalance = getBalanceOfDiscountToken(e, user);
	uint256 discountRate = getUserDiscountRate(user);
	assert(discStrategy.calculateDiscountRate(debtBalance, discountBalance) == discountRate);
}

/**
* @title proves the after calling burn, the user's state is updated with the recent index value
**/
rule integrityOfBurn_updateIndex() {
	address user;
	env e;
	uint256 amount;
	uint256 index;
	burn(e, user, amount, index);
	assert(getUserCurrentIndex(user) == index);
}

/**
* @title proves that calling burn with 0 amount doesn't change the user's balance
**/
use rule burnZeroDoesntChangeBalance;

/**
* @title proves a concrete case of repaying the full debt that ends with a zero balance
**/
rule integrityOfBurn_fullRepay_concrete() {
	env e;
	address user;
	uint256 currentDebt = balanceOf(e, user);
	uint256 index = indexAtTimestamp(e.block.timestamp);
	require(getUserCurrentIndex(user) == ray());
	require(to_mathint(index) == 2*ray());
	require(to_mathint(scaledBalanceOf(user)) == 4*ray());
	burn(e, user, currentDebt, index);
	uint256 scaled = scaledBalanceOf(user);
	assert(scaled == 0);
}


/**
* @title proves that burn can't effect other user's scaled balance
**/
// pass
rule integrityOfBurn_userIsolation() {
	address otherUser;
	uint256 scaledBalanceBefore = scaledBalanceOf(otherUser);
	env e;
	uint256 amount;
	uint256 index;
	address targetUser;
	burn(e,targetUser, amount, index);
	uint256 scaledBalanceAfter = scaledBalanceOf(otherUser);
	assert(scaledBalanceAfter != scaledBalanceBefore => otherUser == targetUser);
}

/***************************************************************
* Integrity of updateDiscountDistribution
***************************************************************/

/**
* @title proves that the discount rate is calculated correctly when calling updateDiscountDistribution
**/
// rule integrityOfUpdateDiscountDistribution_discountRate() {
// 	address sender;
//     address recipient;
//     uint256 senderDiscountTokenBalanceBefore;
//     uint256 recipientDiscountTokenBalanceBefore;
//     uint256 amount;
// 	uint256 senderDiscountTokenBalanceAfter = senderDiscountTokenBalanceBefore - amount;
//     uint256 recipientDiscountTokenBalanceAfter = recipientDiscountTokenBalanceBefore + amount;
// 	env e0;
// 	env e;
// 	require(e.block.timestamp > e0.block.timestamp);
// 	require(indexAtTimestamp(e.block.timestamp) >= indexAtTimestamp(e0.block.timestamp));
// 	require(indexAtTimestamp(e0.block.timestamp) == ray()); // reduces execution time
// 	require(getUserCurrentIndex(sender) == indexAtTimestamp(e0.block.timestamp));
// 	require(getUserCurrentIndex(recipient) == indexAtTimestamp(e0.block.timestamp));

// 	require(getBalanceOfDiscountToken(e0, sender) == senderDiscountTokenBalanceBefore);
// 	require(getBalanceOfDiscountToken(e0, recipient) == recipientDiscountTokenBalanceBefore);
// 	require(discStrategy.calculateDiscountRate(balanceOf(e0, sender), senderDiscountTokenBalanceBefore) == getUserDiscountRate(sender));
// 	require(discStrategy.calculateDiscountRate(balanceOf(e0, recipient), recipientDiscountTokenBalanceBefore) == getUserDiscountRate(recipient));

	
// 	require(getBalanceOfDiscountToken(e, sender) == senderDiscountTokenBalanceAfter);
// 	require(getBalanceOfDiscountToken(e, recipient) == recipientDiscountTokenBalanceAfter);

// 	updateDiscountDistribution(e, sender, recipient, senderDiscountTokenBalanceBefore, recipientDiscountTokenBalanceBefore, amount);
// 	uint256 senderBalance = balanceOf(e, sender);
// 	uint256 recipientBalance = balanceOf(e, recipient);
// 	assert(discStrategy.calculateDiscountRate(senderBalance, senderDiscountTokenBalanceAfter) == getUserDiscountRate(sender));
// 	assert(discStrategy.calculateDiscountRate(recipientBalance, recipientDiscountTokenBalanceAfter) == getUserDiscountRate(recipient));
// }

/**
* @title proves the after calling updateDiscountDistribution, the user's state is updated with the recent index value
**/
rule integrityOfUpdateDiscountDistribution_updateIndex() {
	address sender;
	address recipient;
	uint256 senderDiscountTokenBalance;
    uint256 recipientDiscountTokenBalance;
	env e;
	uint256 amount;
	uint256 index = indexAtTimestamp(e.block.timestamp);
	updateDiscountDistribution(e, sender, recipient, senderDiscountTokenBalance, recipientDiscountTokenBalance, amount);
	assert(scaledBalanceOf(sender) > 0 => getUserCurrentIndex(sender) == index);
	assert(scaledBalanceOf(recipient) > 0 => getUserCurrentIndex(recipient) == index);
}


/**
* @title proves that updateDiscountDistribution can't effect other user's scaled balance
**/
// pass
rule integrityOfUpdateDiscountDistribution_userIsolation() {
	address otherUser;
	uint256 scaledBalanceBefore = scaledBalanceOf(otherUser);
	env e;
	uint256 amount;
	uint256 senderDiscountTokenBalance;
	uint256 recipientDiscountTokenBalance;
	address sender;
	address recipient;
	updateDiscountDistribution(e, sender, recipient, senderDiscountTokenBalance, recipientDiscountTokenBalance, amount);
	uint256 scaledBalanceAfter = scaledBalanceOf(otherUser);
	assert(scaledBalanceAfter != scaledBalanceBefore => (otherUser == sender || otherUser == recipient));
}

/***************************************************************
* Integrity of rebalanceUserDiscountPercent
***************************************************************/

/**
* @title proves that after calling rebalanceUserDiscountPercent, the user's discount rate is up to date
**/
rule integrityOfRebalanceUserDiscountPercent_updateDiscountRate() {
	address user;
	env e;
	rebalanceUserDiscountPercent(e, user);
	assert(discStrategy.calculateDiscountRate(balanceOf(e, user), getBalanceOfDiscountToken(e, user)) == getUserDiscountRate(user));
}

/**
* @title proves the after calling rebalanceUserDiscountPercent, the user's state is updated with the recent index value
**/
rule integrityOfRebalanceUserDiscountPercent_updateIndex() {
	address user;
	env e;
	rebalanceUserDiscountPercent(e, user);
	uint256 index = indexAtTimestamp(e.block.timestamp);
	assert(getUserCurrentIndex(user) == index);
}

/**
* @title proves that rebalanceUserDiscountPercent can't effect other user's scaled balance
**/
// pass
rule integrityOfRebalanceUserDiscountPercent_userIsolation() {
	address otherUser;
	uint256 scaledBalanceBefore = scaledBalanceOf(otherUser);
	env e;
	address targetUser;
	rebalanceUserDiscountPercent(e, targetUser);
	uint256 scaledBalanceAfter = scaledBalanceOf(otherUser);
	assert(scaledBalanceAfter != scaledBalanceBefore => otherUser == targetUser);
}

/***************************************************************
* Integrity of balanceOf
***************************************************************/

/**
* @title proves that a user with 100% discounts has a fixed balance over time
**/
rule integrityOfBalanceOf_fullDiscount() {
	address user;
	uint256 fullDiscountRate = 10000; //100%
	require(getUserDiscountRate(user) == fullDiscountRate);
	env e1;
	env e2;
	uint256 index1 = indexAtTimestamp(e1.block.timestamp);
	uint256 index2 = indexAtTimestamp(e2.block.timestamp);
	assert(balanceOf(e1, user) == balanceOf(e2, user));
}

/**
* @title proves that a user's balance, with no discount, is equal to rayMul(scaledBalance, current index)
**/
rule integrityOfBalanceOf_noDiscount() {
	address user;
	require(getUserDiscountRate(user) == 0);
	env e;
	uint256 scaledBalance = scaledBalanceOf(user);
	uint256 currentIndex = indexAtTimestamp(e.block.timestamp);
	mathint expectedBalance = rayMulCVL(scaledBalance, currentIndex);
	assert(to_mathint(balanceOf(e, user)) == expectedBalance);
}

/**
* @title proves the a user with zero scaled balance has a zero balance
**/
rule integrityOfBalanceOf_zeroScaledBalance() {
	address user;
	env e;
	uint256 scaledBalance = scaledBalanceOf(user);
	require(scaledBalance == 0);
	assert(balanceOf(e, user) == 0);
}

rule burnAllDebtReturnsZeroDebt(address user) {
    env e;
	uint256 _variableDebt = balanceOf(e, user);
	burn(e, user, _variableDebt, indexAtTimestamp(e.block.timestamp));
	uint256 variableDebt_ = balanceOf(e, user);
    assert(variableDebt_ == 0);
}


rule mutant_11() {
    env e;
    address user; address onBehalfOf; uint256 amount; uint256 index;
    require user ==1; require onBehalfOf==10;
    require getUserCurrentIndex(onBehalfOf) <= index;

    uint256 amountScaled = rayDiv_gst(amount,index);
    uint256 prev_bal = scaledBalanceOf(e, onBehalfOf);

    mint(e,user,onBehalfOf,amount,index);

    mathint after_bal = scaledBalanceOf(e, onBehalfOf);
    assert (after_bal <= prev_bal + amountScaled);
}

rule mutant_13_sender() {
    env e;
    address sender; address recipient; 
    uint256 senderDiscountTokenBalance; uint256 recipientDiscountTokenBalance; uint256 amount;

    uint256 sender_scaledBal_prev = scaledBalanceOf(sender);   
    uint256 discountScaled = get_discount_scaled(e,sender);
    updateDiscountDistribution(e, sender, recipient,
                               senderDiscountTokenBalance, recipientDiscountTokenBalance,
                               amount);
    uint256 sender_scaledBal_after = scaledBalanceOf(sender);

    assert (discountScaled > 0 => sender_scaledBal_after<sender_scaledBal_prev);
}


rule mutant_13_recipient() {
    env e;
    address sender; address recipient; 
    uint256 senderDiscountTokenBalance; uint256 recipientDiscountTokenBalance; uint256 amount;

    uint256 recipient_scaledBal_prev = scaledBalanceOf(recipient);   
    uint256 discountScaled = get_discount_scaled(e,recipient);
    updateDiscountDistribution(e, sender, recipient,
                               senderDiscountTokenBalance, recipientDiscountTokenBalance,
                               amount);
    uint256 recipient_scaledBal_after = scaledBalanceOf(recipient);

    assert (discountScaled > 0 => recipient_scaledBal_after<recipient_scaledBal_prev);
}





rule mutant_10_on_sender() {
    env e;
    address sender; address recipient; 
    uint256 senderDiscountTokenBalance; uint256 recipientDiscountTokenBalance; uint256 amount_1;
    require (sender != recipient);
    
    storage initState = lastStorage;

    updateDiscountDistribution(e, sender, recipient,
                               senderDiscountTokenBalance, recipientDiscountTokenBalance,
                               amount_1);
    uint256 discountPercent_1 = getDiscountPercent(e, sender);

    uint256 amount_2;
    updateDiscountDistribution(e, sender, recipient,
                               senderDiscountTokenBalance, recipientDiscountTokenBalance,
                               amount_2) at initState;
    uint256 discountPercent_2 = getDiscountPercent(e, sender);
        
    satisfy (discountPercent_1 != discountPercent_2);
}


rule mutant_10_on_recipient() {
    env e;
    address sender; address recipient; 
    uint256 senderDiscountTokenBalance; uint256 recipientDiscountTokenBalance; uint256 amount_1;
    require (sender != recipient);
    
    storage initState = lastStorage;

    updateDiscountDistribution(e, sender, recipient,
                               senderDiscountTokenBalance, senderDiscountTokenBalance,
                               amount_1);
    uint256 discountPercent_1 = getDiscountPercent(e, recipient);

    uint256 amount_2;
    updateDiscountDistribution(e, sender, recipient,
                               senderDiscountTokenBalance, senderDiscountTokenBalance,
                               amount_2) at initState;
    uint256 discountPercent_2 = getDiscountPercent(e, recipient);
        
    satisfy (discountPercent_1 != discountPercent_2);
}


function get_discount_scaled(env e, address user) returns uint256 {
    uint256 user_scaledBal_prev = scaledBalanceOf(user);
    
    //    assert (user_scaledBal_after <= user_scaledBal_prev);
    uint256 current_index = indexAtTimestamp(e.block.timestamp);
    uint256 user_index = getUserCurrentIndex(user);
    require user_index <= current_index;

    //uint256 bal_increase = (current_index-sender_index) * previousScaledBalance_of_sender;
    mathint bal_increase = rayMul_gst(user_scaledBal_prev, current_index) -
        rayMul_gst(user_scaledBal_prev, user_index);

    //uint256 discountScaled = bal_increase * sender_precentage / index;
    uint256 discountPercent = getDiscountPercent(e, user);
    uint256 discount = require_uint256(bal_increase * discountPercent / 10000);
    uint256 discountScaled = rayDiv_gst(discount, current_index);

    return discountScaled;
}


// same as mutant_13_sender
rule mutant_9() {
    env e;
    address sender; address recipient; 
    uint256 senderDiscountTokenBalance; uint256 recipientDiscountTokenBalance; uint256 amount;

    uint256 sender_scaledBal_prev = scaledBalanceOf(sender);
    uint256 discountScaled = get_discount_scaled(e,sender);

    updateDiscountDistribution(e, sender, recipient,
                               senderDiscountTokenBalance, senderDiscountTokenBalance,
                               amount);
    uint256 sender_scaledBal_after = scaledBalanceOf(sender);

    assert (discountScaled > 0 => sender_scaledBal_after<sender_scaledBal_prev);
}


rule mutant_4() {
    env e;
    address a;
    setAToken(e, a);

    assert get_ghoAToken() != 0;
}


rule mutant_8() {
    env e;
    address user; uint256 amount; uint256 index;

    mathint amountScaled = rayDiv(e,amount,index);
    mathint prev_bal = scaledBalanceOf(e, user);
    uint256 discountScaled = get_discount_scaled(e,sender);
    uint256 balanceBeforeBurn = balanceOf(user);

    burn(e,user,amount,index);

    mathint after_bal = scaledBalanceOf(e, user);


    
    assert (after_bal <= prev_bal + amountScaled);
}



