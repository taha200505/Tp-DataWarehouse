from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 3, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def extract_and_transform():
    # Extraction
    data = pd.read_csv('/opt/airflow/dags/ventes.csv')
    
    # Transformation
    data = data.dropna()  # Supprimer les valeurs NaN
    data = data.drop_duplicates()  # Supprimer les doublons
    
    # Calculer la marge bénéficiaire
    data['profit_margin'] = (data['revenue'] - data['cost']) / data['revenue']
    data['profit_margin_pct'] = (data['profit_margin'] * 100).round(2)
    
    print("Données transformées :")
    print(data)
    
    # Sauvegarde pour la tâche suivante
    data.to_csv('/opt/airflow/dags/ventes_transformed.csv', index=False)
    
    return len(data)

with DAG(
    'etl_pipeline_ventes',
    default_args=default_args,
    description='Pipeline ETL pour les données de ventes',
    schedule_interval='@daily',
    catchup=False,
    tags=['etl', 'ventes', 'tp'],
) as dag:
    
    task_etl = PythonOperator(
        task_id='extract_transform_load',
        python_callable=extract_and_transform,
    )
    
    task_etl