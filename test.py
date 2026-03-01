# # import json
# #
# # with open("maths.json", "r", encoding="utf-8") as f:
# #     data = json.load(f)
# # print(data["derivatives"][0]["id"])
# # ids = []
# # for i in data:
# #     for question in data[i]:
# #         ids.append(question["id"])
# #
# # ids.sort()
# # # 1️⃣ Doublons
# # doublons = [x for x in ids if ids.count(x) > 1]
# # doublons = list(set(doublons))  # on enlève les répétitions dans la liste des doublons
# # print("Doublons :", doublons)
# #
# # # 2️⃣ Valeurs manquantes
# # valeurs_attendues = set(range(1, 121))  # de 1 à 120 inclus
# # valeurs_presentes = set(ids)
# # manquants = valeurs_attendues - valeurs_presentes
# # print("Manquants :", sorted(manquants))
# #
# # # 3️⃣ Valeurs hors limites
# # hors_limites = [x for x in ids if x < 1 or x > 120]
# # print("Hors limites :", hors_limites)
# # print(ids)
#
# import json
# from collections import defaultdict
#
# # Charger le fichier JSON d'origine
# with open('maths.json', 'r', encoding='utf-8') as f:
#     data = json.load(f)
#
# # Dictionnaire pour regrouper les questions par ID
# questions_by_id = defaultdict(lambda: {
#     'id': None,
#     'question': '',
#     'choices': {},
#     'answer': '',
#     'points': [0, 0],
#     'themes': []
# })
#
# # Parcourir tous les thèmes et leurs questions
# for theme, questions in data.items():
#     for question_data in questions:
#         q_id = question_data['id']
#
#         # Si c'est la première fois qu'on voit cette question
#         if questions_by_id[q_id]['id'] is None:
#             questions_by_id[q_id].update({
#                 'id': q_id,
#                 'question': question_data['question'],
#                 'choices': question_data['choices'],
#                 'answer': question_data['answer'],
#                 'points': question_data['points']
#             })
#
#         # Ajouter le thème à la liste des thèmes de cette question
#         questions_by_id[q_id]['themes'].append(theme)
#
# # Convertir en liste et trier par ID
# new_structure = []
# for q_id in sorted(questions_by_id.keys()):
#     question = questions_by_id[q_id]
#     # Assurer l'unicité des thèmes (au cas où)
#     question['themes'] = list(set(question['themes']))
#     new_structure.append(question)
#
# # Écrire le résultat dans un nouveau fichier JSON
# with open('maths.json', 'w', encoding='utf-8') as f:
#     json.dump(new_structure, f, ensure_ascii=False, indent=2)
#
# print(f"Transformation terminée ! {len(new_structure)} questions traitées.")
# print("Résultat sauvegardé dans 'maths_reorganized.json'")



import json
import re

def transform_expression(text):
    # Remplacer les limites
    # Pattern pour les limites avec différentes cibles
    def replace_limit(match):
        expr = match.group(1)
        target = match.group(2)
        # Nettoyer l'expression
        expr = expr.strip()
        return r'$\lim_{x \to ' + target + '} ' + expr + '$'

    # Chercher les limites avec le motif : lim ( ... ) quand x tend vers ...
    # Ce motif peut s'étendre sur plusieurs lignes, mais nous supposons qu'il est sur une ligne.
    text = re.sub(r'lim \( (.*) \) quand x tend vers (\+∞|-\∞|∞|[0-9]+)', replace_limit, text)

    # Remplacer les racines
    text = re.sub(r'√\((.*?)\)', r'$\sqrt{\1}$', text)

    # Remplacer les fonctions avec exposants (ln, sin, cos, etc.)
    # Ce motif capture ln⁹, ln⁵, etc.
    # Convertir les exposants en chiffres normaux
    def replace_superscript(match):
        # Dictionnaire pour les exposants
        superscript_map = {
            '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
            '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9'
        }
        exp = match.group(1)
        # Convertir chaque caractère
        exp_normal = ''.join(superscript_map.get(ch, ch) for ch in exp)
        return r'$\ln^{' + exp_normal + '}'

    text = re.sub(r'ln([⁰¹²³⁴⁵⁶⁷⁸⁹]+)', replace_superscript, text)

    # Remplacer les fractions
    # On utilise un motif pour les fractions qui ont des parenthèses équilibrées
    # Ceci est un peu plus complexe, nous allons d'abord remplacer les fractions simples
    # et ensuite les fractions plus complexes avec des accolades.
    text = re.sub(r'\((.*?)\)/\((.*?)\)', r'$\frac{\1}{\2}$', text)

    # Remplacer les exponentielles
    text = re.sub(r'e\^(x)', r'$e^{\1}$', text)
    text = re.sub(r'e\^{(.*?)}', r'$e^{\1}$', text)

    # Remplacer les suites
    text = re.sub(r'u_n', r'$u_n$', text)
    text = re.sub(r'u_{n+1}', r'$u_{n+1}$', text)

    # Remplacer les sommes
    text = re.sub(r'Σ \(k=0 à n\)', r'$\sum_{k=0}^{n}$', text)

    # Remplacer les probabilités
    text = re.sub(r'P\((.*?)\)', r'$P(\1)$', text)
    text = re.sub(r'P_(.*?)\((.*?)\)', r'$P_{\1}(\2)$', text)

    # Remplacer les vecteurs
    text = re.sub(r'\(([0-9], [0-9], [0-9])\)', r'$(\1)$', text)

    # Remplacer les indices et exposants généraux
    text = re.sub(r'([a-zA-Z])_([0-9])', r'$\1_\2$', text)
    text = re.sub(r'([a-zA-Z])_({[0-9]+})', r'$\1_\2$', text)
    text = re.sub(r'([a-zA-Z])\^([0-9])', r'$\1^\2$', text)
    text = re.sub(r'([a-zA-Z])\^({[0-9]+})', r'$\1^\2$', text)

    return text

# Charger le fichier JSON
with open('maths.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Parcourir chaque question
for i, item in enumerate(data):
    item['question'] = transform_expression(item['question'])
    for key, choice in item['choices'].items():
        item['choices'][key] = transform_expression(choice)

# Enregistrer le fichier JSON modifié
with open('maths_katex.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)