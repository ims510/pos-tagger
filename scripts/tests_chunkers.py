
# Ce script a pour but de tester et comparer plusieurs chunkers


###############################################################################################################################################


# 1. NLTK

'''print("\n\nNLTK : ")
print("--------------------")'''

'''import nltk
from nltk.tokenize import word_tokenize
from nltk.chunk import RegexpParser

# Définir la phrase d'exemple
phrase = "La maman a un cadeau pour son enfant."

# Tokenisation des mots dans la phrase
tokens = word_tokenize(phrase)

# Étiquetage POS des tokens
tagged_tokens = nltk.pos_tag(tokens)

# Définition des motifs de chunking pour SN, SV et SP
patterns = {
    'SN': 'NP: {<DT>?<JJ>*<NN.*>+}',  # Syntagmes nominaux (ex: La maman, un cadeau, son enfant)
    'SV': 'VP: {<VB.*><NP|PP>*}',      # Syntagmes verbaux (ex: a un cadeau, pour son enfant)
    'SP': 'PP: {<IN><NP>}'             # Syntagmes prépositionnels (ex: pour son enfant)
}

# Initialisation du chunker avec les motifs définis
chunkers = {name: RegexpParser(pattern) for name, pattern in patterns.items()}

# Application du chunker sur les tokens étiquetés pour chaque type de chunk
chunked_results = {name: chunker.parse(tagged_tokens) for name, chunker in chunkers.items()}

# Affichage des chunks résultants
for name, chunks in chunked_results.items():
    print(f"Syntagmes {name} :")
    for chunk in chunks.subtrees():
        if chunk.label() == name:
            print(' '.join([token[0] for token in chunk.leaves()]))
'''

'''import nltk
from nltk import word_tokenize, pos_tag, ne_chunk

# Télécharger le modèle 'maxent_ne_chunker' et le corpus 'punkt'
nltk.download('maxent_ne_chunker')
nltk.download('punkt')

def chunk_text_with_nltk(text):
    # Tokenisation des mots
    words = word_tokenize(text)
    # Part-of-speech tagging
    tagged_words = pos_tag(words)
    # Chunking basé sur des expressions régulières
    chunked_words = ne_chunk(tagged_words)
    return chunked_words

texte = "La médecine alternative pose aussi problème dans le sens où elle ne progresse pas contrairement à la medecine moderne"
resultat_chunking_nltk = chunk_text_with_nltk(texte)
print(resultat_chunking_nltk)'''


###############################################################################################################################################


# 2. Spacy

print("\n\nSpacy : ")
print("--------------------")


from dataclasses import dataclass
from typing import List
import spacy


@dataclass
class Mot: 
    ID: int
    forme: str
    pos: str
    lemme: str
    deprel: str
    gouv: str
    syntagmes: List[str]



# Charger le modèle français de spaCy
nlp = spacy.load('fr_core_news_sm')


def extraire_sn(text):
    """Extrait les syntagmes nominaux du texte donné sous forme de liste."""
    doc = nlp(text)
    sn = [chunk.text for chunk in doc.noun_chunks]
    return sn


def extraire_sv(text):
    """Extrait les syntagmes verbaux du texte donné sous forme de liste."""
    doc = nlp(text)
    sv = []
    for token in doc:
        if token.pos_ == 'VERB':  # Si le token est un verbe
            verb_phrase = [token.text]
            for child in token.children:  # Ajouter les dépendants du verbe
                verb_phrase.append(child.text)
            sv.append(' '.join(verb_phrase))
    return sv


def extraire_sp(text):
    """Extrait les syntagmes prépositionnels du texte donné sous forme de liste."""
    doc = nlp(text)
    sp = []
    for token in doc:
        if token.dep_ == 'case':  # Si le token est une préposition
            governor = token.head  # Récupérer le gouverneur du token prépositionnel
            prep_phrase = f"{token.text} {governor.text}"
            sp.append(prep_phrase)
    return sp


