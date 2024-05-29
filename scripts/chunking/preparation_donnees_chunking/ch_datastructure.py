from dataclasses import dataclass
from typing import List
import treetaggerwrapper

# Spécifier le chemin vers les fichiers TreeTagger
TAGGER_PATH = '/home/amandine/Tagger'

# Initialisation de TreeTagger
tagger = treetaggerwrapper.TreeTagger(TAGLANG='fr', TAGDIR=TAGGER_PATH)


import spacy
nlp = spacy.load("fr_core_news_sm")

@dataclass
class Difference:
    """Classe représentant une erreur."""
    mot_errone: str
    ligne: int
    pos_reel:str
    pos_suppose:str



@dataclass
class Ligne:
    """Classe représentant une ligne du fichier de données."""
    ID: str
    charge: str
    outil: str
    n_burst: int
    debut_burst: float
    duree_burst: float
    duree_pause: float
    duree_cycle: float
    pct_burst: float
    pct_pause: float
    longueur_burst: int
    burst: str
    startPos	: str
    endPos: str
    docLength: int
    categ: str
    charBurst: str
    ratio: float
    

@dataclass
class AnLine:
    """Classe représentant une ligne annotée."""
    ID: str
    charge: str
    outil: str
    n_burst: int
    debut_burst: float
    duree_burst: float
    duree_pause: float
    duree_cycle: float
    pct_burst: float
    pct_pause: float
    longueur_burst: int
    burst: str
    startPos	: str
    endPos: str
    docLength: int
    categ: str
    charBurst: str
    ratio: float
    
    erreur: str
    cat_error: str
    token_erronne: str
    lemme: str
    pos_suppose: str
    pos_reel: str
    longueur: int
    contexte: str
    correction: str



@dataclass
class Token:
    """Classe représentant un token du fichier de données."""
    texte: str
    pos_suppose: str
    lemme: str
    erreur: bool
    categ: str
    longueur: int
    contexte: str
    pos_reel: str
    correction: str
    ligne: Ligne

    def get_pos_suppose(self):
        """Retourne la POS (partie du discours) avec TreeTagger."""
        tags = tagger.tag_text(self.texte)
        if tags:
            self.pos_suppose = tags[0].split('\t')[1] if len(tags[0].split('\t')) >= 2 else ''
        return self.pos_suppose

    def get_lemme(self):
        """Retourne le lemme."""
        doc = nlp(self.texte)
        for token in doc:
            self.lemme = token.lemma_
        return self.lemme


@dataclass
class Production:
    """Classe représentant une production à chaque nouveau burst."""
    
    ID: str
    charge: str
    outil: str
    n_burst: int
    debut_burst: float
    duree_burst: float
    duree_pause: float
    duree_cycle: float
    pct_burst: float
    pct_pause: float
    longueur_burst: int
    burst: str
    startPos	: str
    endPos: str
    docLength: int
    categ: str
    charBurst: str
    ratio: float
    
    erreur: str
    cat_error: str
    token_erronne: str
    lemme: str
    pos_suppose: str
    pos_reel: str
    longueur: int
    contexte: str
    correction: str
    
    rt: str
    rt_balise: str
   


@dataclass
class Diff:
    """Classe représentant une différence entre 2 chaînes."""
    start: int
    end: int
    difference: str
    
    
    
    
    
