"""Ce script propose un chunking avec Spacy"""



from datastructures_chunking import Mot, Phrase, extraire_chunks
from typing import List
import csv
from tqdm import tqdm
import argparse
import spacy
nlp = spacy.load('fr_core_news_sm')



def open_txt(fichier: str) -> str :
    """Ouvre le fichier txt contenant le texte à chunker

    Parameters
    ----------
    fichier : str
        chemin du fichier contenant le texte à chunker

    Returns
    -------
    str
        texte à chunker
    """
    with open(fichier, 'r') as f :
        content = f.read().strip()
    return content



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
    for sent in tqdm(doc.sents, desc='Découpage du texte en phrases') :
        sentences.append(sent.text)
    return sentences



def mots_in_chunk(liste_chunks: List[str]) -> List[str] :
    """Retourne la liste de tous les mots appartenant à la liste de chunks

    Parameters
    ----------
    liste_chunks : List[str]
        liste des chunks extraits (ex : liste des chunks nominaux)

    Returns
    -------
    List
        liste des mots appartenant à ces chunks
    """

    mots_in_chunks = []
    for chunk in liste_chunks :
        mots = chunk.split()
        for mot in mots :
            mots_in_chunks.append(mot)
    return mots_in_chunks



def analyse_dependances(text: str, sn: List[str], sv: List[str], sp: List[str]) -> List[Mot] :
    """Renvoie la liste des mots avec leurs informations syntaxiques

    Parameters
    ----------
    text : str
        texte qu'on veut analyser
    sn : List[str]
        liste des mots appartenant aux chunks nominaux
    sv : List[str]
        liste des mots appartenant aux chunks verbaux
    sp : List[str]
        liste des mots appartenant aux chunks prépositionnels

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

        # Trouver son chunk direct (chunk auquel il appartient)
        synt = []
        if forme in sn :
            synt.append('SN')
        if forme in sv :
            synt.append('SV')
        if forme in sp :
            synt.append('SP')

        # Trouver l'éventuel chunk dans lequel se trouve le chunk auquel il appartient
        if gouv.text in sn :
            if 'SN' not in synt :
                synt.append('SN')

        if gouv.text in sp :
            if 'SP' not in synt :
                synt.append('SP')

        if gouv.text in sv and deprel != 'mark' : # si le gouverneur du token est dans un groupe verbal ET que le token n’est pas relié au gouverneur par une relation “mark”
            if 'SV' not in synt :
                synt.append('SV')

        # Pour éviter d'aller trop loin dans l'imbrications des chunks, on ne garde que le(s) chunk(s) auquel appartient le mot directement et éventuellement celui de son gouverneur
        while len(synt) > 2 :
            del synt[-1]

        chunks = synt
        liste_tokens.append(Mot(ID, forme, pos, lemme, deprel, gouv, chunks))

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

    # Récupérer les mots des chunks pour chaque phrase
    for sent in tqdm(phrases, desc='Analyse syntaxique du texte') :
        mots_in_sn = mots_in_chunk(sent.sn)
        mots_in_sv = mots_in_chunk(sent.sv)
        mots_in_sp = mots_in_chunk(sent.sp)

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
             'chunks',
             'ID Phrase',
             'Phrase',
             'chunks nominaux',
             'chunks verbaux',
             'chunks prépositionnels']
            )

        for phrase in tqdm(liste_phrases, desc="Sauvegarde de l'analyse") :
            for mot in phrase.mots :
                writer.writerow(
                    [mot.ID,
                     mot.forme,
                     mot.pos,
                     mot.lemme,
                     mot.deprel,
                     mot.gouv,
                     mot.chunks,
                     phrase.ID,
                     phrase.phrase,
                     phrase.sn,
                     phrase.sv,
                     phrase.sp]
                    )

    print(f"Les données ont bien été sauvegardées dans le fichier {fichier}.")



def main() :

    # Gérer les arguments
    parser = argparse.ArgumentParser(description="Chunking d'un texte")
    parser.add_argument("-i", "--input-file", type=str, default="../data/raw/fichier_a_chunker.txt", help="Chemin du fichier txt à chunker")
    parser.add_argument("-o", "--output-file", type=str, default="../data/clean/resultat_chunk_spacy.csv", help="Chemin du fichier csv contenant l'analyse syntaxique")
    args = parser.parse_args()

    # Ouvrir le fichier a chunker
    texte = open_txt(args.input_file)

    # Spliter le texte en phrases
    phrases = split_sentences(texte)

    # Chunker chaque phrase du texte
    liste_chunks = extraire_chunks(phrases)
    print(liste_chunks)

    # Analyser syntaxiquement chaque phrase
    phrases_annotees = analyse_syntaxique(liste_chunks)

    # Sauvegarde de l'analyse syntaxique dans un csv
    sauvegarde_csv(phrases_annotees, args.output_file)



if __name__ == "__main__":
    main()
