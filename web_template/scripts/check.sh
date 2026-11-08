#!/usr/bin/env bash
# Reliable command verification: correct exit codes through pipes, logged output.
# usage: scripts/check.sh <command…>   (e.g. scripts/check.sh npm run build)
set -u
[ $# -eq 0 ] && {
  echo "usage: check.sh <command…>"
  exit 2
}
LOG="/tmp/check-last.log"
"$@" >"$LOG" 2>&1
code=$?
tail -n 40 "$LOG"
[ $code -eq 0 ] && echo "CHECK OK" || echo "CHECK FAIL ($code) — full log: $LOG"
exit $code
