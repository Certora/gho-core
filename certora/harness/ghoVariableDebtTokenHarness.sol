pragma solidity 0.8.10;

import {SafeCast} from '@aave/core-v3/contracts/dependencies/openzeppelin/contracts/SafeCast.sol';
import {PercentageMath} from '@aave/core-v3/contracts/protocol/libraries/math/PercentageMath.sol';
import {GhoVariableDebtToken} from '../munged/contracts/facilitators/aave/tokens/GhoVariableDebtToken.sol';
import {WadRayMath} from '@aave/core-v3/contracts/protocol/libraries/math/WadRayMath.sol';
import {IPool} from '@aave/core-v3/contracts/interfaces/IPool.sol';
import {ScaledBalanceTokenBase} from '../munged/contracts/facilitators/aave/tokens/base/ScaledBalanceTokenBase.sol';



contract GhoVariableDebtTokenHarness is GhoVariableDebtToken {
  using WadRayMath for uint256;
  using SafeCast for uint256;
  using PercentageMath for uint256;

  constructor(IPool pool) public GhoVariableDebtToken(pool) {
    //nop
  }

  function getUserCurrentIndex(address user) external view returns (uint256) {
    return _userState[user].additionalData;
  }

  function getUserDiscountRate(address user) external view returns (uint256) {
    return _ghoUserState[user].discountPercent;
  }

  function getUserAccumulatedDebtInterest(address user) external view returns (uint256) {
    return _ghoUserState[user].accumulatedDebtInterest;
  }

  function scaledBalanceOfToBalanceOf(uint256 bal) public view returns (uint256) {
    return bal.rayMul(POOL.getReserveNormalizedVariableDebt(_underlyingAsset));
  }

  function getBalanceOfDiscountToken(address user) external returns (uint256) {
    return _discountToken.balanceOf(user);
  }

  function rayMul(uint256 x, uint256 y) external view returns (uint256) {
    return x.rayMul(y);
  }

  function rayDiv(uint256 x, uint256 y) external view returns (uint256) {
    return x.rayDiv(y);
  }

  function getIndex(uint256 bal) public view returns (uint256) {
    return POOL.getReserveNormalizedVariableDebt(_underlyingAsset);
  }

  function _accrueDebtOnAction_ext(address user,uint256 previousScaledBalance,
                                   uint256 discountPercent,uint256 index)
      external returns (uint256, uint256) {
      return _accrueDebtOnAction(user,previousScaledBalance,discountPercent,index);
  }

  function ___mint(address account, uint256 amount) external {
      _mint(account, amount.toUint128());
  }

  function _mintScaled_ext(address caller,address onBehalfOf,uint256 amount, uint256 index
                          ) external returns (bool) {
      /*
      uint256 amountScaled = amount.rayDiv(index);
      //    require(amountScaled != 0, Errors.INVALID_MINT_AMOUNT);
      require(amountScaled != 0);

      uint256 previousScaledBalance = scaledBalanceOf(onBehalfOf);
      uint256 discountPercent = getDiscountPercent(onBehalfOf);//_ghoUserState[onBehalfOf].discountPercent;
      (uint256 balanceIncrease, uint256 discountScaled) = _accrueDebtOnAction(
                                                                              onBehalfOf,
                                                                              previousScaledBalance,
                                                                              discountPercent,
                                                                              index
      );
      
      // confirm the amount being borrowed is greater than the discount
      if (amountScaled > discountScaled) {
          _mint(onBehalfOf, (amountScaled + discountScaled).toUint128());
      }
      
      return true;
*/
       return _mintScaled(caller,onBehalfOf,amount,index);
  }

  function _refreshDiscountPercent_ext(
                                       address user,
                                       uint256 balance,
                                       uint256 discountTokenBalance,
                                       uint256 previousDiscountPercent
  ) external {
      _refreshDiscountPercent(user,balance,discountTokenBalance,previousDiscountPercent);
  }

  function get_ghoAToken() external returns (address) {return _ghoAToken;}
}
