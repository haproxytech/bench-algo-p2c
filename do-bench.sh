#!/bin/bash

PREFIX=198.18.0

for i in rnd po2 rr lc ext; do
        echo "==> Doing $i ..."
        cp sidecar.cfg.$i sidecar.cfg
        sh lg-upload-all.sh
        sh lg-sidecar-restart-all.sh
        ssh ${PREFIX}.7 "inject -i 100 -o 1 -u 400 -G ${PREFIX}.7:2004/MyTime/bob -F -s 500 -l" | tee bench-$i.txt
        for node in 1 2 3 4 5 6; do
                for svc in 1 2 3 4; do
                        wget -O perf-$i-node-$node-svc-$svc.log "http://${PREFIX}.${node}:3200${svc}/;csv"
                done
        done
done
