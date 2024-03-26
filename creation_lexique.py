from pathlib import Path
import spacy

nlp = spacy.load("fr_core_sm")



def get_filenames(chemin_dossier: str) -> list[Path]:
    dossier = Path(chemin_dossier)
    return list(dossier.glob('*.txt'))


file_liste = get_filenames("TextesFinaux_txt")
print(file_liste)
lexique = set()
for file in file_liste:
    with open(file, 'r') as lecture_fichier:
        lecture = lecture_fichier.readlines()
        for line in lecture:
            mots = doc.nlp()
            #mots = line.lower().split()
            for mot in mots:
                lexique.add(mot)

print(lexique)





 
