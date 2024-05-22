"""Ce script contient la definition de la classe Mot et de la classe Phrase, ainsi que l'extraction des chunks."""



from dataclasses import dataclass
from typing import List
from tqdm import tqdm
import spacy
nlp = spacy.load('fr_core_news_sm')



@dataclass
class Mot:
    """
    classe qui represente un mot

    Attributes
    ----------
    ID : int
        position du mot dans la phrase
    forme : str
        mot lui-meme
    pos : str
        partie du discours du mot
    lemme : str
        lemme du mot
    deprel : str
        relation de dependance du mot avec son gouverneur
    gouv : str
        gouverneur du mot
    chunks : List
        liste des chunks auquel appartient le mot
    """
    ID: int
    forme: str
    pos: str
    lemme: str
    deprel: str
    gouv: str
    chunks: List[str]



@dataclass
class Phrase:
    """
    classe qui represente une phrase

    Attributes
    ----------
    ID : int
        position de la phrase dans le texte
    phrase : str
        phrase elle-meme
    sn : List
        liste des chunks nominaux de la phrase
    sv : List
        liste des chunks verbaux de la phrase
    sp : List
        liste des chunks prepositionnels de la phrase
    mots: List
        liste des mots de la phrase
    """
    ID: int
    phrase: str
    sn: List
    sv: List
    sp: List
    mots: List



def extraire_sn(sentence: str) -> List[str] :
    """Extrait les chunks nominaux de la phrase

    Parameters
    ----------
    sentence : str
        phrase a chunker

    Returns
    -------
    List
        liste des chunks nominaux de la phrase
    """

    doc = nlp(sentence)

    # Extraire les SN avec Spacy
    sn_spacy = [chunk.text for chunk in doc.noun_chunks]

    # Identifier les sn qui sont en realite des sp
    faux_sn = []
    for mot in doc :
        if mot.pos_ == 'NOUN' or mot.pos_ == 'PRON' :
            for child in mot.children :
                if child.pos_ == 'ADP' :
                    for child in mot.children :
                        if child.pos_ == 'DET' or child.dep_ == 'det' :
                            couple = child.text + ' ' + mot.text
                            faux_sn.append(couple)

    # Supprimer les faux sn de la liste
    for sn in sn_spacy :
        if sn in faux_sn :
            sn_spacy.remove(sn)

    # Trouver les noms qui n'ont pas de determinant dans les SN extraits par spacy
    noms_sans_det = []
    for synt in sn_spacy :
        if len(synt.split()) == 1 :
            doc = nlp(synt)
            for mot in doc :
                if mot.pos_ == 'NOUN' or mot.pos_ == 'PROPN' :
                    noms_sans_det.append(mot.text)

    # Parmi les nom sans determinants, si on trouve dans le texte un dépendant qui est lie à lui par une relation "dep",
    # alors on ajoute le couple (det, nom) a la liste des sn extraits par spacy
    doc = nlp(sentence)
    for token in doc :
        if token.pos_ == 'NOUN' or token.pos_ == 'PROPN' :
            if token.text in noms_sans_det :
                for child in token.children :
                    if child.dep_ == 'det' :
                        couple = child.text + ' ' + token.text
                        sn_spacy.append(couple)

    # On supprime le nom sans determinant de la liste des sn
    for token in doc :
        if token.pos_ == 'NOUN' or token.pos_ == 'PROPN' :
            if token.text in noms_sans_det :
                if token.text in sn_spacy :
                    sn_spacy.remove(token.text)

    return sn_spacy



def extraire_sv(sentence: str) -> List[str] :
    """Extrait les chunks verbaux de la phrase

    Parameters
    ----------
    sentence : str
        phrase a chunker

    Returns
    -------
    List
        liste des chunks verbaux de la phrase
    """

    doc = nlp(sentence)
    sv = []

    for token in doc :
        if token.pos_ == 'VERB' :
            sv.append(token.text)

    return sv



def extraire_sp(sentence: str) -> List[str] :
    """Extrait les chunks prepositionnels de la phrase

    Parameters
    ----------
    sentence : str
        phrase a chunker

    Returns
    -------
    List
        liste des chunks prepositionnels de la phrase
    """

    doc = nlp(sentence)
    sp = []

    for token in doc :

        # Si le token est une preposition et qu'il n'a pas de relation 'det' (evite d'extraire les articles partitifs)
        if token.pos_ == 'ADP' and token.dep_ != 'det' :
            prep_phrase = [(token, token.i)]

            # Recuperer le gouverneur du token prepositionnel et l'ajouter à l'extraction si c'est un nom
            governor = token.head

            # Si le gouverneur est un nom ou un nom propre, on regarde ses dependants
            if governor.pos_ == 'NOUN' or governor.pos_ == 'PROPN' :
                for child in governor.children :

                    # Si le dependant du gouverneur est lie a lui par une relation 'det'
                    # alors on l'extrait
                    if child.dep_ == 'det' :
                        prep_phrase.append((child, child.i))

                prep_phrase.append((governor, governor.i))

            # On trie les tokens par leur position
            prep_phrase = sorted(prep_phrase, key=lambda x: x[1])

            # On extrait le texte des tokens tries et on cree le chunk prepositionnel
            prep_phrase_text = ' '.join([tok[0].text for tok in prep_phrase])
            sp.append(prep_phrase_text)

    # Comparaison des SP avec les SN
    sn = extraire_sn(sentence)

    # Pour chaque sp extrait, s'il appartient aux sn extraits alors on le supprime des sp
    sp = [synt for synt in sp if synt not in sn]

    return sp



def extraire_chunks(sentences: List[str]) -> List[Phrase] :
    """Extrait tous les chunks de chaque phrase d'un texte

    Parameters
    ----------
    sentences : List
        liste des phrases a chunker

    Returns
    -------
    List
        liste des phrases chunkees
    """

    chunks = []
    n = 0

    for sent in tqdm(sentences, desc='Extraction des chunks') :

        # Numero de la phrase dans le texte
        n += 1

        # Extraire les chunks
        liste_sn = extraire_sn(sent)
        liste_sv = extraire_sv(sent)
        liste_sp = extraire_sp(sent)

        # Ajouter les phrases chunkees a la liste de chunks
        phrase_chunkee = Phrase(n, sent, liste_sn, liste_sv, liste_sp, [])
        chunks.append(phrase_chunkee)

    return chunks
