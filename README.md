# MLOps Milestone 3: Automated ML Pipeline & Model Registry
**Author**: Om Jagtap

---

## 🛠 Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone [https://github.com/Omjagtapp/ids568-milestone3-ojagt.git](https://github.com/Omjagtapp/ids568-milestone3-ojagt.git)
   cd ids568-milestone3-ojagt
   ```
2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. **Install all pinned dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Initialize the Airflow database**:
   ```bash
   export AIRFLOW_HOME=$(pwd)
   airflow db init
   ```

---

## 🚀 How to Run the Pipeline

1. **Start the MLflow Tracking Server**:
   Open a new terminal tab and run:
   ```bash
   mlflow ui --host 0.0.0.0 --port 5000
   ```
2. **Start Apache Airflow**:
   Open a separate terminal tab, set the home directory, and start the standalone server:
   ```bash
   export AIRFLOW_HOME=$(pwd)
   airflow standalone
   ```
3. **Execute the DAG**:
   Navigate to `http://localhost:8080` in your browser. Log in using the admin credentials generated in your terminal, unpause the `train_pipeline` DAG, and click **Trigger**.

---

## 🏗 Architecture Explanation

This pipeline is orchestrated to ensure reliable, reproducible machine learning operations:

| Component | Role in Pipeline |
| :--- | :--- |
| **Apache Airflow** | Orchestrates the Directed Acyclic Graph (DAG) consisting of data preprocessing, model training, and model registration. |
| **MLflow** | Serves as the experiment tracking backend and Model Registry. Manages stage transitions (None ➔ Staging ➔ Production). |
| **Scikit-Learn** | Used to train the core machine learning model (`iris-classifier`). |

---

## 🛡 DAG Idempotency and Lineage Guarantees

| Feature | Implementation | Guarantee |
| :--- | :--- | :--- |
| **Idempotency** | Tasks are stateless. Re-running the `train_pipeline` DAG will not overwrite existing production data or crash the system. | Generates a fresh MLflow run and registers a sequential, safe model version. |
| **Data Lineage** | Input data is hashed (SHA-256) before training. | A unique `data_hash` is logged as a tag in every MLflow run, proving exactly what data trained which model. |

---

## 🚦 CI-Based Model Governance Approach

Model governance is strictly enforced via GitHub Actions (`.github/workflows/train_and_validate.yml`):

* **Automated Testing**: Upon every code push, the CI pipeline automatically installs dependencies and executes the training script.
* **Quality Gate**: A threshold-based validation script (`model_validation.py`) queries the MLflow run metrics.
* **Failsafe**: If the model accuracy falls below the set threshold (e.g., 90%), the pipeline exits with a non-zero status code, deliberately failing the build to prevent degraded models from merging.

---

## 📊 Experiment Tracking Methodology

All experiments are tracked automatically using the `mlflow.start_run()` context manager:

| Tracking Category | Logged Elements | Method Used |
| :--- | :--- | :--- |
| **Parameters** | `n_estimators`, `max_depth` | `mlflow.log_param()` |
| **Metrics** | `accuracy`, `f1_score` | `mlflow.log_metric()` |
| **Artifacts** | `model.pkl`, `conda.yaml` | `mlflow.sklearn.log_model()` |
| **Metadata** | `data_hash` | `mlflow.set_tag()` |

---

## ⚙️ Operational Notes

### 1. Retry Strategies and Failure Handling
* **Retries**: Configured with `retries: 2` in Airflow's `default_args` to gracefully handle transient environment issues (like port `Errno 48` collisions).
* **Delay**: A `retry_delay` of 5 minutes allows system resources to clear before a task restarts.
* **Failure Alerts**: An `on_failure_callback` function is integrated to alert operators if a task completely exhausts its retry limits.

### 2. Monitoring and Alerting Recommendations
* **Data Drift Detection**: The logged `data_hash` must be monitored. If training data distributions shift significantly without a corresponding accuracy increase, an alert should trigger to investigate data drift.
* **Performance Monitoring**: Real-world inference metrics must be tracked. If live production accuracy drops below the validated CI/CD threshold, an alert should fire to trigger a pipeline re-run.

### 3. Rollback Procedures
If a newly promoted model (e.g., Version 2) exhibits performance degradation in the production environment, execute the following rollback:
1. Navigate to the **MLflow Model Registry UI**.
2. Select the problematic model (Version 2) and transition its stage from **Production** to **Archived**.
3. Select the previous stable version (Version 1) and transition its stage back to **Production**.
4. Operators can execute `git checkout [stable_tag]` to revert the entire Airflow codebase to the last known working state.
```
