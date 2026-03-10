# 📝 Concours ADVANCE — Quiz Web App
> A Flask-based quiz platform with question management, difficulty filtering, user statistics, and LaTeX rendering — built for competitive exam preparation.

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![KaTeX](https://img.shields.io/badge/KaTeX-LaTeX_Rendering-008080?style=flat-square)](https://katex.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Stars](https://img.shields.io/github/stars/zenst45/Concours?style=flat-square)](https://github.com/zenst45/Concours/stargazers)

---

## 📖 Overview

**Concours** is a web application built with **Flask** that allows users to train for competitive exams through interactive quizzes. Questions can be filtered by difficulty, rendered with full **LaTeX support via KaTeX**, and the app tracks detailed **user statistics** to help monitor progress over time.

Questions are stored in JSON files, making it easy to add, edit, or swap out question sets without touching the core code.

---

## ✨ Features

- 🧠 **Interactive quizzes** — answer questions one by one with immediate feedback
- 🔢 **LaTeX rendering** — mathematical formulas displayed beautifully via KaTeX
- 🎚️ **Difficulty filtering** — select questions by difficulty level
- 📊 **User statistics** — track scores, streaks, and performance over time
- 📁 **JSON-based question bank** — easily customizable and extensible
- 🌐 **Multi-subject support** — separate JSON files per subject (e.g. maths, english)

---

## 📁 Project Structure

```
Concours/
├── app.py                  # Flask application & route definitions
├── main.py                 # Entry point to run the app
├── question_manager.py     # Question loading, filtering, and selection logic
├── maths_utils.py          # Utilities for maths question handling
├── user_stats.py           # User statistics tracking and persistence
├── maths.example.json      # Example question bank (maths)
├── english.json            # Question bank (english)
├── templates/              # Jinja2 HTML templates
├── static/                 # CSS, JS, and KaTeX assets
├── .gitignore
└── LICENSE
```

---

## 🚀 Getting Started

### Prerequisites

Python 3.x is required. Install dependencies with:

```bash
pip install flask
```

### Run the App

```bash
python main.py
```

Then open your browser at:

```
http://localhost:5000
```

---

## 🔧 Usage

### Adding Questions

Questions are stored in JSON files at the root of the project. Follow the format from `maths.example.json` to create your own question bank:

```json
[
  {
    "question": "Solve $x^2 - 4 = 0$",
    "choices": ["x = 2", "x = -2", "x = ±2", "x = 4"],
    "answer": "x = ±2",
    "difficulty": 2
  }
]
```

- `question` — supports LaTeX syntax (rendered by KaTeX)
- `choices` — list of possible answers
- `answer` — correct answer string
- `difficulty` — integer from 1 (easy) to 3 (hard)

### Filtering by Difficulty

On the quiz interface, select a difficulty level before starting a session to only receive questions matching that level.

---

## 📊 Statistics

The app tracks per-session and cumulative stats including:

- Total questions answered
- Correct / incorrect answers
- Score percentage per subject
- Performance over time

Stats are managed by `user_stats.py` and persisted between sessions.

---

## 🧠 How It Works

1. **Load questions** — `question_manager.py` reads the JSON question bank and filters by subject and difficulty
2. **Serve the quiz** — Flask routes in `app.py` handle navigation between questions and answer submission
3. **Render LaTeX** — KaTeX is loaded client-side in the HTML templates for instant formula rendering
4. **Track stats** — correct/incorrect answers are recorded by `user_stats.py` after each question

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

Made by [zenst45](https://github.com/zenst45)
