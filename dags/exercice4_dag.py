from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook
from datetime import datetime, timedelta
import pandas as pd

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}

# Tâche 1: Extraction CSV
def extract_csv_task(**kwargs):
    df = pd.read_csv('/opt/airflow/dags/data/customer_data.csv')
    temp_path = '/tmp/ex4_extracted_customers.csv'
    df.to_csv(temp_path, index=False)
    return temp_path  # Poussé dans XCom automatiquement

# Tâche 2: Extraction MySQL
def extract_mysql_task(**kwargs):
    mysql_hook = MySqlHook(mysql_conn_id='mysql_default')
    df = mysql_hook.get_pandas_df("SELECT customer_id, order_id, amount FROM orders")
    temp_path = '/tmp/ex4_extracted_orders.csv'
    df.to_csv(temp_path, index=False)
    return temp_path  # Poussé dans XCom

# Tâche 3: Transformation (Récupération des chemins via XCom)
def transform_task(**kwargs):
    ti = kwargs['ti']
    csv_path = ti.xcom_pull(task_ids='extract_csv')
    mysql_path = ti.xcom_pull(task_ids='extract_mysql')
    
    df_customers = pd.read_csv(csv_path)
    df_orders = pd.read_csv(mysql_path)
    
    df_merged = pd.merge(df_customers, df_orders, on='customer_id', how='inner')
    df_merged['total_amount'] = df_merged['amount'] * 1.20
    
    transformed_path = '/tmp/ex4_transformed_final.csv'
    df_merged.to_csv(transformed_path, index=False)
    return transformed_path  # Poussé dans XCom

# Tâche 4: Insertion (Récupération du chemin final via XCom)
def load_mysql_task(**kwargs):
    ti = kwargs['ti']
    transformed_path = ti.xcom_pull(task_ids='transform')
    
    df_final = pd.read_csv(transformed_path)
    mysql_hook = MySqlHook(mysql_conn_id='mysql_default')
    engine = mysql_hook.get_sqlalchemy_engine()
    
    df_final.to_sql('final_customer_orders_ex4', con=engine, if_exists='replace', index=False)
    print(f"{len(df_final)} lignes insérées dans MySQL.")

with DAG(
    'exercice4_xcom_paths',
    default_args=default_args,
    description='Ex 4 : Ajout de XCom pour gérer les chemins',
    schedule_interval=None,
    catchup=False,
    tags=['tp', 'exercice4', 'xcom'],
) as dag:

    t1 = PythonOperator(task_id='extract_csv', python_callable=extract_csv_task, provide_context=True)
    t2 = PythonOperator(task_id='extract_mysql', python_callable=extract_mysql_task, provide_context=True)
    t3 = PythonOperator(task_id='transform', python_callable=transform_task, provide_context=True)
    t4 = PythonOperator(task_id='load_mysql', python_callable=load_mysql_task, provide_context=True)

    [t1, t2] >> t3 >> t4