from flask import Flask, render_template, request, session, redirect, url_for, jsonify, flash, send_file
import json
import random
import os
from collections import defaultdict
from datetime import datetime
from werkzeug.utils import secure_filename
from question_manager import QuestionManager
from user_stats import UserStatsManager

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_ici_changez_pour_production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max

# Initialiser le gestionnaire de questions
question_manager = QuestionManager()

# Initialiser le gestionnaire de stats
user_stats = UserStatsManager()

# Configuration des thèmes
chapitres = [
    "derivatives",
    "sequences",
    "limits",
    "logarithm_exponential",
    "domain_definition",
    "primitives_ode",
    "combinatorics_probability",
    "geometry",
    "trigonometry",
    "integral_calculus"
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'json'}

def load_questions():
    return question_manager.load_questions('maths.json')

def save_questions(data):
    with open('maths.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_theme_name(theme_id):
    theme_names = {
        "derivatives": "Dérivées",
        "sequences": "Suites",
        "limits": "Limites",
        "logarithm_exponential": "Logarithme et Exponentielle",
        "domain_definition": "Domaine de définition",
        "primitives_ode": "Primitives et Équations Différentielles",
        "combinatorics_probability": "Dénombrement et Probabilités",
        "geometry": "Géométrie dans l'Espace",
        "trigonometry": "Trigonométrie",
        "integral_calculus": "Calcul Intégral"
    }
    return theme_names.get(theme_id, theme_id)

def get_difficulty_text(score):
    if score < 1.5:
        return "Très facile"
    elif score < 2:
        return "Facile"
    elif score < 2.5:
        return "Moyen"
    elif score < 3:
        return "Difficile"
    else:
        return "Très difficile"

def calculate_dynamic_difficulty(question):
    """
    Calcule la difficulté d'une question en fonction de son taux de réussite.
    Retourne None si pas assez de tentatives.
    """
    points = question.get("points", [0, 0])
    attempts = points[1]
    correct = points[0]

    # Pas assez de données (moins de 3 tentatives)
    if attempts < 3:
        return None

    # Calcul du taux de réussite
    success_rate = (correct / attempts) * 100 if attempts > 0 else 0

    # Système de difficulté basé sur le taux de réussite
    if success_rate >= 80:
        return "Très facile"
    elif success_rate >= 65:
        return "Facile"
    elif success_rate >= 45:
        return "Moyenne"
    elif success_rate >= 25:
        return "Difficile"
    else:
        return "Très difficile"

def get_difficulty_stats():
    """Retourne les statistiques de difficulté"""
    data = load_questions()

    difficulty_stats = {
        'Très facile': {'count': 0, 'avg_success': 0, 'questions': 0, 'attempts': 0, 'correct': 0},
        'Facile': {'count': 0, 'avg_success': 0, 'questions': 0, 'attempts': 0, 'correct': 0},
        'Moyenne': {'count': 0, 'avg_success': 0, 'questions': 0, 'attempts': 0, 'correct': 0},
        'Difficile': {'count': 0, 'avg_success': 0, 'questions': 0, 'attempts': 0, 'correct': 0},
        'Très difficile': {'count': 0, 'avg_success': 0, 'questions': 0, 'attempts': 0, 'correct': 0}
    }

    for question in data:
        difficulty = question.get('difficulty', 'Moyenne')
        if difficulty in difficulty_stats:
            points = question.get('points', [0, 0])
            attempts = points[1]
            correct = points[0]

            difficulty_stats[difficulty]['count'] += 1
            difficulty_stats[difficulty]['questions'] += 1
            difficulty_stats[difficulty]['attempts'] += attempts
            difficulty_stats[difficulty]['correct'] += correct

    # Calculer les taux de réussite moyens par difficulté
    for diff, stats in difficulty_stats.items():
        if stats['attempts'] > 0:
            stats['avg_success'] = round((stats['correct'] / stats['attempts']) * 100, 1)
        else:
            stats['avg_success'] = 0

    return difficulty_stats

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/maths')
def maths_menu():
    return render_template('maths_menu.html')

@app.route('/start-quiz', methods=['POST'])
def start_quiz():
    quiz_type = request.form.get('quiz_type')
    theme_id = request.form.get('theme_id', 0)

    data = load_questions()
    questions = []

    if quiz_type == 'complet':
        questions = random.sample(data, min(10, len(data)))
    else:
        theme_id = int(theme_id)
        if 1 <= theme_id <= len(chapitres):
            theme = chapitres[theme_id - 1]
            theme_questions = [q for q in data if theme in q.get("themes", [])]
            questions = random.sample(theme_questions, min(10, len(theme_questions)))

    session['questions'] = questions
    session['current_question'] = 0
    session['score'] = 0
    session['answers'] = []

    return redirect(url_for('show_question'))

@app.route('/question')
def show_question():
    if 'questions' not in session or session['current_question'] >= len(session['questions']):
        return redirect(url_for('index'))

    question = session['questions'][session['current_question']]
    question_number = session['current_question'] + 1
    total_questions = len(session['questions'])

    return render_template('quiz.html',
                           question=question,
                           question_number=question_number,
                           total_questions=total_questions)

@app.route('/submit-answer', methods=['POST'])
def submit_answer():
    # Récupérer la réponse (simple ou multiple)
    is_multiple = request.form.get('is_multiple') == 'true'

    if is_multiple:
        # Réponses multiples - récupérer la liste
        answers = request.form.getlist('answers')
        # Trier pour avoir un ordre cohérent (a,b,c au lieu de c,b,a)
        answers.sort()
        answer_str = ''.join(answers) if answers else ''
    else:
        # Réponse simple
        answer_str = request.form.get('answer', '')

    current_q_index = session['current_question']
    question = session['questions'][current_q_index]

    # Vérifier si la réponse est correcte (pour les réponses multiples)
    if is_multiple:
        # Pour les réponses multiples, on compare les chaînes triées
        correct_answer_str = question['answer']
        # Trier la bonne réponse aussi pour être sûr
        correct_sorted = ''.join(sorted(correct_answer_str))
        answer_sorted = ''.join(sorted(answer_str))
        is_correct = (answer_sorted == correct_sorted)
    else:
        is_correct = (answer_str == question['answer'])

    # Fonction pour obtenir le texte d'une réponse (gère les réponses multiples)
    def get_answer_text(question, answer_key):
        if not answer_key:
            return "Non spécifié"

        answer_key_str = str(answer_key)

        # Si c'est une réponse multiple (plusieurs lettres)
        if len(answer_key_str) > 1:
            # Pour chaque lettre, essayer de récupérer le texte correspondant
            parts = []
            for letter in answer_key_str:
                if letter in question['choices']:
                    parts.append(f"{letter}: {question['choices'][letter]}")
                else:
                    parts.append(letter)
            return " / ".join(parts)
        else:
            # Réponse simple
            return question['choices'].get(answer_key_str, f"Option {answer_key_str}")

    # Récupérer les textes des réponses
    user_choice_text = get_answer_text(question, answer_str)
    correct_choice_text = get_answer_text(question, question['answer'])

    user_answer = {
        'question': question['question'],
        'user_answer': answer_str,
        'user_answer_text': user_choice_text,
        'correct_answer': question['answer'],
        'correct_answer_text': correct_choice_text,
        'is_correct': is_correct
    }

    session['answers'].append(user_answer)

    # Charger les données
    data = load_questions()
    question_updated = False

    for q in data:
        if q.get('id') == question.get('id'):
            if is_correct:
                session['score'] = session.get('score', 0) + 1
                q["points"][0] += 1
                q["points"][1] += 1
            else:
                q["points"][1] += 1

            # Mettre à jour la difficulté
            old_difficulty = q.get('difficulty')
            new_difficulty = calculate_dynamic_difficulty(q)

            if new_difficulty is None:
                # Pas assez de données, on enlève la difficulté ou on laisse l'ancienne
                if 'difficulty' in q:
                    # Option 1: supprimer la clé difficulty
                    # del q['difficulty']
                    # Option 2: mettre "N/A"
                    q['difficulty'] = "N/A"
            elif old_difficulty != new_difficulty:
                q['difficulty'] = new_difficulty
                question_updated = True

            break

    # Sauvegarder les modifications
    save_questions(data)

    # Enregistrer l'activité pour le streak
    if session['current_question'] + 1 >= len(session['questions']):
        total_questions = len(session['questions'])
        score = session.get('score', 0)
        user_stats.record_quiz_activity(total_questions, score)

    session['current_question'] += 1

    if session['current_question'] >= len(session['questions']):
        return redirect(url_for('show_results'))

    return redirect(url_for('show_question'))

@app.route('/results')
def show_results():
    if 'questions' not in session:
        return redirect(url_for('index'))

    score = session.get('score', 0)
    total = len(session.get('questions', []))
    answers = session.get('answers', [])

    session.pop('questions', None)
    session.pop('current_question', None)
    session.pop('answers', None)

    return render_template('result.html',
                           score=score,
                           total=total,
                           answers=answers,
                           percentage=int((score/total)*100) if total > 0 else 0)

# --- Routes pour les statistiques ---
@app.route('/stats')
def stats_dashboard():
    return render_template('stats_dashboard.html')

@app.route('/stats/global')
def stats_global():
    data = load_questions()

    total_questions = len(data)
    total_attempts = sum(q.get("points", [0, 0])[1] for q in data)
    total_correct = sum(q.get("points", [0, 0])[0] for q in data)
    accuracy = (total_correct / total_attempts * 100) if total_attempts > 0 else 0

    themes_count = defaultdict(int)
    themes_correct = defaultdict(int)
    themes_attempts = defaultdict(int)

    for question in data:
        for theme in question.get("themes", []):
            themes_count[theme] += 1
            points = question.get("points", [0, 0])
            themes_correct[theme] += points[0]
            themes_attempts[theme] += points[1]

    theme_names_fr = {
        "derivatives": "Dérivées",
        "sequences": "Suites",
        "limits": "Limites",
        "logarithm_exponential": "Log et Exponentielle",
        "domain_definition": "Domaine de définition",
        "primitives_ode": "Primitives et ED",
        "combinatorics_probability": "Probabilités",
        "geometry": "Géométrie",
        "trigonometry": "Trigonométrie",
        "integral_calculus": "Calcul intégral"
    }

    themes_data = []
    for theme_id, theme_name in theme_names_fr.items():
        if themes_attempts.get(theme_id, 0) > 0:
            themes_data.append({
                'name': theme_name,
                'id': theme_id,
                'total': themes_count.get(theme_id, 0),
                'attempts': themes_attempts.get(theme_id, 0),
                'correct': themes_correct.get(theme_id, 0),
                'accuracy': round((themes_correct.get(theme_id, 0) / themes_attempts.get(theme_id, 0) * 100), 1)
            })

    themes_data.sort(key=lambda x: x['accuracy'], reverse=True)

    return jsonify({
        'global': {
            'total_questions': total_questions,
            'total_attempts': total_attempts,
            'total_correct': total_correct,
            'accuracy': round(accuracy, 1)
        },
        'themes': themes_data
    })

@app.route('/stats/theme/<theme_id>')
def stats_theme(theme_id):
    data = load_questions()
    theme_questions = [q for q in data if theme_id in q.get("themes", [])]

    if not theme_questions:
        return jsonify({'error': 'Thème non trouvé'}), 404

    theme_names_fr = {
        "derivatives": "Dérivées",
        "sequences": "Suites",
        "limits": "Limites",
        "logarithm_exponential": "Logarithme et Exponentielle",
        "domain_definition": "Domaine de définition",
        "primitives_ode": "Primitives et Équations Différentielles",
        "combinatorics_probability": "Dénombrement et Probabilités",
        "geometry": "Géométrie dans l'Espace",
        "trigonometry": "Trigonométrie",
        "integral_calculus": "Calcul Intégral"
    }

    total_questions = len(theme_questions)
    total_attempts = sum(q.get("points", [0, 0])[1] for q in theme_questions)
    total_correct = sum(q.get("points", [0, 0])[0] for q in theme_questions)
    accuracy = (total_correct / total_attempts * 100) if total_attempts > 0 else 0

    questions_stats = []
    for q in theme_questions:
        points = q.get("points", [0, 0])
        q_accuracy = (points[0] / points[1] * 100) if points[1] > 0 else 0
        questions_stats.append({
            'id': q.get('id'),
            'question': q.get('question'),
            'difficulty': q.get('difficulty', 'Moyenne'),
            'attempts': points[1],
            'correct': points[0],
            'accuracy': round(q_accuracy, 1)
        })

    questions_stats.sort(key=lambda x: x['accuracy'])

    difficulty_map = {'Très facile': 1, 'Facile': 2, 'Moyenne': 3, 'Difficile': 4, 'Très difficile': 5}
    avg_difficulty = sum(difficulty_map.get(q.get('difficulty', 'Moyenne'), 3) for q in theme_questions) / total_questions

    return jsonify({
        'theme': {
            'id': theme_id,
            'name': theme_names_fr.get(theme_id, theme_id),
            'total_questions': total_questions,
            'total_attempts': total_attempts,
            'total_correct': total_correct,
            'accuracy': round(accuracy, 1),
            'avg_difficulty': round(avg_difficulty, 1),
            'difficulty_text': get_difficulty_text(avg_difficulty)
        },
        'questions': questions_stats
    })

# --- Routes pour l'administration des questions ---
@app.route('/admin/questions')
def admin_questions():
    return render_template('admin_questions.html')

@app.route('/admin/questions/upload', methods=['GET', 'POST'])
def upload_questions():
    if request.method == 'POST':
        if 'question_file' not in request.files:
            flash('Aucun fichier sélectionné', 'error')
            return redirect(request.url)

        file = request.files['question_file']

        if file.filename == '':
            flash('Aucun fichier sélectionné', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])

            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            description = request.form.get('description', 'Téléversement via interface web')

            try:
                success = question_manager.add_questions_from_file(filepath, description)

                os.remove(filepath)

                if success:
                    flash('Questions ajoutées avec succès!', 'success')
                    return redirect(url_for('admin_questions'))
                else:
                    flash('Erreur lors de l\'ajout des questions', 'error')

            except Exception as e:
                flash(f'Erreur: {str(e)}', 'error')
                return redirect(request.url)

        else:
            flash('Format de fichier non autorisé. Utilisez un fichier JSON.', 'error')

    return render_template('upload_questions.html')

