"""Ce script contient la dÃ©finition de la classe Mot et de la classe Phrase, ainsi que l'extraction des syntagmes."""



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
    classe qui represente une phrase

    Attributes
    ----------
    ID : int
        position de la phrase dans le texte
    phrase : str
        phrase elle-meme
    sn : List
        liste des syntagmes nominaux de la phrase
    sv : List
        liste des syntagmes verbaux de la phrase
    sp : List
        liste des syntagmes prepositionnels de la phrase
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
        phrase a chunker

    Returns
    -------
    List
        liste des syntagmes nominaux de la phrase
    """
    
    doc = nlp(sentence)
    
    # Extraire les SN avec Spacy 
    sn_spacy = [chunk.text for chunk in doc.noun_chunks]
    
    # Trouver les noms qui n'ont pas de determinant dans les SN extraits par spacy
    noms_sans_det = []
    for synt in sn_spacy : 
        if len(synt.split()) == 1 : 
            doc = nlp(synt)
            for mot in doc : 
                if mot.pos_ == 'NOUN' or mot.pos_ == 'PROPN' : 
                    noms_sans_det.append(mot.text)
    
    # Parmi les nom sans determinants, si on trouve dans le texte un dpendant qui est lie ˆ lui par une relation "dep", 
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
    """Extrait les syntagmes verbaux de la phrase

    Parameters
    ----------
    sentence : str
        phrase a chunker

    Returns
    -------
    List
        liste des syntagmes verbaux de la phrase
    """
    
    doc = nlp(sentence)
    sv = []
    
    for token in doc :
        if token.pos_ == 'VERB' and token.dep_ != 'xcomp' :  # Si le token est un verbe pas complement
            verb_phrase = [(token, token.i)]   # On ajoute le verbe ˆ la liste avec sa position
            
            # On parcourt les dpendants du verbe
            for child in token.children :
                
                # Si le dependant est relie au verbe par "xcomp", on ajoute ses dependants
                # Sauf s'ils sont relies a ce dependant par "mark" ou "advcl"
                if child.dep_ == "xcomp" :
                    enfant = child
                    for enfant in enfant.children :
                        if enfant.dep_ != 'mark' and enfant.dep_ != 'advcl' :
                            verb_phrase.append((enfant, enfant.i))
                
                # Si le dependant n'est pas relie au verbe par "mark" ou "advcl" on l'ajoute
                if child.dep_ != 'mark' and child.dep_ != 'advcl' :
                    verb_phrase.append((child, child.i))
            
            # On trie les tokens par leur position
            verb_phrase = sorted(verb_phrase, key=lambda x: x[1])
            
            # On extrair le texte des tokens tries et on cree le syntagme verbal
            verb_phrase_text = ' '.join([tok[0].text for tok in verb_phrase])
            sv.append(verb_phrase_text)

    return sv
    


def extraire_sp(sentence: str) -> List[str] :
    """Extrait les syntagmes prÃ©positionnels de la phrase

    Parameters
    ----------
    sentence : str
        phrase a chunker

    Returns
    -------
    List
        liste des syntagmes prepositionnels de la phrase
    """
    
    doc = nlp(sentence)
    sp = []
    
    for token in doc :
        
        # Si le token est une preposition et qu'il n'a pas de relation 'det' (evite d'extraire les articles partitifs)
        if token.pos_ == 'ADP' and token.dep_ != 'det' :
            prep_phrase = [(token, token.i)]
            
            # Recuperer le gouverneur du token prepositionnel et l'ajouter ˆ l'extraction
            governor = token.head
            
            # Si le gouverneur est un nom ou un nom propre, on regarde ses dependants
            if governor.pos_ == 'NOUN' or governor.pos_ == 'PROPN' :
                for child in governor.children :
                    
                    # Si le dependant du gouverneur est lie a lui par une relation 'det'
                    # alors on l'extrait
                    if child.dep_ == 'det' :
                        prep_phrase.append((child, child.i))
            
            prep_phrase.append((governor, governor.i))
            
            # Si le gouverneur est un verbe, on regarde ses dependants
            if governor.pos_ == 'VERB' :
                
                # S'il possede un dependant qui est son objet alors on ajoute cet objet a l'extraction
                for child in governor.children:
                    if child.dep_ == 'obj' :
                        prep_phrase.append((child, child.i))
            
            # On trie les tokens par leur position
            prep_phrase = sorted(prep_phrase, key=lambda x: x[1])
            
            # On extrait le texte des tokens tries et on cree le syntagme prepositionnel
            prep_phrase_text = ' '.join([tok[0].text for tok in prep_phrase])
            sp.append(prep_phrase_text)

    # Comparaison des SP avec les SN
    sn = extraire_sn(sentence)
    
    # Pour chaque sp extrait, s'il appartient aux sn extraits alors on le supprime des sp
    sp = [synt for synt in sp if synt not in sn]
            
    return sp



def extraire_syntagmes(sentences: List[str]) -> List[Phrase] : 
    """Extrait tous les syntagmes de chaque phrase d'un texte

    Parameters
    ----------
    sentences : List
        liste des phrases Ã  chunker

    Returns
    -------
    List
        liste des phrases chunkÃ©es
    """
    
    syntagmes = []
    n = 0
    
    for sent in tqdm(sentences, desc='Extraction des syntagmes') : 
        
        # NumÃ©ro de la phrase dans le texte
        n += 1
        
        # Extraire les syntagmes
        liste_sn = extraire_sn(sent)
        liste_sv = extraire_sv(sent)
        liste_sp = extraire_sp(sent)
        
        # Ajouter les phrases chunkÃ©es Ã  la liste de syntagmes
        phrase_chunkee = Phrase(n, sent, liste_sn, liste_sv, liste_sp, [])
        syntagmes.append(phrase_chunkee)
        
    return syntagmes