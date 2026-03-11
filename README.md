# 📝 Concours ADVANCE — Quiz Web App
> A Flask-based interactive quiz platform for ADVANCE competitive exam preparation — featuring math training, dynamic difficulty, user statistics, streak tracking, and LaTeX rendering.

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![KaTeX](https://img.shields.io/badge/KaTeX-LaTeX_Rendering-008080?style=flat-square)](https://katex.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Stars](https://img.shields.io/github/stars/zenst45/Concours?style=flat-square)](https://github.com/zenst45/Concours/stargazers)

---

## 📖 Overview

**Concours ADVANCE** is a web application built with **Flask** for training on math questions in preparation for the ADVANCE competitive exam. It offers interactive multiple-choice quizzes across 10 mathematical topics, tracks detailed user statistics and daily streaks, and lets administrators easily manage the question bank with automatic archiving.

Questions are stored in JSON files, making them easy to add, edit, or extend without touching the core code. Mathematical formulas are rendered beautifully client-side via **KaTeX**.

---

## ✨ Features

### 🎯 Training
- **10 math topics** — derivatives, sequences, limits, logarithm/exponential, domain definition, primitives, probability, geometry, trigonometry, integral calculus — plus a full mixed mode
- **Single & multiple-choice questions** — automatic handling (e.g. answers like `"acd"`)
- **Dynamic difficulty** — each question is rated (Very Easy → Very Hard) based on real user success rates (computed after 3 attempts)
- **Detailed results** — score, progress circle, full answer breakdown with correct/incorrect indication and per-question stats

### 📊 User Statistics
- **Dashboard** — global accuracy, total questions, total attempts, current streak
- **Per-topic performance** — charts and tables, with a direct link to train on weak topics
- **Difficulty breakdown** — question distribution by level with average success rates
- **Streak tracking** — current streak, best streak, activity history, last 7 days view
- **Areas to improve** — topics with accuracy below 50% are highlighted with a quick-train button

### ⚙️ Question Administration
- **Upload questions** — import a JSON file; the system detects duplicates (by question text + choices) and reassigns conflicting IDs automatically
- **Automatic archiving** — before every import, `maths.json` is backed up in `archives/` with a timestamp and description; streak stats are saved in the associated `.meta.json`
- **Archive management** — list, download, restore, delete, or inspect any archive (including the streak snapshot from that date)
- **Detailed stats view** — question count per topic and difficulty level, percentage of total base
- **Reset statistics** — wipe all success points and streak history (irreversible, requires confirmation)

### 💻 UI
- Modern design with gradients, rounded cards, animations
- Fully responsive (mobile, tablet, desktop)
- Flash messages for actions and errors
- LaTeX rendering via KaTeX across all Jinja2 templates

---

## 📁 Project Structure
```
.
├── app.py                     # Main Flask application
├── question_manager.py        # Question & archive management
├── user_stats.py              # Streak and user statistics
├── maths_utils.py             # Utilities (compatibility)
├── requirements.txt           # Python dependencies
├── .gitignore
├── LICENSE
├── maths.example.json         # Example question bank (rename to maths.json)
├── static/
│   └── style.css
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── maths_menu.html
│   ├── quiz.html
│   ├── result.html
│   ├── stats_dashboard.html
│   ├── admin_questions.html
│   ├── upload_questions.html
│   ├── list_archives.html
│   └── questions_stats.html
├── archives/                  # Auto-generated backups (not versioned)
├── maths.json                 # Question database (not versioned)
└── user_stats.json            # User statistics (not versioned)
```

---

## 🚀 Getting Started

### Prerequisites

Python 3.x is required.

### Installation
```bash
# Clone the repository
git clone https://github.com/zenst45/Concours.git
cd Concours

# (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Set up the question bank
cp maths.example.json maths.json
# Or start from scratch with an empty array: []
```

### Run the App
```bash
python app.py
```

Open your browser at: `http://127.0.0.1:5000`

---

## 🔧 Question Format

Questions are stored in `maths.json` as a JSON array. Each object follows this structure:
```json
[
  {
    "id": 1,
    "question": "Soit $(u_n)$ une suite géométrique de raison $2$ telle que $u_2 = 1$. Alors",
    "choices": {
      "a": "$u_7 = 32$",
      "b": "$u_7 = 64$",
      "c": "$u_7 = 128$",
      "d": "$u_7 = 16$",
      "e": "rien de ce qui précède"
    },
    "answer": "a",
    "points": [0, 0],
    "themes": ["sequences"],
    "difficulty": "Moyenne",
    "first_seen": "2024-01-15"
  }
]
```

| Field | Description |
|---|---|
| `id` | Unique integer (auto-reassigned on conflict) |
| `question` | Question text, supports LaTeX |
| `choices` | Dict of `letter → text` pairs |
| `answer` | Letter or string of letters for multi-answer (e.g. `"acd"`) |
| `points` | `[correct, attempts]` — updated automatically |
| `themes` | List of theme IDs (see list below) |
| `difficulty` | Optional initial difficulty, default `"Moyenne"` — recalculated dynamically |
| `first_seen` | Optional date added |

**Available theme IDs:** `derivatives`, `sequences`, `limits`, `logarithm_exponential`, `domain_definition`, `primitives_ode`, `combinatorics_probability`, `geometry`, `trigonometry`, `integral_calculus`

---

## 📊 Statistics & Streaks

`user_stats.json` is auto-generated on first activity:
```json
{
  "streak": {
    "current": 3,
    "best": 5,
    "last_activity": "2025-03-10",
    "history": [
      { "streak": 5, "end_date": "2025-03-05", "start_date": "2025-03-01" }
    ]
  },
  "daily_activity": {
    "2025-03-10": {
      "quizzes_completed": 2,
      "questions_attempted": 20,
      "correct_answers": 15
    }
  },
  "total_days_active": 10,
  "first_activity": "2025-03-01",
  "total_quizzes": 15,
  "total_questions_attempted": 150,
  "total_correct_answers": 120
}
```

Streak data is also embedded into each archive's `.meta.json`, so restoring an archive also restores the streak state from that point in time.

---

## 🔌 Internal API

| Method | Endpoint | Description |
|---|---|---|
| GET | `/stats/global` | Global accuracy and totals |
| GET | `/stats/theme/<theme_id>` | Per-topic details |
| GET | `/stats/difficulty` | Difficulty breakdown |
| GET | `/api/stats/streak` | Current streak info |
| GET | `/api/questions/count` | Question count and last modified |
| GET | `/api/archives/count` | Number of archives |
| GET | `/api/archive/info/<filename>` | Archive metadata |
| POST | `/admin/archives/delete/<filename>` | Delete an archive |

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the project
2. Create a branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add my feature'`
4. Push the branch: `git push origin feature/my-feature`
5. Open a Pull Request

Please follow the existing code style and update documentation as needed.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

Made by [zenst45](https://github.com/zenst45)
