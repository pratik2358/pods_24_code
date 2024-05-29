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
            lineitem
        where
            c_custkey = o_custkey
            and o_orderkey = l_orderkey
            and l_partkey%64=0
        group by
            c_name,
            c_custkey,
            o_orderkey,
            o_orderdate,
            o_totalprice

    LOOP
        FOR result IN
            SELECT CONCAT(row_record.provs::text,',',provsql.banzhaf_all_vars(row_record.provs)::text)
        LOOP
            INSERT INTO banzhaf_results(banzhaf_tuple)
            VALUES (to_jsonb(result));

        END LOOP;
    END LOOP;
END $$;

\COPY banzhaf_results TO '/home/senellar/git/students/pratik/prob_data_shap/experiments/results_banzhaf/18.csv' WITH CSV HEADER;
