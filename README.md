# MLOps Milestone 3: Automated ML Pipeline & Registry
**Author**: Om Jagtap

## Setup & Execution
1. **Environment**: Install dependencies using `pip install -r requirements.txt`.
2. **Start Services**: 
   - Start Airflow: `export AIRFLOW_HOME=$(pwd) && airflow standalone`
   - Start MLflow: `mlflow ui --host 0.0.0.0 --port 5000`
3. **Run Pipeline**: Open the Airflow UI at `localhost:8080`, unpause the `train_pipeline` DAG, and trigger a manual run.

## Architecture & Experiment Tracking
* **Pipeline Orchestration**: Airflow orchestrates three tasks: `preprocess_data` >> `train_model` >> `register_model`.
* **Experiment Tracking**: MLflow logs hyperparameters (like `n_estimators`), metrics (accuracy), and the unique `data_hash` for every run to ensure exact reproducibility.
* **Idempotency**: The Airflow DAG is idempotent. Re-running it will not crash the system; it simply logs a new run and creates a new model version in the MLflow Registry.
* **CI-Based Governance**: A threshold-based quality gate is implemented via GitHub Actions. If model accuracy falls below the set threshold, the CI pipeline fails, preventing poor models from merging.

## Operational Notes
* **Retry Strategies**: The DAG is configured with `retries: 2` and a `retry_delay` of 5 minutes to automatically recover from transient errors (like temporary port blocks or connection drops).
* **Rollback Procedures**: If a deployed model degrades in Production, an operator can go to the MLflow Registry UI, transition the current Production model to "Archived", and transition the previous stable version (e.g., Version 1) back to "Production".
* **Monitoring & Alerting**: Monitor the `data_hash` logged in MLflow. If data distribution shifts significantly, an alert should be triggered to retrain the model.
