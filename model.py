import pandas as pd
import pickle
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "raw" / "16P.csv"
MODEL_PATH = BASE_DIR / "models" / "mbti_quiz_model.pkl"

# Load dataset
df = pd.read_csv(DATA_PATH, encoding="latin1")

print("Dataset shape:", df.shape)
print("Columns:", df.columns.tolist())


# preprocess the data
target_col = "Personality"
id_col = "Response Id"

# Keep only questionnaire columns
question_cols = [col for col in df.columns if col not in [id_col, target_col]]

# Remove missing rows if any
df = df.dropna(subset=question_cols + [target_col]).copy()

# Features
X = df[question_cols]

# Create 4 binary trait labels
df["E_I"] = df["Personality"].apply(lambda x: 1 if x[0] == "E" else 0)
df["S_N"] = df["Personality"].apply(lambda x: 1 if x[1] == "S" else 0)
df["T_F"] = df["Personality"].apply(lambda x: 1 if x[2] == "T" else 0)
df["J_P"] = df["Personality"].apply(lambda x: 1 if x[3] == "J" else 0)

traits = ["E_I", "S_N", "T_F", "J_P"]


# training and evaluation
models = {}
results = {}

for trait in traits:
    print(f"\n======================")
    print(f"Training for {trait}")
    print(f"======================")

    y = df[trait]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    results[trait] = acc
    models[trait] = model

    print("Accuracy:", acc)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))


# accuracy summary
print("\n==== FINAL ACCURACIES ====")
for trait, acc in results.items():
    print(f"{trait}: {acc:.4f}")


# save the models and metadata
bundle = {
    "models": models,
    "question_cols": question_cols,
    "trait_map": {
        "E_I": {0: "I", 1: "E"},
        "S_N": {0: "N", 1: "S"},
        "T_F": {0: "F", 1: "T"},
        "J_P": {0: "P", 1: "J"},
    }
}

with MODEL_PATH.open("wb") as f:
    pickle.dump(bundle, f)

print(f"\nModel saved successfully as {MODEL_PATH}")
