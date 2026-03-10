import json
import os
import shutil
from datetime import datetime
from typing import List, Dict, Any

class ArchiveManager:
    """Gestionnaire d'archivage automatique"""

    def __init__(self, archive_dir="archives"):
        self.archive_dir = archive_dir
        self.ensure_archive_dir()

    def ensure_archive_dir(self):
        """Crée le dossier d'archives s'il n'existe pas"""
        if not os.path.exists(self.archive_dir):
            os.makedirs(self.archive_dir)

    def create_backup(self, source_file: str, description: str = "avant ajout de questions"):
        """Crée une copie archivée du fichier"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        filename = os.path.basename(source_file)
        name, ext = os.path.splitext(filename)
        # Nettoyer la description pour le nom de fichier - garder seulement "Manuelle" ou court
        clean_description = description.replace(' ', '_').replace('/', '_').replace(':', '_')
        # Limiter la longueur de la description dans le nom de fichier
        if len(clean_description) > 20:
            clean_description = clean_description[:20]
        archive_name = f"{name}_{timestamp}_{clean_description}{ext}"
        archive_path = os.path.join(self.archive_dir, archive_name)

        try:
            # Copier le fichier
            shutil.copy2(source_file, archive_path)

            # S'assurer que le timestamp du fichier est correct
            current_time = datetime.now().timestamp()
            os.utime(archive_path, (current_time, current_time))

            # Créer les métadonnées avec toutes les informations
            metadata = {
                "original_file": source_file,
                "archive_date": datetime.now().isoformat(),
                "archive_datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "description": description,
                "size": os.path.getsize(source_file),
                "archive_path": archive_path,
                "created_by": "system"
            }

            # Sauvegarder les métadonnées
            metadata_path = archive_path.replace('.json', '.meta.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            print(f"✅ Archive créée: {archive_name} à {metadata['archive_datetime']}")
            return archive_path

        except Exception as e:
            print(f"❌ Erreur lors de la création de l'archive: {e}")
            return None

    def list_archives(self, source_file: str = None):
        """Liste toutes les archives disponibles"""
        archives = []

        if not os.path.exists(self.archive_dir):
            return archives

        for file in os.listdir(self.archive_dir):
            if file.endswith('.json') and not file.endswith('.meta.json') and not file.endswith('.report.json'):
                file_path = os.path.join(self.archive_dir, file)

                metadata_path = file_path.replace('.json', '.meta.json')
                metadata = {}
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)

                if source_file and metadata.get('original_file') != source_file:
                    continue

                # Compter le nombre de questions dans l'archive
                questions_count = 0
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        questions_count = len(data)
                except:
                    pass

                # Chercher un rapport associé
                report_path = file_path.replace('.json', '.report.json')
                report = None
                if os.path.exists(report_path):
                    with open(report_path, 'r', encoding='utf-8') as f:
                        report = json.load(f)

                archives.append({
                    'filename': file,
                    'path': file_path,
                    'size': os.path.getsize(file_path),
                    'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                    'metadata': metadata,
                    'questions_count': questions_count,
                    'report': report
                })

        archives.sort(key=lambda x: x['filename'], reverse=True)
        return archives

    def restore_archive(self, archive_path: str, target_file: str):
        """Restaure une archive"""
        try:
            shutil.copy2(archive_path, target_file)
            print(f"Archive restaurée: {archive_path} -> {target_file}")
            return True
        except Exception as e:
            print(f"Erreur lors de la restauration: {e}")
            return False

    def get_archive_stats(self):
        """Obtient des statistiques sur les archives"""
        archives = self.list_archives()

        if not archives:
            return {
                "total": 0,
                "total_size": 0,
                "oldest": None,
                "newest": None
            }

        total_size = sum(a['size'] for a in archives)
        dates = []
        for a in archives:
            try:
                dates.append(datetime.fromisoformat(a['modified']))
            except:
                pass

        if dates:
            oldest = min(dates).isoformat()
            newest = max(dates).isoformat()
        else:
            oldest = newest = None

        return {
            "total": len(archives),
            "total_size": total_size,
            "oldest": oldest,
            "newest": newest,
            "avg_size": total_size / len(archives) if archives else 0
        }

class QuestionManager:
    """Gestionnaire de questions avec archivage"""

    def __init__(self, main_file="maths.json", archive_dir="archives"):
        self.main_file = main_file
        self.archive_manager = ArchiveManager(archive_dir)

    def load_questions(self, filepath: str) -> List[Dict[str, Any]]:
        """Charge les questions depuis un fichier JSON."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Erreur: Le fichier {filepath} n'a pas été trouvé.")
            return []
        except json.JSONDecodeError:
            print(f"Erreur: Le fichier {filepath} n'est pas un JSON valide.")
            return []

    def save_questions(self, questions: List[Dict[str, Any]], filepath: str) -> None:
        """Sauvegarde les questions dans un fichier JSON."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)

    def create_question_key(self, question: Dict[str, Any]) -> str:
        """
        Crée une clé unique pour une question basée sur son intitulé ET ses choix de réponse.
        """
        question_text = question["question"].strip().lower()

        choices = question.get("choices", {})
        choices_parts = []

        for key in sorted(choices.keys()):
            choice_text = choices[key].strip().lower()
            choices_parts.append(f"{key}:{choice_text}")

        choices_str = ";".join(choices_parts)
        return f"{question_text}|{choices_str}"

    def merge_questions(self, existing_questions: List[Dict[str, Any]],
                        new_questions: List[Dict[str, Any]]):
        """
        Fusionne les questions en préservant les IDs.
        """
        existing_keys = {}
        existing_ids = {q["id"] for q in existing_questions if "id" in q}

        for q in existing_questions:
            key = self.create_question_key(q)
            existing_keys[key] = q

        max_id = max(existing_ids) if existing_ids else 0
        merged = existing_questions.copy()
        added_count = 0
        duplicate_count = 0

        for question in new_questions:
            # S'assurer que la question a un ID
            if "id" not in question:
                max_id += 1
                question["id"] = max_id

            question_key = self.create_question_key(question)

            if question_key in existing_keys:
                duplicate_count += 1
                continue

            original_id = question.get("id")
            if original_id in existing_ids:
                max_id += 1
                new_id = max_id
            else:
                new_id = original_id
                if original_id > max_id:
                    max_id = original_id

            question["id"] = new_id

            # Initialise les statistiques si absentes
            if "points" not in question:
                question["points"] = [0, 0]
            if "difficulty" not in question:
                question["difficulty"] = "Moyenne"
            if "first_seen" not in question:
                question["first_seen"] = datetime.now().strftime("%Y-%m-%d")

            merged.append(question)
            existing_keys[question_key] = question
            existing_ids.add(new_id)
            added_count += 1

        return merged, added_count, duplicate_count

    def add_questions_from_file(self, new_file_path: str, description: str = "Ajout manuel"):
        """Ajoute des questions depuis un fichier avec archivage automatique"""

        print(f"1. Création d'une archive de sauvegarde...")
        backup_path = self.archive_manager.create_backup(
            self.main_file,
            f"{description}"
        )

        if not backup_path and os.path.exists(self.main_file):
            print("Erreur: Impossible de créer la sauvegarde. Opération annulée.")
            return False

        print(f"2. Chargement des questions existantes...")
        existing_questions = self.load_questions(self.main_file)

        print(f"3. Chargement des nouvelles questions...")
        new_questions = self.load_questions(new_file_path)

        if not new_questions:
            print("Erreur: Aucune question valide dans le fichier")
            return False

        print(f"4. Fusion des questions...")
        merged_questions, added_count, duplicate_count = self.merge_questions(
            existing_questions,
            new_questions
        )

        print(f"5. Sauvegarde des questions fusionnées...")
        self.save_questions(merged_questions, self.main_file)

        # Créer un rapport
        report = {
            "date": datetime.now().isoformat(),
            "backup_file": backup_path,
            "source_file": new_file_path,
            "existing_count": len(existing_questions),
            "new_count": len(new_questions),
            "added_count": added_count,
            "duplicate_count": duplicate_count,
            "final_count": len(merged_questions),
            "description": description
        }

        # Sauvegarder le rapport
        if backup_path:
            report_path = backup_path.replace('.json', '.report.json')
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n{'='*50}")
        print("RAPPORT D'AJOUT DE QUESTIONS")
        print(f"{'='*50}")
        print(f"✓ Questions existantes: {len(existing_questions)}")
        print(f"✓ Nouvelles questions: {len(new_questions)}")
        print(f"✓ Questions ajoutées: {added_count}")
        print(f"✓ Questions dupliquées ignorées: {duplicate_count}")
        print(f"✓ Total final: {len(merged_questions)}")
        print(f"{'='*50}")

        return True

    def restore_from_archive(self, archive_path: str):
        """Restaure le fichier principal depuis une archive"""
        print(f"Restauration depuis l'archive: {os.path.basename(archive_path)}")

        # Créer une archive de l'état actuel avant restauration
        if os.path.exists(self.main_file):
            self.archive_manager.create_backup(self.main_file, "avant_restauration")

        # Restaurer
        success = self.archive_manager.restore_archive(archive_path, self.main_file)

        if success:
            print("✓ Restauration terminée avec succès")
        else:
            print("✗ Échec de la restauration")

        return success

    def update_all_difficulties(self):
        """Met à jour la difficulté de toutes les questions"""
        questions = self.load_questions(self.main_file)
        updated_count = 0

        for question in questions:
            old_difficulty = question.get('difficulty', 'Moyenne')

            # Calculer la nouvelle difficulté
            points = question.get('points', [0, 0])
            attempts = points[1]
            correct = points[0]

            if attempts == 0:
                new_difficulty = 'Moyenne'
            else:
                success_rate = (correct / attempts) * 100

                if attempts < 3:
                    new_difficulty = old_difficulty  # Pas assez de données
                elif success_rate >= 80:
                    new_difficulty = 'Très facile'
                elif success_rate >= 65:
                    new_difficulty = 'Facile'
                elif success_rate >= 45:
                    new_difficulty = 'Moyenne'
                elif success_rate >= 25:
                    new_difficulty = 'Difficile'
                else:
                    new_difficulty = 'Très difficile'

            if old_difficulty != new_difficulty:
                question['difficulty'] = new_difficulty
                updated_count += 1

        self.save_questions(questions, self.main_file)

        return {
            'total_questions': len(questions),
            'updated_count': updated_count,
            'message': f'{updated_count} questions mises à jour sur {len(questions)}'
        }