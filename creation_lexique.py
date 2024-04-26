from pathlib import Path
import spacy
from tqdm import tqdm


nlp = spacy.load("fr_core_news_sm")



def get_filenames(chemin_dossier: str) -> list[Path]:
    dossier = Path(chemin_dossier)
    return list(dossier.glob('*.txt'))


file_liste = get_filenames("TextesFinaux_txt")
#print(file_liste)
def obtenir_lexique(file_liste):
    lexique = []
    for file in tqdm(file_liste, desc="Obtention du lexique") : 
        with open(file, 'r') as lecture_fichier:
            lecture = lecture_fichier.readlines()
            for line in lecture:
                line = line.strip()
                mots = nlp(line)
                for mot in mots:
                    mot = mot.text.lower() #on recupp le text sinon probleme il recupère des attributs mots de spacy 
                    if mot not in lexique : 
                        lexique.append(mot)
                    else : 
                        pass
    return lexique

#obtenir_lexique(file_liste)

# print(lexique) 
