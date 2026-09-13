# Network Traffic Anomaly Detection — Multi-Class IDS

A memory-optimized, multi-class Network Intrusion Detection System (IDS) trained on the **CIC-IDS-2017** dataset. The model uses a **Random Forest classifier** to distinguish benign traffic from 8 distinct attack types, achieving **>99% accuracy** across all classes.

## Overview

This project trains a supervised classifier on network flow features (packet lengths, timing, subflow statistics, etc.) to detect and categorize malicious traffic in real time. Rather than a binary benign/malicious split, the model performs **9-class classification**, identifying the specific attack family present in a given flow.

## Detected Classes

| Label | Class          |
|-------|----------------|
| 0     | BENIGN         |
| 1     | DDoS           |
| 2     | DoS GoldenEye  |
| 3     | DoS Hulk       |
| 4     | DoS Slowhttptest |
| 5     | DoS slowloris  |
| 6     | FTP-Patator    |
| 7     | PortScan       |
| 8     | SSH-Patator    |

## Model Details

- **Algorithm:** Random Forest (`sklearn.ensemble.RandomForestClassifier`)
- **Estimators:** 100 trees
- **Max features per split:** `sqrt`
- **Criterion:** Gini impurity
- **Random state:** 42 (for reproducibility)
- **Input features:** 77 network flow features
- **Serialized model size:** ~70 MB (`.pkl`, joblib/pickle format)

The model was tuned for a balance of accuracy and memory footprint, making it suitable for deployment in resource-constrained monitoring environments.

## Dataset

Trained on the [CIC-IDS-2017](https://www.unb.ca/cic/datasets/ids-2017.html) dataset, a widely used benchmark for network intrusion detection containing labeled benign and attack traffic captured over five days, including DoS, DDoS, brute-force, and port scan attacks. The full dataset contains roughly **2.5 million labeled flow records**.

A **5,000-row sample** (`sample_traffic.csv`) of the original data is included in this repo so you can quickly test the model and `predict.py` without downloading the full 2.5M-row dataset.

## Performance

### Classification Report

| Class | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| BENIGN | 1.00 | 1.00 | 1.00 | 429,380 |
| DDoS | 1.00 | 1.00 | 1.00 | 25,603 |
| DoS GoldenEye | 1.00 | 1.00 | 1.00 | 2,057 |
| DoS Hulk | 1.00 | 1.00 | 1.00 | 34,569 |
| DoS Slowhttptest | 0.96 | 0.99 | 0.97 | 1,046 |
| DoS slowloris | 1.00 | 0.99 | 1.00 | 1,077 |
| FTP-Patator | 1.00 | 1.00 | 1.00 | 1,186 |
| PortScan | 0.99 | 1.00 | 0.99 | 18,139 |
| SSH-Patator | 1.00 | 0.99 | 1.00 | 644 |
| **Accuracy** | | | **1.00** | 513,701 |
| **Macro avg** | 0.99 | 1.00 | 0.99 | 513,701 |
| **Weighted avg** | 1.00 | 1.00 | 1.00 | 513,701 |

- **Overall accuracy:** ~99.9%
- **Multi-Class ROC AUC Score:** 0.9998

### Confusion Matrix

![Confusion Matrix](confusion_matrix.png)

Nearly all predictions land on the diagonal. The small amount of confusion that does occur is concentrated around BENIGN traffic being misclassified as PortScan or vice versa, and minor overlap between similar DoS variants (e.g., DoS Hulk / DoS GoldenEye) — consistent with the underlying similarity of those attack patterns at the flow-feature level.

## Feature Importance

![Top 20 Feature Importances](feature_importance.png)

The most predictive features are almost entirely derived from **packet size statistics** rather than timing or flag counts:

1. **Bwd Packet Length Std** — variability in backward (server→client) packet sizes
2. **Packet Length Variance**
3. **Packet Length Std**
4. **Bwd Packet Length Mean**
5. **Subflow Bwd Bytes**

This makes intuitive sense: many attack types (e.g., floods, brute-force tools) generate traffic with highly regular or unusually uniform packet sizes, whereas benign traffic shows more natural variability.

## Repository Structure

```
├── network_anomaly.ipynb              # Training notebook (data prep, training, evaluation)
├── network_traffic_anomaly_detection.pkl  # Trained Random Forest model
├── predict.py                         # Script to run inference on new/sample data
├── sample_traffic.csv                 # 5,000-row sample of the CIC-IDS-2017 dataset
├── confusion_matrix.png
├── feature_importance.png
├── requirements.txt
├── LICENSE
└── README.md
```

## Usage

### Quick start with the sample data

```bash
python predict.py
```
This runs the trained model against `sample_traffic.csv` (5,000 rows sampled from the original 2.5M-row dataset) and prints predictions out of the box — no need to download the full CIC-IDS-2017 dataset just to try the model.

### Using the model directly

```python
import pickle
import pandas as pd

# Load the trained model
with open("network_traffic_anomaly_detection.pkl", "rb") as f:
    model = pickle.load(f)

# X should contain the same 77 features used during training,
# in the same column order
predictions = model.predict(X)
probabilities = model.predict_proba(X)
```

> **Note:** The model expects preprocessed flow-level features matching the CIC-IDS-2017 feature schema (e.g., CICFlowMeter output). Ensure feature engineering/scaling matches the training pipeline before inference.

## Requirements

- Python 3.8+
- scikit-learn, pandas, numpy, scipy, matplotlib, seaborn, joblib

Install everything with:
```bash
pip install -r requirements.txt
```

> The model was serialized with a newer version of scikit-learn than some environments may have installed. If you see an `InconsistentVersionWarning` on load, consider matching your scikit-learn version to the one used for training, or re-serializing the model in your target environment.

## Limitations

- Trained and evaluated on CIC-IDS-2017; performance on live/production traffic or other datasets may differ due to distribution shift.
- Minority classes (e.g., DoS Slowhttptest, SSH-Patator) have far fewer training examples than BENIGN or DDoS, so metrics on those classes are more sensitive to small sample effects.
- As with any supervised IDS, the model can only detect attack patterns represented in its training data and may not generalize to novel or adversarially evasive traffic.

## License

This project is licensed under the [MIT License](LICENSE) — free to use, modify, and distribute, including for commercial purposes, with attribution.

Note: the MIT license covers the code and model in this repository. The underlying **CIC-IDS-2017 dataset** has its own usage terms set by the Canadian Institute for Cybersecurity — see the [dataset page](https://www.unb.ca/cic/datasets/ids-2017.html) for citation requirements if you use it in your own work.