def analyse_dependances(text, liste_sn, liste_sv, liste_sp):
    """Affiche les tokens avec leur relation de dépendance syntaxique et leur gouverneur pour le texte donné."""
    liste_tokens = []
    doc = nlp(text)
    
    # Liste des mots appartenant aux syntagmes nominaux
    mots_in_sn = []
    for sn in liste_sn : 
        mots = sn.split()
        for mot in mots : 
            mots_in_sn.append(mot)
    
    # Liste des mots appartenant aux syntagmes verbaux
    mots_in_sv = []
    for sv in liste_sv : 
        mots = sv.split()
        for mot in mots : 
            mots_in_sv.append(mot)

    # Liste des mots appartenant aux syntagmes prépositionnels
    mots_in_sp = []
    for sp in liste_sp : 
        mots = sp.split()
        for mot in mots : 
            mots_in_sp.append(mot)
    
    
    for index, token in enumerate(doc) :
        
        ID = index + 1   # Pour que le premier mot ait la position 1
        forme = token.text
        pos = token.pos_
        lemme = token.lemma_
        deprel = token.dep_
        gouv = token.head
        
        
        
        # Trouver son syntagme direct (syntagme auquel il appartient)
        synt = []
        if forme in mots_in_sn : 
            synt.append('SN')
        if forme in mots_in_sv : 
            synt.append('SV')
        if forme in mots_in_sp : 
            synt.append('SP')
        
        # Trouver l'éventuel syntagme dans lequel se trouve le syntagme auquel il appartient
        if gouv.text in mots_in_sn : 
            if 'SN' not in synt : 
                synt.append('SN')
        if gouv.text in mots_in_sv : 
            if 'SV' not in synt :
                synt.append('SV')
        if gouv.text in mots_in_sp : 
            if 'SP' not in synt :
                synt.append('SP')
        
        # Pour éviter d'aller trop loin dans l'imbrications des syntagmes, on ne garde que le(s) syntagme(s) auquel appartient le mot directement et éventuellement celui de son gouverneur
        while len(synt) > 2 : 
            del synt[-1]
        
        
        syntagmes = synt
        
        liste_tokens.append(Mot(ID, forme, pos, lemme, deprel, gouv, syntagmes))
        
        
        # Afficher le token, sa relation de dépendance et son gouverneur
        #print(f"Token: {token.text}, Relation de dépendance: {dependency_relation}, Gouverneur: {governor.text}")
        
    return liste_tokens


# Texte d'exemple
texte = "La maman a un cadeau pour son enfant."

# Extraction des syntagmes nominaux sous forme de liste
syntagmes_nominaux = extraire_sn(texte)
print("Syntagmes nominaux :", syntagmes_nominaux)

# Extraction des syntagmes verbaux sous forme de liste
syntagmes_verbaux = extraire_sv(texte)
print("Syntagmes verbaux :", syntagmes_verbaux)

# Extraction des syntagmes prépositionnels sous forme de liste
syntagmes_prepositionnels = extraire_sp(texte)
print("Syntagmes prépositionnels :", syntagmes_prepositionnels)

# Analyse en dépendance
print("\nAnalyse en dépendance :")
tokens = analyse_dependances(texte, syntagmes_nominaux, syntagmes_verbaux, syntagmes_prepositionnels)
print(f"ID\tMot\tPOS\tLemme\tRel\tGouv\tyntagmes")
for token in tokens : 
    print(f"{token.ID}\t{token.forme}\t{token.pos}\t{token.lemme}\t{token.deprel}\t{token.gouv}\t{token.syntagmes}")








# Version qui marche mais qui n'affiche pas les syntagmes auxquels appartient chaque token : 
'''import spacy

# Charger le modèle français de spaCy
nlp = spacy.load('fr_core_news_sm')


def extraire_sn(text):
    """Extrait les syntagmes nominaux du texte donné sous forme de liste."""
    doc = nlp(text)
    sn = [chunk.text for chunk in doc.noun_chunks]
    return sn


def extraire_sv(text):
    """Extrait les syntagmes verbaux du texte donné sous forme de liste."""
    doc = nlp(text)
    sv = []
    for token in doc:
        if token.pos_ == 'VERB':  # Si le token est un verbe
            verb_phrase = [token.text]
            for child in token.children:  # Ajouter les dépendants du verbe
                verb_phrase.append(child.text)
            sv.append(' '.join(verb_phrase))
    return sv


def extraire_sp(text):
    """Extrait les syntagmes prépositionnels du texte donné sous forme de liste."""
    doc = nlp(text)
    sp = []
    for token in doc:
        if token.dep_ == 'case':  # Si le token est une préposition
            governor = token.head  # Récupérer le gouverneur du token prépositionnel
            prep_phrase = f"{token.text} {governor.text}"
            sp.append(prep_phrase)
    return sp


def analyse_dependances(text):
    """Affiche les tokens avec leur relation de dépendance syntaxique et leur gouverneur pour le texte donné."""
    doc = nlp(text)
    for token in doc:
        # Récupérer le token gouverneur et sa relation de dépendance
        governor = token.head
        dependency_relation = token.dep_
        
        # Afficher le token, sa relation de dépendance et son gouverneur
        print(f"Token: {token.text}, Relation de dépendance: {dependency_relation}, Gouverneur: {governor.text}")


# Texte d'exemple
texte = "La maman a un cadeau pour son enfant."

# Extraction des syntagmes nominaux sous forme de liste
syntagmes_nominaux = extraire_sn(texte)
print("Syntagmes nominaux :", syntagmes_nominaux)

# Extraction des syntagmes verbaux sous forme de liste
syntagmes_verbaux = extraire_sv(texte)
print("Syntagmes verbaux :", syntagmes_verbaux)

# Extraction des syntagmes prépositionnels sous forme de liste
syntagmes_prepositionnels = extraire_sp(texte)
print("Syntagmes prépositionnels :", syntagmes_prepositionnels)

# Analyse en dépendance
print("\nAnalyse en dépendance :")
analyse_dependances(texte)'''




