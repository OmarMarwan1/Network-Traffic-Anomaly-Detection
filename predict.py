import pandas as pd
import pickle

print("1. Loading the Random Forest model...")
# Using the exact 69MB model file from your screenshot
with open("network_traffic_anomaly_detection.pkl", "rb") as file:
    model = pickle.load(file)

print("2. Loading the sample network traffic...")
data = pd.read_csv("sample_traffic.csv")

print("3. Cleaning data...")
# Drop the exact same columns you dropped during training
columns_to_drop = ['Label', 'day', 'Destination Port']
X_new = data.drop(columns=[col for col in columns_to_drop if col in data.columns])

# Add predictions to the dataframe and print the first 15 results
data['Predicted_Attack'] = predictions
print("4. Scanning traffic for attacks...")
predictions = model.predict(X_new)

# Add predictions to the dataframe
data['Predicted_Attack'] = predictions

    # Create a dictionary to map the numbers back to the attack names
    # (Update this list if your specific label encoder assigned different numbers to other attacks)
attack_mapping = {
        0: "BENIGN",
        1: "DDoS",
        2: "DoS GoldenEye",
        3: "DoS Hulk",
        4: "DoS Slowhttptest",
        5: "DoS slowloris",
        6: "FTP-Patator",
        7: "PortScan",
        8: "SSH-Patator" 
    }
    
    # Apply the mapping to the column
data['Predicted_Attack'] = data['Predicted_Attack'].map(attack_mapping)

print("\n--- Scan Complete. Top 15 Results ---")
print(data[['Label', 'Predicted_Attack']].value_counts())