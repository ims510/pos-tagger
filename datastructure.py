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
    texte_complete: str
    texte_simple: str # texte sans les caracteres de supprime, et qui a les caracteres supprimés
    tokens: List[Token]
    categorie: str
    start_position: int
    end_position: int
    doc_length: int
    id: str

@dataclass
class Erreur:
    """Classe représentant une erreur."""
    mot_errone: str
    ligne: int
    pos_reel:str
    pos_suppose:str


