from datastructure import Ligne, Token, Difference
import csv
from typing import List
from creation_lexique import obtenir_lexique, get_filenames


'''import nltk
from nltk.tokenize import word_tokenize
nltk.download('punkt')


import treetaggerwrapper

# Spécifier le chemin vers les fichiers TreeTagger
TAGGER_PATH = '/home/amandine/Tagger'

# Initialisation de TreeTagger
tagger = treetaggerwrapper.TreeTagger(TAGLANG='fr', TAGDIR=TAGGER_PATH)

'''

import spacy
nlp = spacy.load("fr_core_news_sm")

def ouverture_csv(file : str) -> List[Ligne]:
    """Ouvre un fichier csv et retourne une liste de lignes."""
    with open (file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t') ## le delimiter de notre csv c'est des tabs
        next(reader, None)
        liste_lignes = []
        for row in reader:
            
            #line = Ligne(charBurst=row[16], texte_simple = row[11], categorie=row[15], start_position=int(row[12]), end_position=int(row[13]), doc_length=int(row[14]), id=row[0], n_burst=int(row[3]))
            
            line = Ligne(
                ID=row[0], 
                charge=row[1], 
                outil=row[2], 
                n_burst=int(row[3]), 
                debut_burst=float(row[4].replace(',', '.')) if row[4] else None, 
                duree_burst=float(row[5].replace(',', '.')) if row[5] else None, 
                duree_pause=float(row[6].replace(',', '.')) if row[6] else None, 
                duree_cycle=float(row[7].replace(',', '.')) if row[7] else None, 
                pct_burst=float(row[8].replace(',', '.')) if row[8] else None, 
                pct_pause=float(row[9].replace(',', '.')) if row[9] else None, 
                longueur_burst=int(row[10]), 
                burst=row[11], 
                startPos=int(row[12]), 
                endPos=int(row[13]), 
                docLength=int(row[14]), 
                categ=row[15], 
                charBurst=row[16], 
                ratio=float(row[17].replace(',', '.')) if row[17] else None
                )
            
            liste_lignes.append(line)
                
        return liste_lignes

        # next(reader)
        # lignes = [Ligne(row[0], [Token(row[i], row[i+1], row[i+2]) for i in range(1, len(row)-1, 3)], row[-1]) for row in reader]



def clean_lines(liste_lignes: List[Ligne]) -> List[Ligne]:
    """Nettoie les lignes de la liste."""
    for ligne in liste_lignes:
        ligne.charBurst = ligne.charBurst.replace("␣"," ")
    return liste_lignes
            


def compare_data_lexique(liste_lignes: List[Ligne], lexique: List[str]):
    """Compare les données avec le lexique et retourne une liste d'erreurs."""
    n = 0
    liste_erreurs = []
    for ligne in liste_lignes:
        mots_originaux = nlp(ligne.charBurst)
        mots_originaux = ligne.charBurst.split()
        
        
        for mot in mots_originaux:
            if mot.text!=" " and mot.text.lower() not in lexique:
                erreur = Difference(mot, n, "Unknown", mot.pos_)
                liste_erreurs.append(erreur)
                # print(f"{n}. Erreur : {mot}")
                n += 1
    return liste_erreurs


'''def compare_data_lexique(liste_lignes: List[Ligne], lexique: List[str]):
    """Compare les données avec le lexique et retourne une liste d'erreurs."""
    n = 0
    liste_erreurs = []
    for ligne in liste_lignes:
        charburst = ligne.charBurst
        
        
        #tokens = word_tokenize(charburst)
        tokens = nlp(charburst)
        
        
        for token in tokens :
            print(token)
            if token!=" " and token.lower() not in lexique:
                erreur = Difference(token, n, "Unknown", 'pos')
                liste_erreurs.append(erreur)
                # print(f"{n}. Erreur : {mot}")
                n += 1
    return liste_erreurs
'''


def main():
    liste_lignes = ouverture_csv("CLEAN_csv_planification.tsv")
    file_list = get_filenames("TextesFinaux_txt")
    lexique = obtenir_lexique(file_list)
    liste_lignes = clean_lines(liste_lignes)

    liste_erreurs = compare_data_lexique(liste_lignes, lexique)

    print("Ligne\tMot erroné\tPos réel\tPos supposé\n")
    for error in liste_erreurs:

        print(f"{error.ligne}\t{error.mot_errone}\t{error.pos_reel}\t{error.pos_suppose}")

if __name__ == "__main__":
    main()