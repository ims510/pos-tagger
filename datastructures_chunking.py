"""Ce script contient la définition de la classe Mot et de la classe Phrase, ainsi que l'extraction des syntagmes."""



from dataclasses import dataclass
from typing import List
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



@dataclass
class Phrase:
    """
    classe qui représente une phrase

    Attributes
    ----------
    ID : int
        position de la phrase dans le texte
    phrase : str
        phrase elle-même
    sn : List
        liste des syntagmes nominaux de la phrase
    sv : List
        liste des syntagmes verbaux de la phrase
    sp : List
        liste des syntagmes prépositionnels de la phrase
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
    """Extrait les syntagmes nominaux de la phrase

    Parameters
    ----------
    sentence : str
        phrase à chunker

    Returns
    -------
    List
        liste des syntagmes nominaux de la phrase
    """
    doc = nlp(sentence)
    sn = [chunk.text for chunk in doc.noun_chunks]
    return sn



def extraire_sv(sentence: str) -> List[str] :
    """Extrait les syntagmes verbaux de la phrase

    Parameters
    ----------
    sentence : str
        phrase à chunker

    Returns
    -------
    List
        liste des syntagmes verbaux de la phrase
    """
    
    doc = nlp(sentence)
    sv = []
    for token in doc:
        if token.pos_ == 'VERB':  # Si le token est un verbe
            verb_phrase = [token.text]
            for child in token.children:  # Ajouter les dépendants du verbe
                verb_phrase.append(child.text)
            sv.append(' '.join(verb_phrase))
    return sv



def extraire_sp(sentence: str) -> List[str] :
    """Extrait les syntagmes prépositionnels de la phrase

    Parameters
    ----------
    sentence : str
        phrase à chunker

    Returns
    -------
    List
        liste des syntagmes prépositionnels de la phrase
    """
    
    doc = nlp(sentence)
    sp = []
    for token in doc:
        if token.dep_ == 'case':  # Si le token est une préposition
            governor = token.head  # Récupérer le gouverneur du token prépositionnel
            prep_phrase = f"{token.text} {governor.text}"
            sp.append(prep_phrase)
    return sp



def extraire_syntagmes(sentences: List[str]) -> List[Phrase] : 
    """Extrait tous les syntagmes de chaque phrase d'un texte

    Parameters
    ----------
    sentences : List
        liste des phrases à chunker

    Returns
    -------
    List
        liste des phrases chunkées
    """
    
    syntagmes = []
    n = 0
    
    for sent in sentences : 
        
        # Numéro de la phrase dans le texte
        n += 1
        
        # Extraire les syntagmes
        liste_sn = extraire_sn(sent)
        liste_sv = extraire_sv(sent)
        liste_sp = extraire_sp(sent)
        
        # Ajouter les phrases chunkées à la liste de syntagmes
        phrase_chunkee = Phrase(n, sent, liste_sn, liste_sv, liste_sp, [])
        syntagmes.append(phrase_chunkee)
        
    return syntagmes