@app.route('/admin/questions/archives')
def list_archives():
    archives = question_manager.archive_manager.list_archives()
    stats = question_manager.archive_manager.get_archive_stats()

    return render_template('list_archives.html',
                           archives=archives,
                           stats=stats)

@app.route('/admin/questions/restore/<path:archive_name>')
def restore_archive(archive_name):
    try:
        archive_path = os.path.join('archives', archive_name)

        if not os.path.exists(archive_path):
            flash('Archive non trouvée', 'error')
            return redirect(url_for('list_archives'))

        success = question_manager.restore_from_archive(archive_path)

        if success:
            flash(f'Archive {archive_name} restaurée avec succès', 'success')
        else:
            flash('Erreur lors de la restauration', 'error')

    except Exception as e:
        flash(f'Erreur: {str(e)}', 'error')

    return redirect(url_for('list_archives'))

@app.route('/admin/questions/stats')
def questions_stats():
    data = load_questions()

    themes_count = {}
    difficulty_count = {'Très facile': 0, 'Facile': 0, 'Moyenne': 0, 'Difficile': 0, 'Très difficile': 0}

    for q in data:
        for theme in q.get('themes', []):
            themes_count[theme] = themes_count.get(theme, 0) + 1

        difficulty = q.get('difficulty', 'Moyenne')
        difficulty_count[difficulty] = difficulty_count.get(difficulty, 0) + 1

    total_attempts = sum(q.get("points", [0, 0])[1] for q in data)
    total_correct = sum(q.get("points", [0, 0])[0] for q in data)
    accuracy = (total_correct / total_attempts * 100) if total_attempts > 0 else 0

    return render_template('questions_stats.html',
                           total_questions=len(data),
                           themes_count=themes_count,
                           difficulty_count=difficulty_count,
                           total_attempts=total_attempts,
                           total_correct=total_correct,
                           accuracy=round(accuracy, 1))

