DROP TABLE IF EXISTS banzhaf_results;

CREATE TABLE banzhaf_results (
    banzhaf_tuple JSONB
);


DO $$
DECLARE
    row_record RECORD;
    result TEXT;
BEGIN
    FOR row_record IN
            SELECT provsql.provenance() as provs from
            customer,
            orders,
            lineitem,
            supplier,
            nation,
            region
        where
            c_custkey = o_custkey
            and l_orderkey = o_orderkey
            and l_suppkey = s_suppkey
            and c_nationkey = s_nationkey
            and s_nationkey = n_nationkey
            and n_regionkey = r_regionkey
            and r_name = 'ASIA'
            and o_orderdate >= date '1994-01-01'
            and o_orderdate < date '1994-01-01' + interval '1' year
            and l_partkey%56=0
        group by
            n_name

    LOOP
        FOR result IN
            SELECT CONCAT(row_record.provs::text,',',provsql.banzhaf_all_vars(row_record.provs)::text)
        LOOP
            INSERT INTO banzhaf_results(banzhaf_tuple)
            VALUES (to_jsonb(result));

        END LOOP;
    END LOOP;
END $$;

\COPY banzhaf_results TO '/home/senellar/git/students/pratik/prob_data_shap/experiments/results_banzhaf/5.csv' WITH CSV HEADER;
