SELECT provsql.provenance() as provs from
    partsupp,
    supplier,
    nation
where
    ps_suppkey = s_suppkey
    and s_nationkey = n_nationkey
    and n_name = 'GERMANY'
    and ps_partkey%512=0
group by
    ps_partkey;