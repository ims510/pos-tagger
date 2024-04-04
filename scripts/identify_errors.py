from datastructure import Ligne, Token, Erreur
import csv
from typing import List
from creation_lexique import obtenir_lexique, get_filenames
import spacy
from tqdm import tqdm

nlp = spacy.load("fr_core_news_sm")

def ouverture_csv(file : str) -> List[Ligne]:
    """Ouvre un fichier csv et retourne une liste de lignes."""
    with open (file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=',') ## le delimiter de notre csv c'est des tabs
        liste_lignes = []
        for row in tqdm(reader, desc="Lecture du fichier csv"):
            line = Ligne(texte=row[22], texte_corrige=[], tokens=[], categorie=row[21])
            liste_lignes.append(line)
        return liste_lignes

def clean_lines(liste_lignes: List[Ligne]) -> List[Ligne]:
    """Nettoie les lignes de la liste."""
    for ligne in liste_lignes:
        ligne.texte = ligne.texte.replace("␣"," ")
        ligne.texte = ligne.texte.replace("⌫","~")
    return liste_lignes



def compare_data_lexique(liste_lignes: List[Ligne], lexique: List[str]):
    """Compare les données avec le lexique et retourne une liste d'erreurs."""
    n = 0
    liste_erreurs = []
    for ligne in liste_lignes:
        mots_originaux = nlp(ligne.texte)
        for mot in mots_originaux:
            if mot.text!=" " and mot.text.lower() not in lexique:
                erreur = Erreur(mot, n, "Unknown", mot.pos_)
                liste_erreurs.append(erreur)
                # print(f"{n}. Erreur : {mot}")
                n += 1
    return liste_erreurs
            
### cas où le la suppression se passe sur la même ligne
def suppression_interne_mots_meme_ligne(liste_lignes: List[Ligne]) -> List[Ligne]:
    """Suppression du nombre de ~ et du nombre de caractère associé pour permettre la concaténation d'un mot correct """

    for ligne in liste_lignes:
        nouvelle_phrase = ""
        if ligne.texte.startswith("~"):
            continue
        for char in ligne.texte:
            if char == "~":
                nouvelle_phrase = nouvelle_phrase[:-1]  
            else:
                nouvelle_phrase += char
        ligne.texte_corrige = nouvelle_phrase  

    return liste_lignes


          
def suppression_interne_mots_sur_plusieurs_lignes(liste_lignes: List[Ligne]) -> List[Ligne]: 
    """Suppression des caractères précédents sur plusieurs lignes si la première ligne commence par un ~."""
    for i, line in enumerate(liste_lignes):
        if line.texte.startswith('~'):
            if i > 0: ## récupération de la ligne précédante
                ligne_precedente = liste_lignes[i - 1]
                print("Ligne précédente :", ligne_precedente)
    return liste_lignes
            

def main():
    liste_lignes = ouverture_csv("../data/csv_planification.csv")
    file_list = get_filenames("TextesFinaux_txt")
    lexique = obtenir_lexique(file_list)
    liste_erreurs = compare_data_lexique(liste_lignes, lexique)
    print(liste_erreurs)
    liste_lignes = clean_lines(liste_lignes)
    print(liste_lignes)
    # lignes_supprime = suppression_interne_mots_meme_ligne(liste_lignes)
    # print(lignes_supprime)
    # test = suppression_interne_mots_meme_ligne(liste_lignes)
    # print(test)
if __name__ == "__main__":
    main()