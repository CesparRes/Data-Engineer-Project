from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

my_lufthansa_dag = DAG(
    dag_id="Lufthansa_scrape_dag",
    tags=['Datascientest','Lufthansa-Project'],
    schedule_interval='0 6 */1 * *',
    default_args={
        'owner': 'airflow',
        'start_date': days_ago(0, 1)
    },
    catchup=False
)


task1 = BashOperator(
    task_id="API_calls",
    bash_command="python3 ~/Lufthansa-Project/new_test.py > ~/Lufthansa-Project/all_airports.txt",
    dag=my_lufthansa_dag
)

task2 = BashOperator(
    task_id="Flatten",
    bash_command="python3 ~Lufthansa-Project/flatten_data.py",
    dag=my_lufthansa_dag
)

task3 = BashOperator(
    task_id="DB_insert",
    bash_command="mongoimport --db flight_info --collection flights --file ~/Lufthansa-Project/airports_parsed.txt --jsonArray",
    dag=my_lufthansa_dag
)

task1 >> task2
task2 >> task3