# Version avec balises : 
'''import spacy

# Charger le modèle français de spaCy
nlp = spacy.load('fr_core_news_sm')


def extraire_sn(text):
    """Extrait les syntagmes nominaux du texte donné avec balises."""
    doc = nlp(text)
    sn = []
    for chunk in doc.noun_chunks:
        sn.append(f"<sn>{chunk.text}</sn>")
    return ' '.join(sn)


def extraire_sv(text):
    """Extrait les syntagmes verbaux du texte donné avec balises."""
    doc = nlp(text)
    sv = []
    for token in doc:
        if token.pos_ == 'VERB':  # Si le token est un verbe
            verb_phrase = [token.text]
            for child in token.children:  # Ajouter les dépendants du verbe
                verb_phrase.append(child.text)
            sv.append(f"<SV>{' '.join(verb_phrase)}</SV>")
    return ' '.join(sv)


def extraire_sp(text):
    """Extrait les syntagmes prépositionnels du texte donné avec balises."""
    doc = nlp(text)
    sp = []
    for token in doc:
        if token.dep_ == 'case':  # Si le token est une préposition
            governor = token.head  # Récupérer le gouverneur du token prépositionnel
            prep_phrase = f"<SP>{token.text} {governor.text}</SP>"
            sp.append(prep_phrase)
    return ' '.join(sp)


def analyse_dependances(text):
    """Affiche les tokens avec leur relation de dépendance syntaxique et leur gouverneur pour le texte donné."""
    doc = nlp(text)
    for token in doc:
        # Récupérer le token gouverneur et sa relation de dépendance
        governor = token.head
        dependency_relation = token.dep_
        
        # Afficher le token, sa relation de dépendance et son gouverneur
        print(f"Token: {token.text}, Relation de dépendance: {dependency_relation}, Gouverneur: {governor.text}")


# Texte d'exemple
#texte = "La médecine alternative pose aussi problème dans le sens où elle ne progresse pas contrairement à la médecine moderne"
texte = "La maman a un cadeau pour son enfant."

# Extraction des syntagmes nominaux avec balises
syntagmes_nominaux = extraire_sn(texte)
print("Syntagmes nominaux avec balises :", syntagmes_nominaux)

# Extraction des syntagmes verbaux avec balises
syntagmes_verbaux = extraire_sv(texte)
print("Syntagmes verbaux avec balises :", syntagmes_verbaux)

# Extraction des syntagmes prépositionnels avec balises
syntagmes_prepositionnels = extraire_sp(texte)
print("Syntagmes prépositionnels avec balises :", syntagmes_prepositionnels)

# Analyse en dépendance
print("\nAnalyse en dépendance :")
analyse_dependances(texte)'''


###############################################################################################################################################


# 3. SEM








###############################################################################################################################################

# 4. Treetagger



# Correction 1 (pour les problemes 1 et 2)
"""doc = nlp(sentence)
sp = []

for token in doc : 
    prep_phrase = [token.text]
    
    # Si le token est une preposition et qu'il n'a pas de relation 'det' (evite d'extraire les articles partitifs)
    if token.pos_ == 'ADP' and token.dep_ != 'det' :
        
        # Recuperer le gouverneur du token prepositionnel et l'ajouter à l'extraction
        governor = token.head
        prep_phrase.append(governor.text)
        
        # Si le gouverneur est un verbe, on regarde ses dependants
        if governor.pos_ == 'VERB' : 
            
            # S'il possede un dependant qui est son objet alors on ajoute cet objet a l'extraction
            for child in governor.children : 
                if child.dep_ == 'obj' : 
                    prep_phrase.append(child.text)
        
        sp.append(' '.join(prep_phrase))

print(sp)
return sp


# Premiere version
doc = nlp(sentence)
sp = []
for token in doc:
    if token.pos_ == 'ADP' : # Si le token est une pr√©position
        governor = token.head  # R√©cup√©rer le gouverneur du token pr√©positionnel
        prep_phrase = f"{token.text} {governor.text}"
        sp.append(prep_phrase)

print(sp)
return sp"""