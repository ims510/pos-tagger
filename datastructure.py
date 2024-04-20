from dataclasses import dataclass
from typing import List
import spacy

nlp = spacy.load("fr_core_news_sm")

@dataclass
class Difference:
    """Classe représentant une erreur."""
    mot_errone: str
    ligne: int
    pos_reel:str
    pos_suppose:str
 

# @dataclass
# class Token:
#     """Classe représentant un token du fichier de données."""
#     texte: str
#     pos_auto: str
#     lemme: str
#     erreur: Erreur
#     ligne: Ligne


@dataclass
class Ligne:
    """Classe représentant une ligne du fichier de données."""
    texte_complete: str
    texte_simple: str # texte sans les caracteres de supprime, et qui a les caracteres supprimés
    categorie: str
    start_position: int
    end_position: int
    doc_length: int
    id: str
    n_burst: int

    # def get_tokens(self):
    #     """Retourne les tokens de la ligne."""
    #     doc = nlp(self.texte_simple)
    #     for token in doc:
    #         self.tokens.append(Token(token.text, token.pos_, token.lemma_, False))
    #     return self.tokens


@dataclass
class Token:
    """Classe représentant un token du fichier de données."""
    texte: str
    pos_suppose: str
    lemme: str
    erreur: bool
    details: str
    pos_reel: str
    correction: str
    ligne: Ligne

    def get_pos_suppose(self):
        """Retourne la pos supposée."""
        doc = nlp(self.texte)
        for token in doc:
            self.pos_suppose = token.pos_
        return self.pos_suppose

    def get_lemme(self):
        """Retourne le lemme."""
        doc = nlp(self.texte)
        for token in doc:
            self.lemme = token.lemma_
        return self.lemme
