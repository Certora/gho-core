#!/bin/sh

if (($# > 0))
then
certoraRun certora/harness/GhoTokenHarness.sol:GhoTokenHarness certora/munged/contracts/gho/GhoToken.sol \
    --verify GhoTokenHarness:certora/specs/ghoToken.spec \
    --solc solc8.10 \
    --loop_iter 3 \
    --optimistic_loop \
    --rule "${@}" \
    --msg "GhoToken rules ${@}"
else
certoraRun certora/harness/GhoTokenHarness.sol:GhoTokenHarness certora/munged/contracts/gho/GhoToken.sol \
    --verify GhoTokenHarness:certora/specs/ghoToken.spec \
    --solc solc8.10 \
    --loop_iter 3 \
    --optimistic_loop \
    --msg "GhoToken, all rules."
fi