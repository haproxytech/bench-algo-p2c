for i in 1 2 3 4 5 6;do ssh lg$i 'cd svc-mesh/; for s in *.conf; do ./service.sh $s stop start; ./sidecar.sh $s stop start;done';done
