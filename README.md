# PersonaScope MBTI Predictor

PersonaScope is a Flask-based MBTI prediction app that uses questionnaire responses and a trained machine learning model to estimate a user's likely MBTI type. The app includes a landing page, a guided questionnaire, answer validation, live progress tracking, and a result view with confidence-style validation across the four MBTI dimensions.

## Features

- Clean landing page with a guided user flow
- Questionnaire UI with progress tracking and client-side completeness checks
- Server-side validation to ensure every answer stays within the `1` to `5` scale
- Random forest based MBTI prediction using four binary trait models
- Result validation summary with:
  - overall confidence
  - per-dimension breakdown
  - weakest prediction dimension
- Avatar support for all 16 MBTI types

## Project Structure

```text
MBTI PREDICTOR v3/
|-- app.py
|-- model.py
|-- README.md
|-- .gitignore
|-- data/
|   `-- raw/
|       `-- 16P.csv
|-- docs/
|   `-- 16p-Mapping.txt
|-- models/
|   `-- mbti_quiz_model.pkl
|-- notebooks/
|   `-- DataVisual.ipynb
|-- static/
|   |-- avatars/
|   |   `-- *.jpg
|   |-- css/
|   |   `-- styles.css
|   `-- js/
|       `-- app.js
`-- templates/
    `-- index.html
```

## What Each Folder Is For

- `app.py`
  Runs the Flask web app, loads the trained model bundle, validates form input, predicts MBTI output, and renders the frontend.

- `model.py`
  Trains the machine learning models from the CSV dataset and saves the model bundle into `models/`.

- `data/raw/`
  Stores the original questionnaire dataset used for model training.

- `models/`
  Stores generated ML artifacts such as the trained `mbti_quiz_model.pkl` file.

- `docs/`
  Contains supporting notes and dataset-to-type mapping references.

- `notebooks/`
  Holds exploratory analysis or data visualization notebooks.

- `static/`
  Contains frontend assets:
  - `avatars/` for MBTI images
  - `css/` for styling
  - `js/` for client-side behavior

- `templates/`
  Contains Flask HTML templates.

## Tech Stack

- Python
- Flask
- pandas
- scikit-learn
- HTML, CSS, and JavaScript

## Setup

### 1. Create a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install dependencies

```powershell
pip install flask pandas scikit-learn
```

If you prefer, you can also create a `requirements.txt` later from your environment:

```powershell
pip freeze > requirements.txt
```

## Running the App

Start the Flask app with:

```powershell
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

The app will try to open the browser automatically when launched directly.

## Training or Rebuilding the Model

If `models/mbti_quiz_model.pkl` does not exist, or if you want to retrain the model:

```powershell
python model.py
```

This script will:

1. Load the dataset from `data/raw/16P.csv`
2. Split the MBTI type into four binary targets:
   - `E_I`
   - `S_N`
   - `T_F`
   - `J_P`
3. Train one `RandomForestClassifier` for each dimension
4. Print evaluation metrics
5. Save the trained model bundle to `models/mbti_quiz_model.pkl`

## How Prediction Works

The model does not directly predict one of the 16 MBTI classes in a single step. Instead, it predicts each of the four MBTI letter pairs independently:

- `E` vs `I`
- `S` vs `N`
- `T` vs `F`
- `J` vs `P`

The final MBTI type is assembled from the winners of those four binary predictions.

The app also computes:

- probability scores for both sides of each dimension
- an overall confidence average
- the weakest dimension based on the smallest probability margin

This makes the result page easier to interpret than a plain label alone.

## Validation Behavior

Both frontend and backend validation are present.

### Frontend validation

- Tracks how many questions are completed
- Scrolls to the first unanswered question on submit
- Highlights missing answers visually

### Backend validation

- Rejects missing answers
- Rejects non-integer input
- Rejects values outside the `1` to `5` range

Server-side validation is the final safety layer and should always be kept even if the UI changes.

## Notes About Version Control

The included `.gitignore` is set up to ignore common Python, notebook, environment, and generated model artifacts such as:

- `__pycache__/`
- `.ipynb_checkpoints/`
- virtual environments
- generated files in `models/`

If you want to keep a trained model inside version control anyway, remove the `models/*.pkl` rule from `.gitignore`.

## Suggested Next Improvements

- Add `requirements.txt`
- Move Flask app code into a package such as `src/` or `mbti_predictor/`
- Add automated tests for:
  - form validation
  - prediction response shape
  - route rendering
- Add model metadata such as training date and validation accuracy to the result page
- Add deployment support for Render, Railway, or PythonAnywhere

## Quick Start Summary

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install flask pandas scikit-learn
python model.py
python app.py
```

