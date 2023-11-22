#!/bin/sh

if (($# > 0))
then
certoraRun certora/harness/ghoVariableDebtTokenHarness.sol:GhoVariableDebtTokenHarness \
    certora/harness/DummyPool.sol \
    certora/harness/DummyERC20WithTimedBalanceOf.sol \
    certora/munged/contracts/facilitators/aave/interestStrategy/GhoDiscountRateStrategy.sol \
    certora/harness/DummyERC20A.sol certora/harness/DummyERC20B.sol \
    --verify GhoVariableDebtTokenHarness:certora/specs/ghoVariableDebtToken.spec \
    --link GhoVariableDebtTokenHarness:_discountRateStrategy=GhoDiscountRateStrategy \
    --link GhoVariableDebtTokenHarness:_discountToken=DummyERC20WithTimedBalanceOf \
    --link GhoVariableDebtTokenHarness:POOL=DummyPool \
    --loop_iter 2 \
    --solc solc8.10 \
    --optimistic_loop \
    --rule "${@}" \
    --prover_args '-depth 0 -adaptiveSolverConfig false -smt_nonLinearArithmetic true' --server staging --prover_version shelly/z3-4-12-3-build \
    --msg "GhoVariableDebtToken"

else
certoraRun certora/harness/ghoVariableDebtTokenHarness.sol:GhoVariableDebtTokenHarness \
    certora/harness/DummyPool.sol \
    certora/harness/DummyERC20WithTimedBalanceOf.sol \
    certora/munged/contracts/facilitators/aave/interestStrategy/GhoDiscountRateStrategy.sol \
    certora/harness/DummyERC20A.sol certora/harness/DummyERC20B.sol \
    --verify GhoVariableDebtTokenHarness:certora/specs/ghoVariableDebtToken.spec \
    --link GhoVariableDebtTokenHarness:_discountRateStrategy=GhoDiscountRateStrategy \
    --link GhoVariableDebtTokenHarness:_discountToken=DummyERC20WithTimedBalanceOf \
    --link GhoVariableDebtTokenHarness:POOL=DummyPool \
    --loop_iter 2 \
    --solc solc8.10 \
    --optimistic_loop \
    --prover_args '-depth 0 -adaptiveSolverConfig false -smt_nonLinearArithmetic true' --server staging --prover_version shelly/z3-4-12-3-build \
    --msg "GhoVariableDebtToken"

fi