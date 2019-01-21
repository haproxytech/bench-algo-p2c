#!/bin/sh
for i in 1 2 3 4 5 6;do ssh lg$i 'cd svc-mesh/; for s in *.conf; do ./sidecar.sh $s stop start;done';done
