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

# Tâche 1: Extraction CSV (Chemin statique)
def extract_csv():
    df = pd.read_csv('/opt/airflow/dags/data/customer_data.csv')
    df.to_csv('/tmp/ex3_customers.csv', index=False)
    print("Données clients extraites et sauvegardées.")

# Tâche 2: Extraction MySQL (Chemin statique)
def extract_mysql():
    mysql_hook = MySqlHook(mysql_conn_id='mysql_default')
    sql = "SELECT customer_id, order_id, amount FROM orders"
    df = mysql_hook.get_pandas_df(sql)
    df.to_csv('/tmp/ex3_orders.csv', index=False)
    print("Données commandes extraites et sauvegardées.")

# Tâche 3: Transformation
def transform():
    df_customers = pd.read_csv('/tmp/ex3_customers.csv')
    df_orders = pd.read_csv('/tmp/ex3_orders.csv')
    
    # Fusion sur customer_id
    df_merged = pd.merge(df_customers, df_orders, on='customer_id', how='inner')
    
    # Colonne calculée
    df_merged['total_amount'] = df_merged['amount'] * 1.20
    
    df_merged.to_csv('/tmp/ex3_final_data.csv', index=False)
    print("Fusion et calculs terminés.")

# Tâche 4: Insertion dans MySQL
def load_mysql():
    df_final = pd.read_csv('/tmp/ex3_final_data.csv')
    mysql_hook = MySqlHook(mysql_conn_id='mysql_default')
    engine = mysql_hook.get_sqlalchemy_engine()
    
    df_final.to_sql('final_customer_orders_ex3', con=engine, if_exists='replace', index=False)
    print("Données insérées dans MySQL avec succès.")

with DAG(
    'exercice3_merge_csv_mysql',
    default_args=default_args,
    description='Ex 3 : Fusionner CSV et MySQL sans XCom',
    schedule_interval=None,
    catchup=False,
    tags=['tp', 'exercice3'],
) as dag:

    t1 = PythonOperator(task_id='extract_csv', python_callable=extract_csv)
    t2 = PythonOperator(task_id='extract_mysql', python_callable=extract_mysql)
    t3 = PythonOperator(task_id='transform', python_callable=transform)
    t4 = PythonOperator(task_id='load_mysql', python_callable=load_mysql)

    [t1, t2] >> t3 >> t4