from flask import Flask, render_template, request
import os
import pickle
import threading
import webbrowser
from pathlib import Path

import pandas as pd

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "mbti_quiz_model.pkl"


with MODEL_PATH.open("rb") as f:
    bundle = pickle.load(f)

models = bundle["models"]
question_cols = bundle["question_cols"]

# Use the dataset column text as the prompt label.
question_texts = {col: col for col in question_cols}

MBTI_DESCRIPTIONS = {
    "INTJ": "The Architect - strategic, independent, and future-focused.",
    "INTP": "The Thinker - curious, analytical, and imaginative.",
    "ENTJ": "The Commander - bold, organized, and natural at leading.",
    "ENTP": "The Debater - inventive, energetic, and loves ideas.",
    "INFJ": "The Advocate - insightful, idealistic, and empathetic.",
    "INFP": "The Mediator - creative, sensitive, and values-driven.",
    "ENFJ": "The Protagonist - warm, inspiring, and people-oriented.",
    "ENFP": "The Campaigner - enthusiastic, expressive, and imaginative.",
    "ISTJ": "The Logistician - practical, responsible, and dependable.",
    "ISFJ": "The Defender - caring, loyal, and detail-oriented.",
    "ESTJ": "The Executive - efficient, decisive, and structured.",
    "ESFJ": "The Consul - supportive, social, and community-minded.",
    "ISTP": "The Virtuoso - adaptable, hands-on, and calm under pressure.",
    "ISFP": "The Adventurer - gentle, artistic, and flexible.",
    "ESTP": "The Entrepreneur - energetic, bold, and action-driven.",
    "ESFP": "The Entertainer - lively, spontaneous, and fun-loving.",
}

DIMENSION_CONFIG = [
    ("E_I", ("E", "I"), "Energy"),
    ("S_N", ("S", "N"), "Awareness"),
    ("T_F", ("T", "F"), "Decision Style"),
    ("J_P", ("J", "P"), "Lifestyle"),
]


def validate_answers(form_data):
    cleaned_answers = {}

    for col in question_cols:
        value = form_data.get(col)

        if value is None or value == "":
            raise ValueError("Please answer every question before submitting your result.")

        try:
            numeric_value = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Each answer must be a number from 1 to 5.") from exc

        if numeric_value not in {1, 2, 3, 4, 5}:
            raise ValueError("Answer choices must stay within the 1 to 5 scale.")

        cleaned_answers[col] = numeric_value

    return cleaned_answers


def validation_label(overall_confidence):
    if overall_confidence >= 80:
        return "High confidence"
    if overall_confidence >= 65:
        return "Balanced confidence"
    return "Low confidence"


def validation_message(overall_confidence):
    if overall_confidence >= 80:
        return "Your answers point clearly toward this type across all four MBTI dimensions."
    if overall_confidence >= 65:
        return "Your result looks fairly stable, though one or two dimensions are still close."
    return "Your answers were more mixed, so this result is best treated as a helpful starting point."


def predict_mbti(answer_dict):
    sample_df = pd.DataFrame([answer_dict])
    mbti_letters = []
    trait_scores = {}
    dimension_results = []

    for model_key, letters, label in DIMENSION_CONFIG:
        prediction = models[model_key].predict(sample_df)[0]
        probabilities = models[model_key].predict_proba(sample_df)[0]

        winner = letters[0] if prediction == 1 else letters[1]
        loser = letters[1] if prediction == 1 else letters[0]
        winner_score = round(probabilities[1] * 100, 2) if prediction == 1 else round(probabilities[0] * 100, 2)
        loser_score = round(probabilities[0] * 100, 2) if prediction == 1 else round(probabilities[1] * 100, 2)
        margin = round(abs(winner_score - loser_score), 2)

        mbti_letters.append(winner)
        trait_scores[letters[0]] = round(probabilities[1] * 100, 2)
        trait_scores[letters[1]] = round(probabilities[0] * 100, 2)
        dimension_results.append(
            {
                "label": label,
                "winner": winner,
                "loser": loser,
                "winner_score": winner_score,
                "loser_score": loser_score,
                "margin": margin,
            }
        )

    overall_confidence = round(
        sum(item["winner_score"] for item in dimension_results) / len(dimension_results),
        2,
    )
    weakest_dimension = min(dimension_results, key=lambda item: item["margin"])

    result_summary = {
        "dimension_results": dimension_results,
        "overall_confidence": overall_confidence,
        "validation_label": validation_label(overall_confidence),
        "validation_message": validation_message(overall_confidence),
        "weakest_dimension": weakest_dimension,
    }

    return "".join(mbti_letters), trait_scores, result_summary


@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    description = None
    trait_scores = None
    result_summary = None
    error = None
    avatar_path = None
    submitted_answers = {}

    if request.method == "POST":
        try:
            answers = validate_answers(request.form)
            submitted_answers = answers.copy()
            result, trait_scores, result_summary = predict_mbti(answers)
            description = MBTI_DESCRIPTIONS.get(result, "No description available.")

            candidate_path = f"avatars/{result}.jpg"
            static_full = os.path.join(app.static_folder, "avatars", f"{result}.jpg")
            if os.path.exists(static_full):
                avatar_path = candidate_path

        except Exception as e:
            error = str(e)

    return render_template(
        "index.html",
        question_cols=question_cols,
        question_texts=question_texts,
        result=result,
        description=description,
        trait_scores=trait_scores,
        result_summary=result_summary,
        error=error,
        avatar_path=avatar_path,
        submitted_answers=submitted_answers,
        total_questions=len(question_cols),
    )


def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")


if __name__ == "__main__":
    threading.Timer(1, open_browser).start()
    app.run(debug=True)
