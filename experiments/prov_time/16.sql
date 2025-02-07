SELECT provsql.provenance() as provs from
    partsupp,
    part,
    supplier
where
    p_partkey = ps_partkey
    and ps_suppkey = s_suppkey
    and p_brand <> 'Brand#45'
    and p_type not like 'MEDIUM POLISHED%'
    and p_size in (49, 14, 23, 45, 19, 3, 36, 9)
    and s_comment not like '%Customer%Complaints%'
    and p_partkey%64=0
group by
    p_brand,
    p_type,
    p_size;