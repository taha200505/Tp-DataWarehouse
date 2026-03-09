# Compte Rendu - TP Apache Airflow
## Orchestration des Pipelines de Données ETL

---

**Étudiant :** Taha Jamali alaoui
**Date :** 8 Mars 2026  
**Sujet :** Atelier Apache Airflow - Pipeline ETL avec Docker  
**Professeur :** Fadwa Bouhafer

---

## Table des Matières

1. [Introduction](#introduction)
2. [Objectifs du TP](#objectifs-du-tp)
3. [Environnement Technique](#environnement-technique)
4. [Travail Réalisé](#travail-réalisé)
5. [Résultats Obtenus](#résultats-obtenus)
6. [Difficultés Rencontrées](#difficultés-rencontrées)
7. [Solutions Apportées](#solutions-apportées)
8. [Conclusion](#conclusion)
9. [Annexes](#annexes)

---

## 1. Introduction

Ce travail pratique vise à découvrir et mettre en œuvre Apache Airflow, une plateforme open-source d'orchestration de workflows de données. L'objectif principal est de créer un pipeline ETL (Extract, Transform, Load) simple pour traiter des données de ventes à partir d'un fichier CSV.

### Contexte
Apache Airflow, développé initialement par Airbnb en 2014, est devenu un standard de l'industrie pour l'orchestration de pipelines de données. Il permet de :
- Définir des workflows complexes sous forme de DAGs (Directed Acyclic Graphs)
- Planifier et surveiller l'exécution des tâches
- Gérer les dépendances entre tâches
- Offrir une interface web intuitive pour la supervision

---

## 2. Objectifs du TP

### Objectifs Principaux
1. **Installation d'Apache Airflow** via Docker Compose
2. **Configuration de l'environnement** avec :
   - PostgreSQL (base de données des métadonnées Airflow)
   - Redis (broker pour Celery)
   - MySQL (base de données cible pour le chargement des données)
3. **Création d'un pipeline ETL** comprenant :
   - **Extract** : Lecture d'un fichier CSV de données de ventes
   - **Transform** : Nettoyage (suppression des doublons) et calcul de la marge bénéficiaire
   - **Load** : Affichage/Chargement des résultats

### Objectifs Pédagogiques
- Comprendre l'architecture d'Airflow (Scheduler, Webserver, Worker, Executor)
- Maîtriser les concepts de DAG, Tasks et Operators
- Savoir déployer Airflow avec Docker
- Développer un pipeline ETL fonctionnel en Python

---

## 3. Environnement Technique

### Configuration Système
- **OS :** Linux (Ubuntu/Debian)
- **Docker :** Version installée
- **Docker Compose :** Version 2.x
- **Python :** 3.12 (dans les conteneurs Airflow)

### Architecture Docker Déployée

```yaml
Services déployés :
┌─────────────────────────────────────────────────────┐
│                  Airflow Webserver                  │
│              (Interface Web - Port 8080)            │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│               Airflow Scheduler                     │
│          (Orchestration des DAGs)                   │
└─────────────────────────────────────────────────────┘
                         ↓
┌──────────────┬──────────────┬──────────────────────┐
│   Worker     │  Triggerer   │      Redis           │
│  (Celery)    │              │  (Message Broker)    │
└──────────────┴──────────────┴──────────────────────┘
                         ↓
┌──────────────┬─────────────────────────────────────┐
│  PostgreSQL  │         MySQL                       │
│  (Metadata)  │    (Base de données cible)          │
└──────────────┴─────────────────────────────────────┘
```

### Composants Airflow

| Service | Rôle | Port |
|---------|------|------|
| **airflow-webserver** | Interface utilisateur web | 8080 |
| **airflow-scheduler** | Planification et orchestration des DAGs | - |
| **airflow-worker** | Exécution des tâches (CeleryExecutor) | - |
| **airflow-triggerer** | Gestion des déclencheurs asynchrones | - |
| **airflow-init** | Initialisation de la BD et création de l'utilisateur admin | - |
| **postgres** | Base de données des métadonnées Airflow | 5432 |
| **redis** | Message broker pour Celery | 6379 |
| **mysql** | Base de données cible pour le chargement des données | 3307 |

---

## 4. Travail Réalisé

### 4.1. Préparation de l'Environnement

#### Étape 1 : Configuration du fichier `.env`
Création du fichier d'environnement pour définir les variables nécessaires :

```bash
AIRFLOW_UID=1000
AIRFLOW_PROJ_DIR=.
```

#### Étape 2 : Fichier Docker Compose
Le fichier `docker-compose.yaml` a été configuré avec :
- Image Airflow : `apache/airflow:2.9.1`
- Executor : `CeleryExecutor` (distribution des tâches sur plusieurs workers)
- Bases de données : PostgreSQL 13 et MySQL 8.0
- Cache/Broker : Redis 7.2-bookworm

**Configuration clé :**
```yaml
x-airflow-common:
  image: apache/airflow:2.9.1
  environment:
    AIRFLOW__CORE__EXECUTOR: CeleryExecutor
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
    AIRFLOW__CELERY__RESULT_BACKEND: db+postgresql://airflow:airflow@postgres/airflow
    AIRFLOW__CELERY__BROKER_URL: redis://:@redis:6379/0
```

### 4.2. Installation et Démarrage

#### Commandes Exécutées

1. **Initialisation de la base de données Airflow :**
```bash
docker-compose up airflow-init
```

**Résultat :** 
- Création du schéma de base de données
- Migrations Alembic appliquées
- Création de l'utilisateur admin : `airflow/airflow`
- Exit code : 0 (succès)

2. **Démarrage des services :**
```bash
docker-compose up -d
```

**Résultat :**
- Téléchargement des images Docker
- Création du réseau `tp1_default`
- Création du volume `tp1_postgres-db-volume`
- Démarrage de tous les conteneurs

### 4.3. Problèmes Réseau Rencontrés

#### Erreur TLS Handshake Timeout
Lors du premier `docker-compose up`, une erreur est survenue :

```
Error response from daemon: failed to resolve reference 
"docker.io/apache/airflow:2.9.1": failed to do request: Head 
"https://registry-1.docker.io/v2/apache/airflow/manifests/2.9.1": 
net/http: TLS handshake timeout
```

**Cause :** Problème de connectivité réseau temporaire avec Docker Hub.

**Solution Appliquée :**
1. Nouvelle tentative de `docker-compose up -d` (retry)
2. Pull manuel des images critiques :
   ```bash
   docker pull apache/airflow:2.9.1
   docker pull postgres:13
   docker pull redis:7.2-bookworm
   docker pull mysql:8.0
   ```
3. Redémarrage complet avec `docker-compose down && docker-compose up -d`

**Résultat :** Toutes les images ont été téléchargées avec succès et les services ont démarré correctement.

### 4.4. Préparation des Données

#### Fichier CSV : `ventes.csv`

Contenu du fichier source :
```csv
product_id,product_name,revenue,cost
101,Produit A,1000,800
102,Produit B,2000,1500
103,Produit C,1500,1200
104,Produit D,3000,2500
105,Produit E,1800,1400
106,Produit F,NaN,900
107,Produit G,2200,1700
108,Produit H,2400,1900
109,Produit I,2800,2000
110,Produit J,3100,2700
```

**Observations :**
- 10 produits au total
- Présence d'une valeur `NaN` pour le Produit F (nécessite un nettoyage)
- Données en français (différent de l'exemple du TP en anglais)

---

## 5. Résultats Obtenus

### 5.1. État Final des Conteneurs

Tous les services Airflow sont opérationnels :

```
NAMES                     STATUS                   PORTS
tp1-airflow-worker-1      Up 6 minutes (healthy)   8080/tcp
tp1-airflow-webserver-1   Up 6 minutes (healthy)   0.0.0.0:8080->8080/tcp
tp1-airflow-scheduler-1   Up 5 minutes (healthy)   8080/tcp
tp1-airflow-triggerer-1   Up 6 minutes (healthy)   8080/tcp
tp1-postgres-1            Up 7 minutes (healthy)   5432/tcp
tp1-redis-1               Up 7 minutes (healthy)   6379/tcp
mysql_db_2                Up 7 minutes             0.0.0.0:3307->3306/tcp
```

**Statut : ✅ TOUS LES SERVICES SONT HEALTHY**

### 5.2. Vérification du Conteneur airflow-init

Le conteneur `tp1-airflow-init-1` affiche le statut `Exited (0)`, ce qui est **NORMAL et ATTENDU**.

**Explication :**
- C'est un conteneur d'initialisation (init container)
- Il s'exécute une seule fois au démarrage
- Il crée la structure de base de données et l'utilisateur admin
- Il se termine automatiquement avec un code de sortie 0 (succès)

**Logs de airflow-init :**
```
INFO  [alembic.runtime.migration] Running stamp_revision  -> 1949afb29106
[2026-03-06T22:29:52.327+0000] {override.py:1516} INFO - Added user airflow
User "airflow" created with role "Admin"
Database migrating done!
```

### 5.3. Accès à l'Interface Web

**URL :** http://localhost:8080  
**Identifiants :**
- **Username :** airflow
- **Password :** airflow

**Interface Disponible :** ✅ Accessible et fonctionnelle

### 5.4. Structure du Projet

```
TP1/
├── dags/                    (vide - à compléter avec les DAGs)
├── logs/                    (logs des exécutions Airflow)
├── plugins/                 (plugins personnalisés Airflow)
├── config/                  (configurations personnalisées)
├── mysql-data/              (données persistantes MySQL)
├── docker-compose.yaml      (configuration des services)
├── docker-compose.log       (logs du démarrage)
├── .env                     (variables d'environnement)
├── ventes.csv               (fichier de données source)
└── etl (1).pdf              (énoncé du TP)
```

---

## 6. Difficultés Rencontrées

### 6.1. Problème de Connectivité Docker Hub

**Symptôme :**
```
net/http: TLS handshake timeout
```

**Impact :** Échec du téléchargement de l'image `apache/airflow:2.9.1`

**Durée :** ~15 minutes de tentatives

### 6.2. Configuration AIRFLOW_UID

**Symptôme :**
```
WARN[0000] The "AIRFLOW_UID" variable is not set. Defaulting to a blank string.
```

**Impact :** Risque de problèmes de permissions sur les volumes montés

### 6.3. Compréhension du Statut du Conteneur Init

**Confusion initiale :** Le statut `Exited (0)` du conteneur `airflow-init` semblait indiquer un problème.

**Réalité :** C'est le comportement normal d'un init container.

---

## 7. Solutions Apportées

### 7.1. Résolution du Problème Réseau

**Actions entreprises :**
1. Nouvelle tentative immédiate (retry) → Succès partiel
2. Pull manuel des images critiques en arrière-plan
3. Utilisation de `timeout` pour éviter les blocages infinis
4. Redémarrage complet de la stack

**Résultat :** ✅ Toutes les images téléchargées avec succès

### 7.2. Configuration de l'UID

**Solution :**
Création du fichier `.env` avec :
```bash
AIRFLOW_UID=$(id -u)  # 1000
AIRFLOW_PROJ_DIR=.
```

**Résultat :** ✅ Plus d'avertissements sur les permissions

### 7.3. Documentation du Comportement Init

**Documentation ajoutée :**
- Le conteneur init est censé s'arrêter après l'initialisation
- Vérification des logs pour confirmer le succès (exit code 0)
- Explication du rôle des init containers dans l'architecture

---

## 8. Conclusion

### 8.1. Objectifs Atteints

✅ **Installation d'Apache Airflow avec Docker**
- Architecture multi-conteneurs fonctionnelle
- Tous les services opérationnels et healthy
- Interface web accessible

✅ **Configuration de l'Environnement**
- PostgreSQL : Métadonnées Airflow
- Redis : Message broker fonctionnel
- MySQL : Base de données cible prête
- Variables d'environnement configurées

⚠️ **Création du Pipeline ETL**
- **Partial** : Environnement prêt, données source disponibles
- **À compléter** : Création du DAG dans `/dags/etl_pipeline.py`

### 8.2. Compétences Acquises

1. **Docker & Orchestration**
   - Maîtrise de docker-compose pour des stacks complexes
   - Compréhension des dépendances entre services
   - Gestion des volumes et réseaux Docker

2. **Apache Airflow**
   - Architecture complète d'Airflow (Webserver, Scheduler, Worker, Executor)
   - Rôle de chaque composant
   - Processus d'initialisation et de configuration

3. **Résolution de Problèmes**
   - Diagnostic d'erreurs réseau
   - Lecture et interprétation des logs Docker
   - Stratégies de retry et de récupération

4. **Gestion de Données**
   - Préparation de données CSV pour ETL
   - Identification de problèmes de qualité (valeurs NaN)

### 8.3. Recommandations pour Amélioration

1. **Ajout de Monitoring**
   - Intégrer Prometheus/Grafana pour la surveillance
   - Configurer des alertes sur les échecs de DAGs

2. **Sécurité**
   - Changer les mots de passe par défaut
   - Utiliser des secrets Docker pour les credentials
   - Configurer HTTPS pour le webserver

3. **Optimisation**
   - Ajuster le nombre de workers selon la charge
   - Configurer le pool de connexions PostgreSQL
   - Optimiser les paramètres de retry

4. **Prochaines Étapes**
   - Implémenter le DAG ETL complet
   - Ajouter des tâches de validation de données
   - Créer des alertes par email en cas d'échec
   - Développer des DAGs plus complexes avec Sensors et Branching

### 8.4. Perspectives

Ce TP a permis de poser les fondations solides pour l'orchestration de pipelines de données avec Apache Airflow. L'environnement est maintenant prêt pour :
- Le développement de DAGs complexes
- L'intégration avec d'autres outils Big Data (Spark, Hadoop)
- Le déploiement en production avec des configurations adaptées
- L'expérimentation avec différents types d'Operators et d'Executors

Apache Airflow s'avère être un outil puissant et flexible pour l'automatisation et l'orchestration des workflows de données dans des environnements modernes de Data Engineering.

---

## 9. Annexes

### Annexe A : Commandes Docker Utiles

```bash
# Voir l'état des conteneurs
docker ps --format "table {{.Names}}\t{{.Status}}"

# Voir les logs d'un conteneur
docker logs tp1-airflow-scheduler-1 --tail 50

# Voir les logs en temps réel
docker-compose logs -f airflow-webserver

# Redémarrer un service
docker-compose restart airflow-scheduler

# Arrêter tous les services
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v

# Voir l'utilisation des ressources
docker stats

# Exécuter une commande dans un conteneur
docker exec -it tp1-airflow-scheduler-1 bash
```

### Annexe B : Vérification de la Santé des Services

```bash
# Vérifier PostgreSQL
docker exec -it tp1-postgres-1 pg_isready -U airflow

# Vérifier Redis
docker exec -it tp1-redis-1 redis-cli ping

# Vérifier MySQL
docker exec -it mysql_db_2 mysqladmin -u root -prootpassword ping

# Lister les DAGs disponibles
docker exec -it tp1-airflow-scheduler-1 airflow dags list
```

### Annexe C : Configuration Recommandée pour le DAG ETL

```python
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
```

### Annexe D : URLs et Accès

| Service | URL/Connexion | Identifiants |
|---------|---------------|--------------|
| Airflow Web UI | http://localhost:8080 | airflow / airflow |
| PostgreSQL | localhost:5432 | airflow / airflow |
| MySQL | localhost:3307 | airflow_user / airflow_password |
| Redis | localhost:6379 | (pas d'authentification) |

### Annexe E : Résolution de Problèmes Communs

| Problème | Solution |
|----------|----------|
| Conteneurs qui redémarrent en boucle | Vérifier les logs : `docker-compose logs` |
| Webserver inaccessible | Vérifier le port 8080 : `netstat -tulpn \| grep 8080` |
| DAG ne s'affiche pas | Vérifier les erreurs de syntaxe dans les logs scheduler |
| Base de données corrompue | `docker-compose down -v && docker-compose up -d` |
| Problème de permissions | Vérifier AIRFLOW_UID dans `.env` |

---

**Fin du Compte Rendu**

*Document généré le 8 Mars 2026*  
*Apache Airflow Version 2.9.1*  
*Docker Compose Version 2.x*
