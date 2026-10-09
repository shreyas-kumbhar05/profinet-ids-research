# Isolation Forest — Study Notes

## Core Algorithm Concept

Isolation Forest is an unsupervised anomaly detection algorithm. It identifies unusual observations by checking how easily they can be separated from the rest of the data.

The main idea is that anomalies are often few and also different from normal observations. Randomly splitting the data isolate these observations in fewer steps.

For my PROFINET IDS project, the model will be trained using normal traffic features; Later, I will evaluate whether it can identify replay, spoof, and malformed traffic as anomalies.

Isolation Forest does not learn the names of the attack types. It only makes a distinction between normal observations and anomalies.

## `contamination` Parameter

The contamination() parameter helps determine the threshold used to classify observations as normal or anomalous.

For example, `contamination=0.05` specifies an expected outlier proportion of 5% for setting the decision threshold during fitting.

In this project, the model will be trained on normal traffic only. Therefore, this value does not mean that 5% of the complete labeled dataset contains attacks.

The parameter affects the threshold used for anomaly detection, so its value can influence the number of observations flagged as anomalous.

## `predict()` Output Convention

Scikit-learn's Isolation Forest returns:

- `+1` = normal observation (inlier)
- `-1` = anomalous observation (outlier)

My dataset uses these ground-truth labels:

- `0` = normal
- `1` = replay
- `2` = spoof
- `3` = malformed

Will map the model's output to a binary normal/anomaly decision for evaluation:

- Scikit-learn `+1` → normal (`0`)
- Scikit-learn `-1` → anomaly (`1`)

One thing to note: The resulting anomaly label `1` does not mean replay specifically. It means that the model identified the observation as anomalous. The original `attack_type` column will tell us which scenario the observation actually belongs to.

## `fit()` vs `fit_predict()`

- `fit(X)`: trains the model using the supplied feature data.
- `fit_predict(X)`: trains the model and returns predictions for the supplied data.
- `predict(X)`: uses an already-trained model to classify observations as normal or anomalous.

I will be using `fit()` to learn the structure of normal PROFINET traffic and then use the trained model to evaluate the labeled dataset.

## `decision_function()` vs `score_samples()`

`predict()`: gives a binary decision, but it does not tell us how unusual an observation is relative to other observations.

`decision_function(X)`: returns a continuous score. Higher values indicate more normal observations, while lower values indicate more anomalous observations. Negative values are classified as outliers under the fitted threshold.

`score_samples(X)` returns the underlying sample score, where lower values also indicate more abnormal observations.

`decision_function()` will be particularly useful for creating the ROC curve. Since I want higher scores to indicate greater suspicion,I can use the negative of the decision function as the anomaly score.

A continuous score allows to examine detection performance across different thresholds rather than relying on one binary prediction threshold.

## `random_state`

Isolation Forest uses random feature selections and random splits to construct its trees.

Setting a fixed integer, such as Example: `random_state=42`, makes these pseudorandom choices reproducible under comparable conditions.

This is important for this research because need to rerun experiments and obtain comparable results when evaluating metrics such as precision, recall, F1-score, and ROC-AUC.

## Paper Notes — Sections 1–3

### Key Insight: Few and Different

The idea behind Isolation Forest is that anomalies are often a minority of observations and have characteristics that differ from normal observations.

Because of these differences, they can often be isolated with fewer random splits.

For the IDS, an unfamiliar source MAC may make spoofed traffic easier to isolate because normal traffic uses the known baseline MAC address. However, detection is not guaranteed and must be tested experimentally.

### Path Length Concept

A path length is the number of splits required to isolate an observation in an isolation tree.

A short path means the observation was isolated quickly and may be anomalous. A longer path means more splits were needed, which can indicate that the observation resembles other observations.

Isolation Forest builds multiple trees and combines their results rather than relying on a single tree.

### Swamping and Masking

**Swamping:** Normal observations are incorrectly classified as anomalies. this would create false positives and unnecessary security alerts.

**Masking:** Anomalies are not detected because they resemble other observations or are difficult to isolate. This could cause attack traffic to be classified as normal, creating false negatives.

Both problems matter when evaluating the reliability of an Intrusion detection system.

### Difference from Distance-Based Methods

Distance-based methods examine how far an observation is from other observations.

Isolation Forest instead repeatedly partitions the feature space and examines how quickly an observation can be isolated.

It does not require explicit distance or density calculations. This provides a different approach to identifying unusual traffic.

## Connection to PROFINET IDS

The current dataset contains four features:

- `iat`: Inter-arrival time between consecutive PROFINET RT frames.
- `frame_size`: Captured Ethernet frame size in bytes.
- `src_mac_known`: Whether the source MAC belongs to the normal baseline.
- `payload_entropy`: Shannon entropy of the PROFINET IO data portion.

The frame size is almost always 60 bytes, and the payload entropy is 0 for essentially all observations in the current dataset. These features therefore provide little variation for distinguishing the present traffic scenarios.

The malformed attack changes the PROFINET FrameID, but FrameID is not currently included as a feature. Consequently, Isolation Forest cannot directly inspect the manipulated FrameID, although it may still detect differences in the other available features.

## End-of-Day Understanding

Isolation Forest learns the general structure of normal traffic and identifies unusual observations based on how easily they can be isolated. It produces binary anomaly predictions and continuous scores that can be used to evaluate detection performance.

My experiment will show which attack types the model detects and misses when evaluated against the labeled dataset. The results will help identify the limitations of the current features and model.
