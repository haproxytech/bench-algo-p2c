#!/bin/bash
export PORT=2001
export SOURCE=svc-time.py
export SERVICE=127.0.0.2
export SIDECAR=127.0.0.3
export TIME_URL="http://$SIDECAR:2$PORT/GetTime"
export USER_URL="http://$SIDECAR:2$PORT/UserAttr"
export LOG_URL="http://$SIDECAR:2$PORT/Log"
export HAPROXY=${HAPROXY:-haproxy}
export PYTHON=${PYTHON:-python}
export PATH=".:$PATH"

if [ -s "/tmp/haproxy-$PORT.pid" ]; then
        pid=$(cat /tmp/haproxy-$PORT.pid)
        kill $pid >/dev/null 2>&1
fi

if [ -z "$1" -o "$1" = "start" ]; then
        "$HAPROXY" -D -f sidecar.cfg -p "/tmp/haproxy-$PORT.pid"
        "$PYTHON" "$SOURCE" "$SERVICE:1$PORT" "$TIME_URL" "$USER_URL" "$LOG_URL"
fi
