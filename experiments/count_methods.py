#!/usr/bin/env python3

import re

shapley_log = "shapley_01.log"

queries = sorted([10,11,16,18,19,3,5,7])

method=dict()

with open(shapley_log, "r") as log:
    for line in log:
        if "NOTICE:" in line and "gates" in line:
            query = int(re.sub(r".*/(.*)\.sql:.* NOTICE.*","\\1", line))
            if query not in method:
                method[query]=[]

            if "d4" in line:
                method[query].append("d4")
            elif "tree decomposition" in line:
                method[query].append("tree dec.")
            elif "interpreted as dD" in line:
                method[query].append("decomposable")

for q in queries:
    print("%d	%.0f	%.0f	%.0f"%(q,
      100*sum(1 if x=="decomposable" else 0 for x in method[q])/len(method[q]),
      100*sum(1 if x=="tree dec." else 0 for x in method[q])/len(method[q]),
      100*sum(1 if x=="d4" else 0 for x in method[q])/len(method[q])))
