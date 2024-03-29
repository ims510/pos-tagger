from datastructure import Ligne
import csv
from typing import List




def ouverture_csv(file : str) -> List[Ligne]:
    """Ouvre un fichier csv et retourne une liste de lignes."""
    with open (file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=',') ## le delimiter de notre csv c'est des tabs MAIS ATTENTION SUR MA VERSION J'UTILISE DES VIRGULES
        liste_lignes = []
        for row in reader:
            print(row[14])
        #     line = Ligne(texte=row[16], tokens=[], categorie=row[15])
        #     liste_lignes.append(line)
        # return liste_lignes

        
print(ouverture_csv("./data/csv_planification.csv"))