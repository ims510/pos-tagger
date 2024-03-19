from datastructure import Ligne, Token
import csv
from typing import List




def ouverture_csv(file : str) -> List[Ligne]:
    """Ouvre un fichier csv et retourne une liste de lignes."""
    with open (file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t') ## le delimiter de notre csv c'est des tabs
        liste_lignes = []
        for row in reader:
            line = Ligne(texte=row[16], tokens=[], categorie=row[15])
            liste_lignes.append(line)
        return liste_lignes

        # next(reader)
        # lignes = [Ligne(row[0], [Token(row[i], row[i+1], row[i+2]) for i in range(1, len(row)-1, 3)], row[-1]) for row in reader]

print(ouverture_csv("/Users/madalina/Documents/M1TAL/Enrichissement de corpus/Docs/csv_planification.csv"))