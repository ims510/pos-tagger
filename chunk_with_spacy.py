"""Ce script propose un chunking avec Spacy"""


from dataclasses import dataclass
from typing import List
import csv
import spacy
nlp = spacy.load('fr_core_news_sm')


@dataclass
class Mot:
    """
    classe qui représente un mot

    Attributes
    ----------
    ID : int
        position du mot dans la phrase
    forme : str
        mot lui-même
    pos : str
        partie du discours du mot
    lemme : str
        lemme du mot
    deprel : str
        relation de dépendance du mot avec son gouverneur
    gouv : str
        gouverneur du mot
    syntagmes : List
        liste des syntagmes auquel appartient le mot
    """
    ID: int
    forme: str
    pos: str
    lemme: str
    deprel: str
    gouv: str
    syntagmes: List[str]


def extraire_sn(text: str) -> List[str] :
    """Extrait les syntagmes nominaux du texte

    Parameters
    ----------
    text : str
        texte à chunker

    Returns
    -------
    List
        liste des syntagmes nominaux du texte
    """
    doc = nlp(text)
    sn = [chunk.text for chunk in doc.noun_chunks]
    return sn


def extraire_sv(text: str) -> List[str] :
    """Extrait les syntagmes verbaux du texte

    Parameters
    ----------
    text : str
        texte à chunker

    Returns
    -------
    List
        liste des syntagmes verbaux du texte
    """
    
    doc = nlp(text)
    sv = []
    for token in doc:
        if token.pos_ == 'VERB':  # Si le token est un verbe
            verb_phrase = [token.text]
            for child in token.children:  # Ajouter les dépendants du verbe
                verb_phrase.append(child.text)
            sv.append(' '.join(verb_phrase))
    return sv


def extraire_sp(text: str) -> List[str] :
    """Extrait les syntagmes prépositionnels du texte

    Parameters
    ----------
    text : str
        texte à chunker

    Returns
    -------
    List
        liste des syntagmes prépositionnels du texte
    """
    
    doc = nlp(text)
    sp = []
    for token in doc:
        if token.dep_ == 'case':  # Si le token est une préposition
            governor = token.head  # Récupérer le gouverneur du token prépositionnel
            prep_phrase = f"{token.text} {governor.text}"
            sp.append(prep_phrase)
    return sp


def mots_in_syntagme(liste_syntagmes: List[str]) -> List[str] : 
    """Retourne la liste de tous les mots appartenant à la liste de syntagmes

    Parameters
    ----------
    liste_syntagmes : List[str]
        liste des syntagmes extraites (ex : liste des syntagmes nominaux)

    Returns
    -------
    List
        liste des mots appartenant à ces syntagmes
    """
    
    mots_in_syntagmes = []
    for syntagme in liste_syntagmes : 
        mots = syntagme.split()
        for mot in mots :
            mots_in_syntagmes.append(mot)
    return mots_in_syntagmes


def analyse_dependances(text: str, sn: List[str], sv: List[str], sp: List[str]) -> List[Mot] :
    """Renvoie la liste des mots avec leurs informations syntaxiques

    Parameters
    ----------
    text : str
        texte qu'on veut analyser
    sn : List[str]
        liste des mots appartenant aux syntagmes nominaux
    sv : List[str]
        liste des mots appartenant aux syntagmes verbaux
    sp : List[str]
        liste des mots appartenant aux syntagmes prépositionnels

    Returns
    -------
    List
        liste des mots avec leurs informations syntaxiques
    """
    
    liste_tokens = []
    doc = nlp(text)

    for index, token in enumerate(doc) :

        ID = index + 1   # Pour que le premier mot ait la position 1
        forme = token.text
        pos = token.pos_
        lemme = token.lemma_
        deprel = token.dep_
        gouv = token.head

        # Trouver son syntagme direct (syntagme auquel il appartient)
        synt = []
        if forme in sn :
            synt.append('SN')
        if forme in sv :
            synt.append('SV')
        if forme in sp :
            synt.append('SP')

        # Trouver l'éventuel syntagme dans lequel se trouve le syntagme auquel il appartient
        if gouv.text in sn :
            if 'SN' not in synt :
                synt.append('SN')
        if gouv.text in sv :
            if 'SV' not in synt :
                synt.append('SV')
        if gouv.text in sp :
            if 'SP' not in synt :
                synt.append('SP')

        # Pour éviter d'aller trop loin dans l'imbrications des syntagmes, on ne garde que le(s) syntagme(s) auquel appartient le mot directement et éventuellement celui de son gouverneur
        while len(synt) > 2 :
            del synt[-1]

        syntagmes = synt
        liste_tokens.append(Mot(ID, forme, pos, lemme, deprel, gouv, syntagmes))
    return liste_tokens


def sauvegarde_csv(liste_mots: List[Mot], fichier: str) -> None : 
    """Sauvegarde le résultat dans un fichier csv

    Parameters
    ----------
    liste_mots : List
        liste des mots avec leurs informations syntaxiques

    Returns
    -------
    None
    """
    
    with open (fichier, "w") as f :
        writer = csv.writer(f)
        writer.writerow(['ID', 'Mot', 'POS', 'Lemme', 'Rel', 'Gouv', 'Syntagmes'])
        for mot in liste_mots : 
            writer.writerow([mot.ID, mot.forme, mot.pos, mot.lemme, mot.deprel, mot.gouv, mot.syntagmes])


def main() : 
    
    # Texte à chunker
    texte = "La maman a un cadeau pour son enfant."
    
    # Extraction des syntagmes
    liste_sn = extraire_sn(texte)
    print(f"Syntagmes nominaux : {liste_sn}")
    liste_sv = extraire_sv(texte)
    print(f"Syntagmes verbaux : {liste_sv}")
    liste_sp = extraire_sp(texte)
    print(f"Syntagmes prépositionnels : {liste_sp}")
    
    # Récupération des mots des syntagmes
    mots_in_sn = mots_in_syntagme(liste_sn)
    mots_in_sv = mots_in_syntagme(liste_sv)
    mots_in_sp = mots_in_syntagme(liste_sp)
    
    # Analyse syntaxique du texte
    tokens = analyse_dependances(texte, mots_in_sn, mots_in_sv, mots_in_sp)
    
    # Sauvegarde de l'analyse syntaxique
    sauvegarde_csv(tokens, "../data/resultat_chunk_spacy.csv")


if __name__ == "__main__":
    main()
