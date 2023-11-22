if [[ "$1" ]]
then
    RULE="--rule $1"
    MSG="--msg \"$1:: $2\""
fi

echo "RULE is ==>" $RULE "<=="

certoraRun certora/harness/ghoVariableDebtTokenHarness.sol:GhoVariableDebtTokenHarness \
    certora/harness/DummyPool.sol \
    certora/harness/DummyERC20WithTimedBalanceOf.sol \
    certora/munged/contracts/facilitators/aave/interestStrategy/GhoDiscountRateStrategy.sol \
    certora/harness/DummyERC20A.sol certora/harness/DummyERC20B.sol \
    --verify GhoVariableDebtTokenHarness:certora/specs/mutant_11.spec \
    --link GhoVariableDebtTokenHarness:_discountRateStrategy=GhoDiscountRateStrategy \
    --link GhoVariableDebtTokenHarness:_discountToken=DummyERC20WithTimedBalanceOf \
    --link GhoVariableDebtTokenHarness:POOL=DummyPool \
    --loop_iter 2 \
    --solc solc8.10 \
    --optimistic_loop \
    --smt_timeout 900 \
    --send_only \
    --fe_version latest \
    --prover_args "-mediumTimeout 30 -depth 15" \
    --rule $1 \
    --msg "$1 $2"
