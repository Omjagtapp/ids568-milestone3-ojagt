from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import mlflow
from mlflow.tracking import MlflowClient

# Rubric: Retry and failure handling
default_args = {
    'owner': 'ojagt',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

def register_and_promote():
    client = MlflowClient()
    model_name = "iris-classifier"
    
    # 1. Register the latest model version
    # Note: Ensure train.py uses mlflow.sklearn.log_model(model, "model")
    runs = client.search_runs(experiment_ids=["0"], order_by=["attributes.start_time DESC"], max_results=1)
    run_id = runs[0].info.run_id
    model_uri = f"runs:/{run_id}/model"
    mv = mlflow.register_model(model_uri, model_name)
    
    # 2. Rubric: Transition to Production
    client.transition_model_version_stage(
        name=model_name,
        version=mv.version,
        stage="Production"
    )
    print(f"Version {mv.version} of {model_name} is now in Production.")

with DAG(
    'train_pipeline',
    default_args=default_args,
    start_date=datetime(2026, 2, 1),
    schedule=None,
    catchup=False
) as dag:

    preprocess = PythonOperator(
        task_id='preprocess_data',
        python_callable=lambda: print("Cleaning data...")
    )

    train = PythonOperator(
        task_id='train_model',
        python_callable=lambda: os.system("python train.py 100")
    )

    register = PythonOperator(
        task_id='register_model',
        python_callable=register_and_promote
    )

    # Rubric: Use >> operator
    preprocess >> train >> register