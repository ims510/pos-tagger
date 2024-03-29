from dataclasses import dataclass
from typing import List

@dataclass
class Token:
    """Classe représentant un token du fichier de données."""
    texte: str
    pos: str
    lemme: str


@dataclass
class Ligne:
    """Classe représentant une ligne du fichier de données."""
    texte: str
    tokens: List[Token]
    categorie: str
    

    