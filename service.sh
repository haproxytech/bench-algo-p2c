#!/bin/bash

usage() {
        echo "Usage: ${1##*/} <config> [start|stop|status]..."
        exit 1
}

[ $# -ge 2 ] || usage "$0"

config="$1"; shift
actions="$@"

if [ ! -r "$config" ]; then
        echo "Config file $config not readable."
        exit 1
fi

source "$config"

if [ -z "$SERVICE_PID" ]; then
        echo "SERVICE_PID not set, please check config $config."
        exit 1
fi

START=""
[ -z "$CPUS" ] || START="taskset -c $CPUS"

fail=0
for action in ${actions[@]}; do
    case "$action" in
        status)
                if [ -s "$SERVICE_PID" ]; then
                        echo "Running as pid $(cat "$SERVICE_PID")"
                else
                        echo "Not running"
                        fail=1
                fi
                ;;
        stop)
                if [ -s "$SERVICE_PID" ]; then
                        kill $(cat "$SERVICE_PID") >/dev/null 2>&1
                        rm -f "$SERVICE_PID" >/dev/null 2>&1
                        echo "Now stopped"
                else
                        echo "Already stopped"
                fi
                ;;
        start)
                if [ -s "$SERVICE_PID" ]; then
                        echo "Still running as pid $(cat "$SERVICE_PID")"
                else
                        $START "$PYTHON" "$SOURCE" "$SERVICE:1$PORT" "$TIME_URL" "$USER_URL" "$LOG_URL" </dev/null >/dev/null 2>&1 &
                        ret=$?
                        if [ $ret != 0 ]; then
                                echo "Service failed to start."
                                fail=1
                        else
                                echo $! > "$SERVICE_PID"
                                disown
                        fi
                fi
                ;;
        *)
                usage "$0"
                ;;
    esac
done
exit $fail
