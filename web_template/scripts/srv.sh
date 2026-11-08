#!/usr/bin/env bash
# Server lifecycle for the generated app (per-PORT isolation, PID-file based — never pkill).
# Requires backend/dist (run `npm run build` first). PORT/DATABASE_URL come from the env.
set -u
cd -- "$(dirname -- "$0")/.."
PORT="${PORT:-3000}"
PIDFILE="/tmp/srv-$PORT.pid"
LOGFILE="/tmp/srv-$PORT.log"
URL="http://127.0.0.1:$PORT"

alive() {
  [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null
}

start() {
  if alive && curl -sf "$URL/api/health" >/dev/null; then
    echo "already running: $URL"
    exit 0
  fi
  [ -f "$PIDFILE" ] && kill "$(cat "$PIDFILE")" 2>/dev/null
  rm -f "$PIDFILE"
  nohup node backend/dist/server.js >"$LOGFILE" 2>&1 &
  echo $! >"$PIDFILE"
  for _ in $(seq 1 60); do
    if curl -sf "$URL/api/health" >/dev/null; then
      echo "OK: $URL (pid $(cat "$PIDFILE"))"
      exit 0
    fi
    sleep 0.5
  done
  echo "FAIL: health check timed out; tail of $LOGFILE:"
  tail -5 "$LOGFILE"
  exit 1
}

stop() {
  if [ -f "$PIDFILE" ]; then
    kill "$(cat "$PIDFILE")" 2>/dev/null || true
    sleep 1
    kill -9 "$(cat "$PIDFILE")" 2>/dev/null || true
    rm -f "$PIDFILE"
  fi
  echo "stopped"
}

status() {
  if alive; then
    echo "running (pid $(cat "$PIDFILE"))"
  else
    echo "stopped"
  fi
  curl -s "$URL/api/health" || true
}

case "${1:-}" in
start) start ;;
stop) stop ;;
status) status ;;
restart) stop; start ;;
logs)
  tail -n "${2:-50}" "$LOGFILE"
  ;;
*)
  echo "usage: srv.sh start|stop|status|restart|logs [n]"
  exit 2
  ;;
esac
