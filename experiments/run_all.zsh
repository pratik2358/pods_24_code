#!/bin/zsh
sudo ./prov_time.py
rm -rf results results_banzhaf results_random results_banzhaf_random *.log
mkdir results results_banzhaf results_random results_banzhaf_random
echo 'select provsql.set_prob(provsql.provenance(),1.) from (select 1 from customer union all select 1 from lineitem union all select 1 from nation union all select 1 from orders union all select 1 from part union all select 1 from partsupp union all select 1 from region union all select 1 from supplier) t;' | psql tpch &> set_to_1.log
for i (`seq -w 1 20`); psql tpch < run_all.sql &>! shapley_$i.log && mkdir results/$i && mv results/*.csv results/$i
for i (`seq -w 1 20`); psql tpch < run_all_banzhaf.sql &>! banzhaf_$i.log && mkdir results_banzhaf/$i && mv results_banzhaf/*.csv results_banzhaf/$i
echo 'select provsql.set_prob(provsql.provenance(),random()) from (select 1 from customer union all select 1 from lineitem union all select 1 from nation union all select 1 from orders union all select 1 from part union all select 1 from partsupp union all select 1 from region union all select 1 from supplier) t;' | psql tpch &> set_to_random.log
for i (`seq -w 1 20`); psql tpch < run_all.sql &>! shapley_random_$i.log && mkdir results_random/$i && mv results/*.csv results_random/$i
for i (`seq -w 1 20`); psql tpch < run_all_banzhaf.sql &>! banzhaf_random_$i.log && mkdir results_banzhaf_random/$i && mv results_banzhaf/*.csv results_banzhaf_random/$i
