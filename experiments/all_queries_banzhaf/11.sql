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
            partsupp,
            supplier,
            nation
        where
            ps_suppkey = s_suppkey
            and s_nationkey = n_nationkey
            and n_name = 'GERMANY'
            and ps_partkey%512=0
        group by
            ps_partkey

    LOOP
        FOR result IN
            SELECT CONCAT(row_record.provs::text,',',provsql.banzhaf_all_vars(row_record.provs)::text)
        LOOP
            INSERT INTO banzhaf_results(banzhaf_tuple)
            VALUES (to_jsonb(result));

        END LOOP;
    END LOOP;
END $$;

\COPY banzhaf_results TO '/home/senellar/git/students/pratik/prob_data_shap/experiments/results_banzhaf/11.csv' WITH CSV HEADER;
