import json
import sys
from typing import List, Dict, Any

def load_questions(filepath: str) -> List[Dict[str, Any]]:
    """Charge les questions depuis un fichier JSON."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Erreur: Le fichier {filepath} n'a pas été trouvé.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Erreur: Le fichier {filepath} n'est pas un JSON valide.")
        sys.exit(1)

def save_questions(questions: List[Dict[str, Any]], filepath: str) -> None:
    """Sauvegarde les questions dans un fichier JSON."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

def create_question_key(question: Dict[str, Any]) -> str:
    """
    Crée une clé unique pour une question basée sur son intitulé ET ses choix de réponse.
    La clé est normalisée (minuscules, suppression des espaces superflus) pour éviter
    les faux positifs dus à des différences de formatage.
    """
    # Normaliser le texte de la question
    question_text = question["question"].strip().lower()

    # Normaliser les choix de réponse
    choices = question.get("choices", {})
    choices_parts = []

    # Trier les clés pour avoir un ordre cohérent
    for key in sorted(choices.keys()):
        # Normaliser le texte de chaque choix
        choice_text = choices[key].strip().lower()
        choices_parts.append(f"{key}:{choice_text}")

    # Créer une représentation textuelle des choix
    choices_str = ";".join(choices_parts)

    # Combiner l'intitulé et les choix
    return f"{question_text}|{choices_str}"

def merge_questions(existing_questions: List[Dict[str, Any]],
                    new_questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Fusionne les questions en préservant les IDs des nouvelles questions quand c'est possible.
    Si un ID existe déjà, attribue un nouvel ID.
    Vérifie les doublons basés sur l'intitulé ET les choix de réponse.
    """
    # Dictionnaire pour stocker les clés des questions existantes
    existing_keys = {}
    existing_ids = {q["id"] for q in existing_questions}

    # Préparer le dictionnaire des clés existantes
    for q in existing_questions:
        key = create_question_key(q)
        existing_keys[key] = q

    max_id = max(existing_ids) if existing_ids else 0
    merged = existing_questions.copy()

    for question in new_questions:
        # Créer la clé unique pour la nouvelle question
        question_key = create_question_key(question)

        # Vérifier si la question (intitulé + choix) existe déjà
        if question_key in existing_keys:
            print(f"Question dupliquée ignorée: {question['question'][:50]}...")
            continue

        # Vérifier si l'ID de la nouvelle question existe déjà
        original_id = question.get("id")
        if original_id in existing_ids:
            # ID en conflit, on en attribue un nouveau
            max_id += 1
            new_id = max_id
            print(f"Attention: ID {original_id} existe déjà. Attribution du nouvel ID {new_id}.")
        else:
            # ID disponible, on le conserve
            new_id = original_id
            if original_id > max_id:
                max_id = original_id

        question["id"] = new_id

        # Ajouter à la liste fusionnée
        merged.append(question)
        existing_keys[question_key] = question
        existing_ids.add(new_id)

    return merged

def main():
    # Chemins des fichiers
    existing_file = "maths.json"
    new_file = "questions.json"
    output_file = "maths_with_questions_merged.json"  # Ou utiliser existing_file pour écraser

    # Charger les questions existantes
    print(f"Chargement des questions existantes depuis {existing_file}...")
    existing_questions = load_questions(existing_file)
    print(f"{len(existing_questions)} questions chargées.")

    # Charger les nouvelles questions
    print(f"Chargement des nouvelles questions depuis {new_file}...")
    new_questions = load_questions(new_file)
    print(f"{len(new_questions)} nouvelles questions chargées.")

    # Fusionner les questions
    print("Fusion des questions...")
    merged_questions = merge_questions(existing_questions, new_questions)

    # Afficher les statistiques
    added_count = len(merged_questions) - len(existing_questions)
    print(f"\nRésumé:")
    print(f"- Questions existantes: {len(existing_questions)}")
    print(f"- Nouvelles questions: {len(new_questions)}")
    print(f"- Questions ajoutées: {added_count}")
    print(f"- Questions dupliquées ignorées: {len(new_questions) - added_count}")
    print(f"- Total après fusion: {len(merged_questions)}")

    # Sauvegarder le résultat
    print(f"\nSauvegarde des questions fusionnées dans {output_file}...")
    save_questions(merged_questions, output_file)
    print("Fusion terminée avec succès!")

if __name__ == "__main__":
    main()