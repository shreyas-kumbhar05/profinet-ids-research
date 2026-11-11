
## Isolation Forest
Contains the trained Isolation forest model which can detect anomalies in traffic by being trained on normal PROFINET traffic.

## Methodology

The Isolation forest algorithm randomly separates the observations based on their features. If they can be separated quickly, then they are more likely to be an anomaly.

The model was trained using only normal samples from `dataset/labeled_dataset.csv`. This means it will not detect any specific type of attack, just whether traffic looks normal or not.

## Input Features

These are the 4 features taken from PROFINET traffic:

- **iat:** Time between two consecutive frames.
- **frame_size:** Size in bytes of the ethernet frame.
- **src_mac_known:** Boolean value if the source MAC address is known from the normal baseline.
- **payload_entropy:** Shannon entropy of the PROFINET IO data.

The label and attack_type columns are not used, as they are the answers.

## Files

- **train.py:** Script to load the dataset, select the normal samples and train the isolation forest model.
- **saved_model.pkl:** This is the trained model from the train.py script which can easily be loaded.


## Model Training
The model was trained using **contamination=0.05** and **random_state=42.**

- The contamination is used by Scikit Learn to set the decision threshold.
- The random state is fixed to 42 to make sure results are repeatable.


To train the model please go to the root of the repo and run the following command:

`python3 models/isolation_forest/train.py`

The script will load `dataset/labeled_dataset.csv` and save the model to `models/isolation_forest/saved_model.pkl`

## Limitations
- Some current features provide limited variation in the captured dataset. Also, the frame size is always 60 bytes.
- Malformed traffic changes the PROFINET FrameID; however this is not a feature in the model.