# --- Nouvelle route pour réinitialiser les statistiques ---
@app.route('/admin/reset-stats', methods=['POST'])
def reset_stats():
    """Réinitialise toutes les statistiques utilisateur et les points des questions"""
    try:
        # Charger toutes les questions
        data = load_questions()

        # Réinitialiser les points de chaque question
        for question in data:
            question["points"] = [0, 0]  # [correct, attempts]

        # Sauvegarder les questions modifiées
        save_questions(data)

        # Réinitialiser les statistiques utilisateur
        user_stats.stats = {
            "streak": {
                "current": 0,
                "best": 0,
                "last_activity": None,
                "history": []
            },
            "daily_activity": {},
            "total_days_active": 0,
            "first_activity": None,
            "total_quizzes": 0,
            "total_questions_attempted": 0,
            "total_correct_answers": 0
        }
        user_stats.save_stats()

        flash('✅ Toutes les statistiques ont été réinitialisées avec succès !', 'success')

    except Exception as e:
        flash(f'❌ Erreur lors de la réinitialisation : {str(e)}', 'error')

    return redirect(url_for('list_archives'))

# --- Routes API ---
@app.route('/api/questions/count')
def api_questions_count():
    data = load_questions()

    import os
    mtime = os.path.getmtime('maths.json')
    from datetime import datetime
    last_modified = datetime.fromtimestamp(mtime).isoformat()

    return jsonify({
        'total': len(data),
        'last_modified': last_modified
    })

