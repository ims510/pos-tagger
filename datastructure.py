from dataclasses import dataclass
from typing import List

@dataclass
class Token:
    """Classe représentant un token du fichier de données."""
    texte: str
    pos: str
    lemme: str
    erreur: str


@dataclass
class Ligne:
    """Classe représentant une ligne du fichier de données."""
    texte: str
    tokens: List[Token]
    categorie: str

@dataclass
class Erreur:
    """Classe représentant une erreur."""
    mot_errone: str
    ligne: int
    pos_reel: str
    pos_suppose: str
 
