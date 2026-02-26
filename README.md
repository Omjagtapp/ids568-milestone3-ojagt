Markdown
# MLOps Milestone 3: Automated ML Pipeline & Model Registry
**Author**: Om Jagtap

## Setup Instructions
1. Clone the repository to your local machine.
2. Ensure Python 3.9+ is installed.
3. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate
Install all pinned dependencies:

Bash
pip install -r requirements.txt
Initialize the Airflow database:

Bash
export AIRFLOW_HOME=$(pwd)
airflow db init
How to Run the Pipeline
Start the MLflow Tracking Server:
Open a terminal and run:

Bash
mlflow ui --host 0.0.0.0 --port 5000
Start Airflow:
Open a separate terminal, set the Airflow home directory, and start the standalone server:

Bash
export AIRFLOW_HOME=$(pwd)
airflow standalone
Execute:
Navigate to http://localhost:8080, log in using the generated admin credentials, unpause the train_pipeline DAG, and click the "Trigger" button.

Architecture Explanation
This project implements an automated Machine Learning Operations (MLOps) pipeline using:

Apache Airflow: Acts as the orchestrator, executing the Directed Acyclic Graph (DAG) which consists of data preprocessing, model training, and model registration.

MLflow: Serves as the experiment tracking backend and Model Registry. It logs all hyperparameters, metrics, and artifacts, and handles the staging transitions (None -> Staging -> Production).

Scikit-Learn: Used to train the core machine learning model (iris-classifier).

DAG Idempotency and Lineage Guarantees
Idempotency: The Airflow tasks are designed to be fully idempotent. Re-running the train_pipeline DAG will not overwrite existing production data or cause system crashes. Instead, it generates a fresh MLflow run and registers a sequential model version (e.g., Version 1, Version 2) in the registry.

Lineage Guarantees: Complete data and code lineage is maintained by hashing the input dataset. A unique data_hash (SHA256) is logged as a tag in every MLflow run, ensuring the exact data used for any model version can be traced and verified.

CI-Based Model Governance Approach
Model governance is enforced via GitHub Actions (.github/workflows/train_and_validate.yml).

Upon every push, the CI pipeline installs dependencies and executes the training script.

A quality gate is enforced via model_validation.py. The script queries the MLflow run and checks the accuracy metric against a strict threshold (e.g., 90%).

If the metric falls below the threshold, the pipeline exits with a non-zero status code, failing the build and preventing performance regressions from merging into the main branch.

Experiment Tracking Methodology
Experiments are tracked using the mlflow.start_run() context manager.

Parameters: Key hyperparameters like n_estimators are logged using mlflow.log_param().

Metrics: Evaluation metrics such as accuracy are logged using mlflow.log_metric().

Artifacts: The serialized model (model.pkl) and the conda.yaml environments are logged automatically using mlflow.sklearn.log_model().

Operational Notes
Retry Strategies and Failure Handling
The Airflow DAG defines a strict retry policy in its default_args.

Retries: Configured with retries: 2 to gracefully handle transient environment issues, such as temporary port binding errors (Errno 48).

Delay: A retry_delay of 5 minutes allows system resources to clear before a task restarts.

Failure Handling: An on_failure_callback function is integrated to alert operators via logs if a task completely exhausts its retry limits.

Monitoring and Alerting Recommendations
Data Drift Detection: The data_hash should be monitored continuously. If the training data distribution changes significantly without a corresponding increase in model accuracy, an alert should be triggered to investigate data drift.

Performance Monitoring: Real-world inference metrics should be tracked. If live accuracy drops below the validated CI/CD threshold, an alert should fire to trigger a pipeline re-run with fresh data.

Rollback Procedures
If a newly promoted model (e.g., Version 2) exhibits performance degradation in the production environment:

Navigate to the MLflow Model Registry UI.

Select the problematic model (Version 2) and transition its stage from Production to Archived.

Select the previous stable version (Version 1) and transition its stage back to Production.

Since the code is version-controlled via Git tags, operators can also run git checkout [stable_tag] to revert the entire pipeline codebase to the last known working state.


---

**Would you like me to also provide the exact contents for the `.github/workflows/train_and_validate.yml` file so you can secure the final points for Part 2 of the rubric?**
