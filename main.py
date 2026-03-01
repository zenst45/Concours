import json
import maths_utils

print(
    """1. Maths
2. Anglais
3. Stats"""
    )
choix = input()
if choix == "1" or 1==1:
    print(
        """Entrainement de 10 questions par thèmes (1-10) ou complet (0):
0. Complet
1. Dérivées
2. Suites
3. Limites
4. Logarithme et exponentielle
5. Domaine de définition
6. Primitives et équations différentielles
7. Dénombrement et probabilités
8. Géométrie dans l’espace
9. Fonctions sinus et cosinus / Trigonométrie
10. Calcul intégral"""
          )
    choix_maths = input()
    if choix_maths == "0":
        maths_utils.complet()
    else:
        maths_utils.themes(int(choix_maths))
elif choix == "2":
    pass
elif choix == "3":
    pass
