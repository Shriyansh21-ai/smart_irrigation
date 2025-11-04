# Retrain using collected_data.csv which contains optional labels in last column
import pandas as pd
import os
from shutil import copyfile

COLLECTED = "data/collected_data.csv"
TRAINING = "data/training_data.csv"
BACKUP = "data/training_backup.csv"

if not os.path.exists(COLLECTED):
    print("No collected data to retrain.")
    raise SystemExit(1)

df = pd.read_csv(COLLECTED)
# Keep only rows where label present (0 or 1)
df_labeled = df[df['label'].notna() & (df['label'] != '')]
if df_labeled.empty:
    print("No labeled rows found in collected_data.csv")
    raise SystemExit(1)

# Map and append to training CSV
cols = ['soil_moisture','soil_temp','air_temp','humidity','light','label']
df_labeled = df_labeled[cols]
df_labeled = df_labeled.rename(columns={'label':'irrigation_needed'})

# Append to training CSV
if os.path.exists(TRAINING):
    copyfile(TRAINING, BACKUP)
    existing = pd.read_csv(TRAINING)
    combined = pd.concat([existing, df_labeled[['soil_moisture','soil_temp','air_temp','humidity','light','irrigation_needed']]], ignore_index=True)
else:
    combined = df_labeled

combined.to_csv(TRAINING, index=False)
print("Training CSV updated:", TRAINING)

# Retrain model
from xgboost import XGBClassifier
X = combined[['soil_moisture','soil_temp','air_temp','humidity','light']]
y = combined['irrigation_needed']
model = XGBClassifier(n_estimators=100, use_label_encoder=False, eval_metric='logloss')
model.fit(X, y)
os.makedirs('models', exist_ok=True)
model.save_model("models/irrigation_model.json")
print("Retrained model saved.")
