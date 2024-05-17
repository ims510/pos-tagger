import spacy

# Chargez le modèle SpaCy pour le français
nlp = spacy.load("fr_core_news_sm")

# Phrase d'exemple
sentence = "Le chat gris regarde le ciel."

# Analyse de la phrase avec SpaCy
doc = nlp(sentence)

# Parcourir les tokens de la phrase
for token in doc:
    if token.text == "gris":
        # Afficher le dep_ du token "gris"
        print("Dependance de 'gris' :", token.dep_)

# Afficher la dépendance du mot "gris"
