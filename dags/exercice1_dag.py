from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import os

# Paramètres par défaut
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Tâche 1: Extraction
def extract_data():
    source_path = '/opt/airflow/dags/data/weather_data.csv'
    df = pd.read_csv(source_path)
    # Nettoyage des noms de colonnes pour éviter les problèmes avec les espaces
    df.columns = df.columns.str.replace(' ', '_')
    df.to_csv('/tmp/raw_weather.csv', index=False)
    print(f"Extraction terminée. {len(df)} lignes lues.")

# Tâche 2: Transformation
def transform_data():
    df = pd.read_csv('/tmp/raw_weather.csv')
    
    # Nettoyer les valeurs nulles
    df_clean = df.dropna()
    
    # Ajouter une colonne calculée (feels_like_temp)
    # Formule simplifiée pour l'exemple
    df_clean['feels_like_temp'] = df_clean['temperature'] - (df_clean['wind_speed'] * 0.1)
    
    df_clean.to_csv('/tmp/transformed_weather.csv', index=False)
    print(f"Transformation terminée. {len(df_clean)} lignes conservées.")

# Tâche 3: Sauvegarde
def save_data():
    df = pd.read_csv('/tmp/transformed_weather.csv')
    final_path = '/tmp/final_weather_data.csv'
    df.to_csv(final_path, index=False)
    print(f"Sauvegarde réussie dans : {final_path}")

# Définition du DAG
with DAG(
    'exercice1_weather_etl',
    default_args=default_args,
    description='Ex 1 : Charger, Transformer et Sauvegarder',
    schedule_interval=None,
    catchup=False,
    tags=['tp', 'exercice1'],
) as dag:

    t1 = PythonOperator(task_id='extract', python_callable=extract_data)
    t2 = PythonOperator(task_id='transform', python_callable=transform_data)
    t3 = PythonOperator(task_id='save', python_callable=save_data)

    t1 >> t2 >> t3