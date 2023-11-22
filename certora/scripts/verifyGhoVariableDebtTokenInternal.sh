
certoraRun certora/harness/ghoVariableDebtTokenHarnessInternal.sol:GhoVariableDebtTokenHarnessInternal \
    certora/munged/contracts/facilitators/aave/interestStrategy/GhoDiscountRateStrategy.sol \
    --verify GhoVariableDebtTokenHarnessInternal:certora/specs/ghoVariableDebtTokenInternal.spec \
    --loop_iter 2 \
    --solc solc8.10 \
    --optimistic_loop \
    --smt_timeout 900 \
    --prover_args "-mediumTimeout 30 -depth 15" \
    --msg "GhoVariableDebtToken internal functions"

