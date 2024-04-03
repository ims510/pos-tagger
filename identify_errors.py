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
        reader = csv.reader(f, delimiter='\t') ## le delimiter de notre csv c'est des tabs
        liste_lignes = []
        for row in tqdm(reader, desc="Lecture du fichier csv"):
            line = Ligne(texte=row[16], tokens=[], categorie=row[15])
            liste_lignes.append(line)
        return liste_lignes


liste_lignes = ouverture_csv("csv_planification.csv")



def clean_lines(liste_lignes: List[Ligne]) -> List[Ligne]:
    """Nettoie les lignes de la liste."""
    for ligne in liste_lignes:
        ligne.texte = ligne.texte.replace("␣"," ")
        ligne.texte = ligne.texte.replace("⌫","~")
    return liste_lignes
            

file_list = get_filenames("TextesFinaux_txt")
lexique = obtenir_lexique(file_list)
liste_lignes = clean_lines(liste_lignes)


def compare_data_lexique(liste_lignes: List[Ligne], lexique: List[str]):
    """Compare les données avec le lexique et retourne une liste d'erreurs."""
    n = 0
    liste_erreurs = []
    for ligne in tqdm(liste_lignes, desc="Détection des erreurs"):
        mots_originaux = nlp(ligne.texte)
        for mot in mots_originaux:
            if mot.text!=" " and mot.text.lower() not in lexique:
                erreur = Erreur(str(mot), n, "Unknown", mot.pos_)
                liste_erreurs.append(erreur)
                # print(f"{n}. Erreur : {mot}")
                n += 1
    return liste_erreurs

liste_erreurs = compare_data_lexique(liste_lignes, lexique)


###############################################################################

def annotate_corpus(corpus: List[Ligne]) -> List[Ligne] : 
    '''Ajoute les tokens à chaque ligne du corpus'''
    corpus_annote = []
    for ligne in tqdm(corpus, desc="Annotation du corpus") : 
        tokens = nlp(ligne.texte)
        liste_tokens = []
        for token in tokens : 
            token = Token(token.text, token.pos_, token.lemma_, "erreur")
            liste_tokens.append(token)
        ligne.tokens = liste_tokens
        corpus_annote.append(ligne)
    return(corpus_annote)
        
corpus_annote = annotate_corpus(liste_lignes)



def extract_burst(file : str) -> List[str]:
    '''Ouvre un fichier csv et retourne une liste de lignes.'''
    with open (file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t') ## le delimiter de notre csv c'est des tabs
        liste_lignes = []
        for row in tqdm(reader, desc="Extraction du burst"):
            line = str(row[11])
            liste_lignes.append(line)
        return liste_lignes

burst = extract_burst('csv_planification.csv')



def Ligne_burst(corpus: List[Ligne], burst: str) -> List[List] : 
    '''prend en entrée le corpus annoté et la liste de burst et ajoute le burst à chaque ligne'''
    # Convertir chaque Ligne en liste
    corpus_liste = []
    for ligne in corpus : 
        ligne_liste = [ligne.texte, ligne.tokens, ligne.categorie]
        corpus_liste.append(ligne_liste)
    # Ajouter chaque burst à la ligne correspondante
    corpus_avec_burst = []
    for i in range(len(corpus_liste)) : 
        corpus_liste[i].append(burst[i])
        corpus_avec_burst.append(corpus_liste[i])
    return corpus_avec_burst

corpus_burst = Ligne_burst(corpus_annote, burst)



def mots_colles_burst(corpus_avec_burst: List[List]) -> List[List] : 
    '''prend en entrée le corpus de lignes sous forme de listes avec le burst et immite les mots_colles dans le burst'''
    liste_burst = []
    for ligne in corpus_avec_burst : 
        burst = ligne[3]
        liste_mots = burst.split()        
        coller_ligne = []
        for i in range(len(liste_mots)-1) : 
            coller = liste_mots[i]+liste_mots[i+1]
            coller_ligne.append(coller)
        ligne[3] = coller_ligne
        liste_burst.append(ligne)
    return liste_burst

corpus_avec_burst_colles = mots_colles_burst(corpus_burst)



def detecter_mots_colles(corpus_burst_colles: List[List]) -> List[Ligne] : 
    '''détecte les mots collés dans les lignes sous forme de listes et renvoie toutes les lignes avec l'erreur "mots collés" si détecté'''
    corpus_erreur = []
    for ligne in corpus_burst_colles : 
        for token in ligne[1] : 
            if token.texte in ligne[3] : 
                token.erreur = "mots collés"
    for ligne_liste in corpus_burst_colles : 
        ligne = Ligne(ligne_liste[0], ligne_liste[1], ligne_liste[2])
        corpus_erreur.append(ligne)
    #print(corpus_erreur)
    return corpus_erreur

corpus_mots_colles = detecter_mots_colles(corpus_avec_burst_colles)

