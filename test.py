

"""import treetaggerwrapper
from dataclasses import dataclass

# Définition de la dataclasse Token
@dataclass
class Token:
    word: str
    pos: str
    lemma: str

# Spécifie le chemin vers les fichiers TreeTagger
TAGGER_PATH = '/home/amandine/Tagger'

# Initialisation de TreeTagger
tagger = treetaggerwrapper.TreeTagger(TAGLANG='fr', TAGDIR=TAGGER_PATH)

text = "Ceci est un exemple de phrase à annoter."

# Annoter le texte avec TreeTagger
tags = tagger.tag_text(text)

# Initialiser une liste pour stocker les instances de Token
token_list = []

# Parcourir les résultats d'annotation
for tag in tags:
    # Les résultats sont sous la forme "<mot>\t<POS>\t<lemme>"
    parts = tag.split('\t')
    if len(parts) == 3:  # S'assurer qu'il y a bien les trois parties attendues
        word, pos, lemma = parts
        # Créer une instance de Token et l'ajouter à la liste
        token = Token(word=word, pos=pos, lemma=lemma)
        token_list.append(token)
    else:
        # En cas de format inattendu, ignorer ou traiter différemment
        print(f"Résultat inattendu : {tag}")

# Afficher la liste de Token créée
for token in token_list:
    print(token)

"""



from dataclasses import dataclass
import treetaggerwrapper

# Spécifier le chemin vers les fichiers TreeTagger
TAGGER_PATH = '/home/amandine/Tagger'

# Initialisation de TreeTagger
tagger = treetaggerwrapper.TreeTagger(TAGLANG='fr', TAGDIR=TAGGER_PATH)

@dataclass
class Token:
    """Classe représentant un token du fichier de données."""
    word: str
    pos: str
    lemme: str

    def get_pos_suppose(self):
        """Retourne la POS (partie du discours) avec TreeTagger."""
        tags = tagger.tag_text(self.word)
        if tags:
            self.pos = tags[0].split('\t')[1] if len(tags[0].split('\t')) >= 2 else ''
        return self.pos

    def get_lemme(self):
        """Retourne le lemme avec TreeTagger."""
        tags = tagger.tag_text(self.word)
        if tags:
            self.lemme = tags[0].split('\t')[2] if len(tags[0].split('\t')) >= 3 else ''
        return self.lemme




# Exemple d'utilisation de la classe Token avec TreeTagger
if __name__ == "__main__":
    # Créer un objet Token
    token = Token(word="celui", pos="", lemme="")

    # Appeler les fonctions pour obtenir la POS et le lemme avec TreeTagger
    token.get_pos_suppose()
    token.get_lemme()

    # Afficher les résultats
    print(f"Mot : {token.word}")
    print(f"POS (partie du discours) : {token.pos}")
    print(f"Lemme : {token.lemme}")

