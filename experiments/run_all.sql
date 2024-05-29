SET provsql.verbose_level=20;
DO $$ BEGIN RAISE NOTICE 'Query 3'; END $$;
\i all_queries/3.sql
DO $$ BEGIN RAISE NOTICE 'Query 5'; END $$;
\i all_queries/5.sql
DO $$ BEGIN RAISE NOTICE 'Query 7'; END $$;
\i all_queries/7.sql
DO $$ BEGIN RAISE NOTICE 'Query 10'; END $$;
\i all_queries/10.sql
DO $$ BEGIN RAISE NOTICE 'Query 11'; END $$;
\i all_queries/11.sql
DO $$ BEGIN RAISE NOTICE 'Query 16'; END $$;
\i all_queries/16.sql
DO $$ BEGIN RAISE NOTICE 'Query 18'; END $$;
\i all_queries/18.sql
DO $$ BEGIN RAISE NOTICE 'Query 19'; END $$;
\i all_queries/19.sql
