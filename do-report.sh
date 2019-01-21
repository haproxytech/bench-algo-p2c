#!/bin/bash

for algo in rnd po2 rr lc ext; do
        for node in 1 2 3 4 5 6; do
                echo $node $(grep inbound,srv perf-$algo-node-$node-svc-*.log |cut -f6 -d',')
        done > perf-smax-per-node-$algo.log
done
