from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import json

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}

# Tâche 1: Extraction et envoi via XCom
def extract_and_push(**kwargs):
    source_path = '/opt/airflow/dags/data/weather_data.csv'
    df = pd.read_csv(source_path)
    df.columns = df.columns.str.replace(' ', '_')
    
    # Conversion du DataFrame en dictionnaire pour qu'il soit sérialisable en JSON par XCom
    data_dict = df.to_dict(orient='records')
    return data_dict  # Airflow va automatiquement pousser ce retour dans XCom

# Tâche 2: Transformation avec données de XCom
def transform_from_xcom(**kwargs):
    ti = kwargs['ti']
    # Récupération des données depuis XCom
    raw_data = ti.xcom_pull(task_ids='extract_csv')
    
    df = pd.DataFrame(raw_data)
    
    # Nettoyage et filtre (ex: température > 25)
    df_clean = df.dropna()
    df_filtered = df_clean[df_clean['temperature'] > 25]
    
    # Renvoi des données filtrées via XCom
    return df_filtered.to_dict(orient='records')

# Tâche 3: Sauvegarde avec données de XCom
def save_from_xcom(**kwargs):
    ti = kwargs['ti']
    transformed_data = ti.xcom_pull(task_ids='transform_data')
    
    df = pd.DataFrame(transformed_data)
    final_path = '/tmp/final_filtered_weather.json'
    df.to_json(final_path, orient='records', indent=4)
    print(f"Données finales (temp > 25) sauvegardées dans {final_path}")

with DAG(
    'exercice2_xcom_data',
    default_args=default_args,
    description='Ex 2 : Utilisation de XCom pour échanger les données',
    schedule_interval=None,
    catchup=False,
    tags=['tp', 'exercice2', 'xcom'],
) as dag:

    t1 = PythonOperator(task_id='extract_csv', python_callable=extract_and_push, provide_context=True)
    t2 = PythonOperator(task_id='transform_data', python_callable=transform_from_xcom, provide_context=True)
    t3 = PythonOperator(task_id='save_data', python_callable=save_from_xcom, provide_context=True)

    t1 >> t2 >> t3