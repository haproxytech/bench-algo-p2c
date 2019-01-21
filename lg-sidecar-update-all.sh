for i in 1 2 3 4 5 6;do scp sidecar.cfg lg$i:svc-mesh/; ssh lg$i 'cd svc-mesh/; for s in *.conf; do ./sidecar.sh $s stop start ;done'; done
