Folder all_queries contain the queries and 
running them computes the circuit processing time and the shapley value computation time.
Before running them, change the result path in last line of every file.

Then run the file run_all.sql (change the path to files in it too).

After this is done, there will be result files in .csv format.
Run the time_processing.py file (change the folder path here. This would be same as that of the paths in the last
line of files in all_queries folder).

Run the prov_time.py file to generate the provenance computation time files. Change the database connection
details in it before running.