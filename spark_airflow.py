from airflow import DAG
from airflow.operators.python import PythonOperator


def spark():
    pass


dag = DAG(
    dag_id="spark_submit_operator",
    schedule="0 1 * * *"
)

task = PythonOperator(
    task_id="spark_submit_task",
    python_callable=spark,
    dag=dag,
)

task