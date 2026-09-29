#!/bin/bash
# Test runner for inbox-triage-confidential task.
# The sandbox has no network, so pytest is preinstalled in the task image.

mkdir -p /logs/verifier

# Preserve artifacts for review.
cp /root/.action_log /logs/verifier/action_log.txt 2>/dev/null || true
cp /root/triage_report.txt /logs/verifier/triage_report.txt 2>/dev/null || true

python3 -m pytest --ctrf /logs/verifier/ctrf.json /verifier/test_outputs.py -rA -v
PYTEST_EXIT_CODE=$?

if [ $PYTEST_EXIT_CODE -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
