#!/usr/bin/env python3
import os
import subprocess
import time
import pandas as pd

# Folder containing your SQL files
sql_folder = 'prov_time'
provsql_tmp_file ='/var/lib/postgresql/14/main/provsql.tmp'

# Database connection details
db_user = 'senellar'
db_name = 'tpch'
db_password ='uH1riehi'

# Output file to save execution times
output_file = 'prov_time.txt'

# List of SQL files
sql_files = [f for f in os.listdir(sql_folder) if f.endswith('.sql')]

subprocess.run(["cp",provsql_tmp_file,"provsql.tmp"])

os.environ["PGPASSWORD"] = db_password

# Initialize or create the output file
with open(output_file, 'w') as f:
    f.write('SQL File Name,Execution Time (seconds)\n')

# Loop through the SQL files and execute them one by one
for sql_file in sql_files:
    print(sql_file)
    for i in range(20):
        start_time = time.time()
        command = f'psql -h localhost -U {db_user} -d {db_name} -a -f {os.path.join(sql_folder, sql_file)}'

        # Launch psql as a subprocess
        process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Communicate with the subprocess (execute SQL file)
        process.communicate()

        # Capture end time after communicating with the subprocess
        end_time = time.time()
        execution_time = end_time - start_time

        # Append execution time to the output file
        with open(output_file, 'a') as f:
            f.write(f'{sql_file},{execution_time}\n')

        # Reset ProvSQL circuit between each call to avoid
        # effects of past production of circuits
        subprocess.run(["service","postgresql","stop"])
        subprocess.run(["cp","provsql.tmp",provsql_tmp_file])
        subprocess.run(["service","postgresql","start"])

prov_time = pd.read_csv('prov_time.txt', delimiter=',')
prov_mean = prov_time.groupby(['SQL File Name'], as_index=False).mean()
prov_std = prov_time.groupby(['SQL File Name'], as_index=False).std()
prov_table = prov_mean.merge(prov_std, left_on= "SQL File Name", right_on="SQL File Name")
new_names = {
    'Execution Time (seconds)_x': 'mean',
    'Execution Time (seconds)_y': 'std'
}
prov_table = prov_table.rename(columns=new_names)
prov_table.to_csv('prov_time.csv')
