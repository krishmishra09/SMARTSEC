# train_signature_detector.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import numpy as np

import pandas as pd
import glob

# Path to your CSV files
files = glob.glob("C:/Users/kr716/Downloads/archive/*.csv")   # all CSVs in "data" folder

# Read and combine them
df = pd.concat((pd.read_csv(f) for f in files), ignore_index=True)

# Save into one CSV
df.to_csv("merged_train.csv", index=False)


# Use the full CIC-IDS2017 dataset (MachineLearningCSV.zip)
print("Loading CIC-IDS2017 dataset...")
try:
    # Assuming you have combined the CSV files from the dataset
    df = pd.read_csv('merged_train.csv')
except FileNotFoundError:
    print("Error: 'all_cicids2017_data.csv' not found. Please download and combine the CIC-IDS2017 CSV files.")
    exit()

# Preprocessing
df.columns = df.columns.str.strip()
df.replace([np.inf, -np.inf], np.nan, inplace=True)
#this df.replace ->with the help of numpy array assign negative and positive infinite vaule to NAN(not a number)
df.dropna(inplace=True)

X = df.drop(['Label'], axis=1)
#X holds all columns except the 'Label' column. these are the input features and label is the output column so x drops label since it contains output 
y = df['Label']
#y only holds label column i.e output

# Encode labels (e.g., 'BENIGN' -> 0, 'DDoS' -> 1, etc.)
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# For demonstration, we'll use a subset of features. A real implementation would involve feature selection.
features_to_use = [col for col in X.columns if X[col].dtype!= 'object'][:40] # Use first 40 numeric features
X_numeric = X[features_to_use]

X_train, X_test, y_train, y_test = train_test_split(X_numeric, y_encoded, test_size=0.3, random_state=42)
#The train_test_split() method is used to split our data into train and test sets. First, we need to divide our data into features (X) and labels (y).
# #where feartures is the input data contains multiple counumns and label as a single output column 
# The dataframe gets divided into X_train, X_test, y_train, and y_test. X_train and y_train sets are used for training and fitting the model.
#  The X_test and y_test sets are used for testing the model if it's predicting the right outputs/labels. we can explicitly test the size of the train and test sets

print("Training Random Forest model...")
# n_jobs=-1 uses all available CPU cores for faster training
model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
#here n_estimator=100 denotes total 100 trees in the forest i.e. total 100 differ models to generate output
#random_state=42 respresnt that every 42 data is taken and given to eaach model this ensures,whwnever you run task exactly same data set is going to each tree and structure of trees remains exactly as previous
#n_jobs=-1 The number of jobs to run in parallel. fit, predict, decision_path and apply are all parallelized over the trees. None means 1 unless in a joblib.parallel_backend context. -1 means using all processors. See Glossary for more details.
model.fit(X_train, y_train)

print("Model training complete. Evaluating...")
accuracy = model.score(X_test, y_test)
print(f"Model Accuracy: {accuracy * 100:.2f}%")

print("Saving model and label encoder...")
joblib.dump(model, 'random_forest_model.joblib')
joblib.dump(le, 'label_encoder.joblib')
print("Model saved to 'random_forest_model.joblib'")

#feartures of joblib
#Model persistence (saving models):
#After training a model, you don’t want to retrain it every time.
#With joblib, you can save the trained model to a file and load it later
#Handles large objects better than pickle: 