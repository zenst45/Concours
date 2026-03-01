import json
import random

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

def load_questions():
    with open("maths.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Les fonctions originales peuvent être conservées pour compatibilité
# mais ne seront plus utilisées par l'interface web