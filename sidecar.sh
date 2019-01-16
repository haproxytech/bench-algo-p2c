#!/bin/bash

usage() {
        echo "Usage: ${1##*/} <config> [start|stop|status]"
        exit 1
}

[ $# -ge 2 ] || usage "$0"

config="$1"
action="$2"

if [ ! -r "$config" ]; then
        echo "Config file $config not readable."
        exit 1
fi

source "$config"

if [ -z "$SIDECAR_PID" ]; then
        echo "SIDECAR_PID not set, please check config $config."
        exit 1
fi

case "$action" in
        status)
                if [ -s "$SIDECAR_PID" ]; then
                        echo "Running as pid $(cat "$SIDECAR_PID")"
                        exit 0
                else
                        echo "Not running"
                        exit 1
                fi
                ;;
        stop)
                if [ -s "$SIDECAR_PID" ]; then
                        kill $(cat "$SIDECAR_PID") >/dev/null 2>&1
                        rm -f "$SIDECAR_PID" >/dev/null 2>&1
                        echo "Now stopped"
                else
                        echo "Already stopped"
                fi
                exit 0
                ;;
        start)
                if [ -s "$SIDECAR_PID" ]; then
                        echo "Still running as pid $(cat "$SIDECAR_PID")"
                        exit 0
                fi

                "$HAPROXY" -D -f sidecar.cfg -p "$SIDECAR_PID"
                ;;
        *)
                usage "$0"
                ;;
esac
