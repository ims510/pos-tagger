"""Ce script propose un chunking avec Spacy"""



from datastructures_chunking import Mot, Phrase, extraire_syntagmes
from typing import List
import csv
import spacy
nlp = spacy.load('fr_core_news_sm')



def split_sentences(text: str) -> List[str] :
    """Sépare le texte en phrases

    Parameters
    ----------
    text : str
        texte qu'on veut séparer en phrases

    Returns
    -------
    List
        liste des phrases du texte
    """
    
    doc = nlp(text)
    sentences = []
    for sent in doc.sents:
        sentences.append(sent.text)
    return sentences



def mots_in_syntagme(liste_syntagmes: List[str]) -> List[str] : 
    """Retourne la liste de tous les mots appartenant à la liste de syntagmes

    Parameters
    ----------
    liste_syntagmes : List[str]
        liste des syntagmes extraits (ex : liste des syntagmes nominaux)

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
    doc = nlp(text.phrase)

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



def analyse_syntaxique(phrases: List[Phrase]) -> List[Phrase] : 
    """Analyse syntaxiquement chaque phrase du texte

    Parameters
    ----------
    phrases : List
        liste des phrases analysées

    Returns
    -------
    List
        liste des phrases chunkées
    """
    
    phrases_completes = []
    
    # Récupérer les mots des syntagmes pour chaque phrase
    for sent in phrases : 
        mots_in_sn = mots_in_syntagme(sent.sn)
        mots_in_sv = mots_in_syntagme(sent.sv)
        mots_in_sp = mots_in_syntagme(sent.sp)
    
        # Analyse syntaxique du texte
        tokens = analyse_dependances(sent, mots_in_sn, mots_in_sv, mots_in_sp)
        sent.mots = tokens
        phrases_completes.append(sent)
    
    return phrases_completes



def sauvegarde_csv(liste_phrases: List[Phrase], fichier: str) -> None : 
    """Sauvegarde les phrases annotées dans un fichier csv

    Parameters
    ----------
    liste_phrases : List
        liste des phrases annotées
    fichier : str
        fichier dans lequel on veut sauvegarder les données

    Returns
    -------
    None
    """    
    
    with open (fichier, "w") as f :
        writer = csv.writer(f)
        
        writer.writerow(
            ['ID mot', 
             'Mot', 
             'POS', 
             'Lemme', 
             'Deprel', 
             'Gouverneur', 
             'Syntagmes', 
             'ID Phrase', 
             'Phrase', 
             'Syntagmes nominaux', 
             'Syntagmes verbaux', 
             'Syntagmes prépositionnels']
            )
        
        for phrase in liste_phrases : 
            for mot in phrase.mots : 
                writer.writerow(
                    [mot.ID, 
                     mot.forme, 
                     mot.pos, 
                     mot.lemme, 
                     mot.deprel, 
                     mot.gouv, 
                     mot.syntagmes, 
                     phrase.ID, 
                     phrase.phrase, 
                     phrase.sn, 
                     phrase.sv, 
                     phrase.sp]
                    )
    
    print(f"Les données ont bien été sauvegardées dans le fichier {fichier}.")



def main() : 
    
    # Texte à chunker
    texte = "La maman a un cadeau pour son enfant. Je vais apporter cette tarte à la voisine pour qu'elle me remercie. Pour faire un gâteau il faut du beurre et de la farine."
    
    # Spliter le texte en phrases
    phrases = split_sentences(texte)
    
    # Chunker chaque phrase du texte
    phrases_chunkees = extraire_syntagmes(phrases)
    
    # Analyser syntaxiquement chaque phrase
    phrases_annotees = analyse_syntaxique(phrases_chunkees)
    
    # Sauvegarde de l'analyse syntaxique dans un csv
    sauvegarde_csv(phrases_annotees, "../data/resultat_chunk_spacy.csv")



if __name__ == "__main__":
    main()