@app.route('/api/archives/count')
def api_archives_count():
    archives = question_manager.archive_manager.list_archives()
    return jsonify({
        'total': len(archives)
    })

@app.route('/api/questions/themes/stats')
def api_themes_stats():
    data = load_questions()

    themes_data = {}

    for q in data:
        for theme in q.get('themes', []):
            if theme not in themes_data:
                themes_data[theme] = {
                    'total': 0,
                    'attempts': 0,
                    'correct': 0
                }

            themes_data[theme]['total'] += 1
            points = q.get('points', [0, 0])
            themes_data[theme]['attempts'] += points[1]
            themes_data[theme]['correct'] += points[0]

    theme_names_fr = {
        "derivatives": "Dérivées",
        "sequences": "Suites",
        "limits": "Limites",
        "logarithm_exponential": "Log et Exponentielle",
        "domain_definition": "Domaine de définition",
        "primitives_ode": "Primitives et ED",
        "combinatorics_probability": "Probabilités",
        "geometry": "Géométrie",
        "trigonometry": "Trigonométrie",
        "integral_calculus": "Calcul intégral"
    }

    result = []
    for theme_id, data_count in themes_data.items():
        accuracy = (data_count['correct'] / data_count['attempts'] * 100) if data_count['attempts'] > 0 else 0

        if accuracy >= 80:
            accuracy_class = 'excellent'
        elif accuracy >= 60:
            accuracy_class = 'good'
        elif accuracy >= 40:
            accuracy_class = 'average'
        else:
            accuracy_class = 'poor'

        result.append({
            'id': theme_id,
            'name': theme_names_fr.get(theme_id, theme_id),
            'total': data_count['total'],
            'percentage': round((data_count['total'] / len(data) * 100), 1),
            'attempts': data_count['attempts'],
            'correct': data_count['correct'],
            'accuracy': round(accuracy, 1),
            'accuracy_class': accuracy_class
        })

    return jsonify(result)

