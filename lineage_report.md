# Milestone 3: Model Lineage & Selection Report

## 1. Experiment Comparison
Over the course of testing, 5+ MLflow runs were executed with varying hyperparameters. Below is a comparison of the key runs:

| Run Name | Hyperparameters | Accuracy | Data Hash (SHA256) | Registry Stage |
| :--- | :--- | :--- | :--- | :--- |
| **bittersweet-cat-202** | `n_estimators: 500` | **Highest** | `0104e9da8...` | **Production (Version 2)** |
| bedecked-frog-207 | `n_estimators: 500` | High | `0104e9da8...` | Staging |
| gentle-robin-329 | `n_estimators: 100` | Baseline | `0104e9da8...` | Archived |

## 2. Selection Justification
**Version 2 (`bittersweet-cat-202`)** was selected and automatically promoted to **Production** because it achieved the highest accuracy metric during validation. 
Increasing the `n_estimators` to 500 provided a measurable boost in performance over the baseline runs.

## 3. Lineage & Governance Assurances
* **Training Consistency**: As shown in the table, all runs share the exact same `data_hash`. This guarantees that the accuracy improvements are strictly due to hyperparameter tuning and not a change in the underlying training data.
* **Traceability**: The Production model is strictly linked to its original MLflow run ID and the Airflow DAG execution that triggered it. 

## 4. Identified Risks & Monitoring Needs
* **Data Drift**: The current model is highly optimized for the current `data_hash`. If real-world input data begins to drift, the accuracy will drop. 
* **Monitoring**: We must monitor real-time inference accuracy. If it drops below our 90% threshold, it should trigger a webhook to Airflow to automatically kick off a new `train_pipeline` run with fresh data.
