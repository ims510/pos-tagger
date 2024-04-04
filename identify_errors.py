from datastructure import Ligne, Token, Erreur
import csv
from typing import List
from creation_lexique import obtenir_lexique, get_filenames
import spacy

nlp = spacy.load("fr_core_news_sm")

def ouverture_csv(file : str) -> List[Ligne]:
    """Ouvre un fichier csv et retourne une liste de lignes."""
    with open (file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t') ## le delimiter de notre csv c'est des tabs
        next(reader, None)
        liste_lignes = []
        for row in reader:
            line = Ligne(texte_complete=row[16], texte_simple = row[11], tokens=[], categorie=row[15], start_position=int(row[12]), end_position=int(row[13]), doc_length=int(row[14]), id=row[0])
            liste_lignes.append(line)
        return liste_lignes

        # next(reader)
        # lignes = [Ligne(row[0], [Token(row[i], row[i+1], row[i+2]) for i in range(1, len(row)-1, 3)], row[-1]) for row in reader]



def clean_lines(liste_lignes: List[Ligne]) -> List[Ligne]:
    """Nettoie les lignes de la liste."""
    for ligne in liste_lignes:
        ligne.texte_complete = ligne.texte_complete.replace("␣"," ")
        ligne.texte_complete = ligne.texte_complete.replace("⌫","~")
    return liste_lignes
            


def compare_data_lexique(liste_lignes: List[Ligne], lexique: List[str]):
    """Compare les données avec le lexique et retourne une liste d'erreurs."""
    n = 0
    liste_erreurs = []
    for ligne in liste_lignes:
        mots_originaux = nlp(ligne.texte_complete)
        for mot in mots_originaux:
            if mot.text!=" " and mot.text.lower() not in lexique:
                erreur = Erreur(mot, n, "Unknown", mot.pos_)
                liste_erreurs.append(erreur)
                # print(f"{n}. Erreur : {mot}")
                n += 1
    return liste_erreurs

def main():
    liste_lignes = ouverture_csv("/Users/madalina/Documents/M1TAL/Enrichissement de corpus/Docs/csv_planification.csv")
    file_list = get_filenames("22032024/TextesFinaux_txt")
    lexique = obtenir_lexique(file_list)
    liste_lignes = clean_lines(liste_lignes)

    liste_erreurs = compare_data_lexique(liste_lignes, lexique)

    print("Ligne\tMot erroné\tPos réel\tPos supposé\n")
    for error in liste_erreurs:

        print(f"{error.ligne}\t{error.mot_errone}\t{error.pos_reel}\t{error.pos_suppose}")

if __name__ == "__main__":
    main()