@app.route('/api/archive/info/<path:filename>')
def api_archive_info(filename):
    archive_path = os.path.join('archives', filename)

    if not os.path.exists(archive_path):
        return jsonify({'error': 'Archive non trouvée'}), 404

    # Charger les métadonnées si disponibles
    metadata_path = archive_path.replace('.json', '.meta.json')
    metadata = {}
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

    # Charger le rapport si disponible
    report_path = archive_path.replace('.json', '.report.json')
    report = None
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)

    # Compter le nombre de questions
    questions_count = 0
    try:
        with open(archive_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            questions_count = len(data)
    except:
        pass

    return jsonify({
        'filename': filename,
        'path': archive_path,
        'size': os.path.getsize(archive_path),
        'modified': datetime.fromtimestamp(os.path.getmtime(archive_path)).isoformat(),
        'metadata': metadata,
        'questions_count': questions_count,
        'report': report
    })

# --- Nouvelles routes pour streak et difficulté ---
@app.route('/api/stats/streak')
def api_streak_stats():
    streak_info = user_stats.get_streak_info()
    recent_activity = user_stats.get_recent_activity(7)
    activity_summary = user_stats.get_activity_summary()

    return jsonify({
        "streak": streak_info,
        "recent_activity": recent_activity,
        "activity_summary": activity_summary
    })

@app.route('/stats/difficulty')
def stats_difficulty():
    difficulty_stats = get_difficulty_stats()

    # Calculer la distribution
    total_questions = sum(stats['count'] for stats in difficulty_stats.values())

    distribution = []
    for diff, stats in difficulty_stats.items():
        if stats['count'] > 0:
            percentage = round((stats['count'] / total_questions) * 100, 1)
            distribution.append({
                'difficulty': diff,
                'count': stats['count'],
                'percentage': percentage,
                'avg_success': stats['avg_success'],
                'attempts': stats['attempts'],
                'correct': stats['correct']
            })

    # Trier par difficulté (personnalisé)
    difficulty_order = ['Très facile', 'Facile', 'Moyenne', 'Difficile', 'Très difficile']
    distribution.sort(key=lambda x: difficulty_order.index(x['difficulty']))

    return jsonify({
        'distribution': distribution,
        'total_questions': total_questions
    })

@app.route('/api/questions/difficulty/<difficulty_level>')
def api_questions_by_difficulty(difficulty_level):
    data = load_questions()

    # Filtrer les questions par difficulté
    filtered_questions = [
        {
            'id': q['id'],
            'question': q['question'],
            'themes': q.get('themes', []),
            'attempts': q.get('points', [0, 0])[1],
            'correct': q.get('points', [0, 0])[0],
            'success_rate': round((q.get('points', [0, 0])[0] / q.get('points', [0, 0])[1] * 100), 1)
            if q.get('points', [0, 0])[1] > 0 else 0,
            'last_updated': q.get('last_updated', 'Jamais')
        }
        for q in data if q.get('difficulty', 'Moyenne') == difficulty_level
    ]

    # Trier par taux de réussite (plus difficile d'abord)
    filtered_questions.sort(key=lambda x: x['success_rate'])

    return jsonify({
        'difficulty': difficulty_level,
        'count': len(filtered_questions),
        'questions': filtered_questions[:20]  # Limiter à 20 questions
    })

@app.route('/admin/questions/update-difficulties')
def update_all_difficulties():
    """Met à jour la difficulté de toutes les questions"""
    try:
        result = question_manager.update_all_difficulties()
        flash(f"Difficultés mises à jour : {result['message']}", 'success')
    except Exception as e:
        flash(f'Erreur : {str(e)}', 'error')

    return redirect(url_for('admin_questions'))

@app.route('/download/questions')
def download_questions():
    return send_file('maths.json',
                     as_attachment=True,
                     download_name=f'maths_backup_{datetime.now().strftime("%Y%m%d")}.json')

@app.route('/download/archive/<filename>')
def download_archive(filename):
    return send_file(f'archives/{filename}',
                     as_attachment=True,
                     download_name=filename)

# Contexte pour les templates
@app.context_processor
def utility_processor():
    return dict(get_theme_name=get_theme_name)

@app.route('/admin/archives/create')
def create_archive():
    """Crée une archive manuelle de la base de questions actuelle."""
    try:
        from datetime import datetime
        # Créer une archive avec un nom simplifié (juste la date sans description longue)
        backup_path = question_manager.archive_manager.create_backup(
            question_manager.main_file,
            description="Manuelle"  # Description courte pour le nom de fichier
        )
        if backup_path and os.path.exists(backup_path):
            # Mettre à jour le mtime du fichier pour correspondre à la date de création
            os.utime(backup_path, (datetime.now().timestamp(), datetime.now().timestamp()))
            flash(f'✅ Archive créée avec succès', 'success')
        else:
            flash('❌ Erreur lors de la création de l\'archive', 'error')
    except Exception as e:
        flash(f'❌ Erreur : {str(e)}', 'error')
    return redirect(url_for('list_archives'))

@app.route('/admin/archives/delete/<path:filename>', methods=['POST'])
def delete_archive(filename):
    """Supprime une archive spécifique."""
    try:
        # Chemins des fichiers à supprimer
        archive_path = os.path.join('archives', filename)
        metadata_path = archive_path.replace('.json', '.meta.json')
        report_path = archive_path.replace('.json', '.report.json')

        deleted_count = 0

        # Supprimer l'archive principale
        if os.path.exists(archive_path):
            os.remove(archive_path)
            deleted_count += 1

        # Supprimer les métadonnées si elles existent
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
            deleted_count += 1

        # Supprimer le rapport si il existe
        if os.path.exists(report_path):
            os.remove(report_path)
            deleted_count += 1

        if deleted_count > 0:
            return jsonify({'success': True, 'message': f'{deleted_count} fichier(s) supprimé(s)'})
        else:
            return jsonify({'error': 'Archive non trouvée'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)