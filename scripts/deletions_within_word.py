from identify_errors import ouverture_csv
from datastructure import Ligne, Token
from typing import List, Dict, Tuple


liste_lignes = ouverture_csv("../data/CLEAN_csv_planification.tsv")

def deletion_within_word(liste_lignes: List[Ligne]) -> List[Token]:
    """Returns a list of tokens where characters have been deleted within a word."""
    list_tokens = []
    for line in liste_lignes[0:10]:
        line_words = line.texte_complete.split("␣")
        for line_word in line_words:
            if "⌫" in line_word[1:-1] and len(line_word) > 1:
                formed_word = ""
                for char in line_word:
                    if char == "⌫":
                        formed_word = formed_word[:-1]
                    else:
                        formed_word += char
                token = Token(
                    texte = line_word,
                    pos_suppose="",
                    lemme="",
                    erreur=True,
                    details="Suppression de caractères à l'intérieur d'un mot",
                    pos_reel="Unknown",
                    correction=formed_word,
                    ligne=line
                )
                token.pos_suppose = token.get_pos_suppose()
                token.lemme = token.get_lemme()

                list_tokens.append(token)
    return list_tokens



