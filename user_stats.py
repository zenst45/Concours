import json
import os
from datetime import datetime, timedelta

class UserStatsManager:
    """Gestionnaire des statistiques utilisateur pour suivre les streaks"""

    def __init__(self, stats_file="user_stats.json"):
        self.stats_file = stats_file
        self.load_stats()

    def load_stats(self):
        """Charge les statistiques utilisateur"""
        if os.path.exists(self.stats_file):
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                self.stats = json.load(f)
        else:
            self.stats = {
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
            self.save_stats()

    def save_stats(self):
        """Sauvegarde les statistiques utilisateur"""
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)

    def record_quiz_activity(self, questions_attempted, correct_answers):
        """Enregistre l'activité d'un quiz terminé"""
        today = datetime.now().strftime("%Y-%m-%d")

        # Initialiser l'activité quotidienne si nécessaire
        if today not in self.stats["daily_activity"]:
            self.stats["daily_activity"][today] = {
                "quizzes_completed": 0,
                "questions_attempted": 0,
                "correct_answers": 0
            }

        # Mettre à jour l'activité d'aujourd'hui
        self.stats["daily_activity"][today]["quizzes_completed"] += 1
        self.stats["daily_activity"][today]["questions_attempted"] += questions_attempted
        self.stats["daily_activity"][today]["correct_answers"] += correct_answers

        # Mettre à jour les totaux globaux
        self.stats["total_quizzes"] += 1
        self.stats["total_questions_attempted"] += questions_attempted
        self.stats["total_correct_answers"] += correct_answers

        # Mettre à jour la série (streak)
        self.update_streak(today)

        # Mettre à jour le premier jour d'activité
        if not self.stats["first_activity"]:
            self.stats["first_activity"] = today

        self.save_stats()

    def update_streak(self, today_str):
        """Met à jour la série de jours consécutifs"""
        today = datetime.strptime(today_str, "%Y-%m-%d")
        last_activity = self.stats["streak"]["last_activity"]

        if last_activity:
            last_date = datetime.strptime(last_activity, "%Y-%m-%d")
            days_diff = (today - last_date).days

            if days_diff == 1:
                # Jour consécutif - incrémenter le streak
                self.stats["streak"]["current"] += 1
            elif days_diff == 0:
                # Même jour - ne rien changer
                pass
            else:
                # Série rompue (plus d'un jour d'écart)
                # Enregistrer l'ancien streak dans l'historique s'il était > 0
                if self.stats["streak"]["current"] > 0:
                    self.stats["streak"]["history"].append({
                        "streak": self.stats["streak"]["current"],
                        "end_date": last_activity,
                        "start_date": self.get_streak_start_date(last_activity, self.stats["streak"]["current"])
                    })

                # Recommencer à 1 pour aujourd'hui
                self.stats["streak"]["current"] = 1
        else:
            # Première activité - commencer à 1
            self.stats["streak"]["current"] = 1

        # Mettre à jour la meilleure série
        if self.stats["streak"]["current"] > self.stats["streak"]["best"]:
            self.stats["streak"]["best"] = self.stats["streak"]["current"]

        # Mettre à jour la dernière activité
        self.stats["streak"]["last_activity"] = today_str

        # Mettre à jour le nombre total de jours actifs
        self.stats["total_days_active"] = len(self.stats["daily_activity"])

    def get_streak_start_date(self, end_date_str, streak_length):
        """Calcule la date de début d'un streak"""
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        start_date = end_date - timedelta(days=streak_length - 1)
        return start_date.strftime("%Y-%m-%d")

    def get_streak_info(self):
        """Retourne les informations sur la série"""
        return {
            "current": self.stats["streak"]["current"],
            "best": self.stats["streak"]["best"],
            "last_activity": self.stats["streak"]["last_activity"],
            "total_days_active": self.stats["total_days_active"],
            "first_activity": self.stats["first_activity"],
            "total_quizzes": self.stats["total_quizzes"],
            "total_questions_attempted": self.stats["total_questions_attempted"],
            "total_correct_answers": self.stats["total_correct_answers"],
            "history": self.stats["streak"]["history"][-3:] if self.stats["streak"]["history"] else []
        }

    def get_recent_activity(self, days=7):
        """Retourne l'activité des X derniers jours"""
        recent = []
        today = datetime.now()

        for i in range(days):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")

            if date_str in self.stats["daily_activity"]:
                day_stats = self.stats["daily_activity"][date_str]
                recent.append({
                    "date": date_str,
                    "day_name": date.strftime("%a"),
                    "day_number": date.day,
                    "quizzes": day_stats["quizzes_completed"],
                    "questions": day_stats["questions_attempted"],
                    "correct": day_stats["correct_answers"],
                    "active": True
                })
            else:
                recent.append({
                    "date": date_str,
                    "day_name": date.strftime("%a"),
                    "day_number": date.day,
                    "quizzes": 0,
                    "questions": 0,
                    "correct": 0,
                    "active": False
                })

        return list(reversed(recent))

    def get_activity_summary(self):
        """Retourne un résumé de l'activité"""
        total_accuracy = 0
        if self.stats["total_questions_attempted"] > 0:
            total_accuracy = (self.stats["total_correct_answers"] / self.stats["total_questions_attempted"]) * 100

        return {
            "total_quizzes": self.stats["total_quizzes"],
            "total_questions_attempted": self.stats["total_questions_attempted"],
            "total_correct_answers": self.stats["total_correct_answers"],
            "total_accuracy": round(total_accuracy, 1),
            "total_days_active": self.stats["total_days_active"],
            "avg_quizzes_per_day": round(self.stats["total_quizzes"] / max(self.stats["total_days_active"], 1), 1),
            "avg_questions_per_day": round(self.stats["total_questions_attempted"] / max(self.stats["total_days_active"], 1), 1)
        }