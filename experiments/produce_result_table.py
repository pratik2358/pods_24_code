#!/usr/bin/env python3

import glob
import csv
import re
import pandas
from statistics import mean, stdev

results_dir = ["results","results_random","results_banzhaf","results_banzhaf_random"]
shapley_log = "shapley_01.log"
provenance_results = "prov_time.csv"

queries = sorted([10,11,16,18,19,3,5,7])

prov_time = dict()

with open(provenance_results, mode='r') as infile:
    reader = csv.reader(infile)
    next(reader)
    for row in reader:
        prov_time[int(row[1].replace('.sql',''))]=(float(row[2]),float(row[3]))

method=dict()
gates=dict()

with open(shapley_log, "r") as log:
    for line in log:
        if "NOTICE:" in line and "gates" in line:
            query = int(re.sub(r".*/(.*)\.sql:.* NOTICE.*","\\1", line))
            g = int(re.sub(r".* ([\d]+) gates", "\\1", line))
            if query not in gates:
                gates[query]=[]
            gates[query].append(g)

            if "d4" in line:
                method[query]="d4"
            elif "tree decomposition" in line and (query not in method or
                                                method[query] != 'd4'):
                method[query]="tree dec."
            elif "interpreted as dD" in line and query not in method:
                method[query]="d-D"

for q in queries:
    print(q, end='&')

    (pt_mean,pt_std)=prov_time[q]
    print("$%.3f \\pm %.3f$"%(pt_mean, pt_std), end='&')

    ckt_times=[]
    results_times=dict()

    for d in results_dir:
        results_times[d]=[]

        for f in glob.glob(d+"/*/"+str(q)+".csv"):
            c = pandas.read_csv(f)
            if "banzhaf" in d:
                key="banzhaf_tuple"
            else:
                key="shapley_tuple"
            c[key] = c[key].str.strip('()[]""')
            c[['tuple1','tuple2','value','ckt_time', 'value_time']] = c[key].str.split(',', expand=True)
            c['value'] = c['value'].astype(float)
            c['ckt_time'] = c['ckt_time'].astype(float)
            c['value_time'] = c['value_time'].astype(float)
            group = c[['tuple1', 'ckt_time']].groupby('tuple1')
            ckt_time = sum(group.mean()['ckt_time'])
            value_time = sum(c["value_time"].astype('float'))
            if d == 'results':
                ckt_times.append(ckt_time)
            results_times[d].append(value_time)

    print("$%.3f \\pm %.3f$"%(mean(ckt_times),stdev(ckt_times)), end='&')

    print("%s&%d"%(method[q],round(mean(gates[q]))), end='')

    for d in results_dir:
        print("&$%.3f \\pm %.3f$"%(mean(results_times[d]),stdev(results_times[d])),end='')

    print('\\\\')
