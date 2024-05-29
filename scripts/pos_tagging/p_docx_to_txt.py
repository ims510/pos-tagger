import pypandoc
from pathlib import Path
import re

# Parcours arborescence : 
def get_filenames(chemin_dossier: str) -> list[Path]:
    dossier = Path(chemin_dossier)
    return list(dossier.glob('*.docx'))

folder_list = sorted(get_filenames("../data/TextesFinaux_docx/Planification"), key=lambda x: x.name)

liste = []
for file in folder_list:
    output = pypandoc.convert_file(file, 'plain', outputfile=f"{file.name}.txt")
    assert output == "" 
    with open(file, 'r', encoding='UFT-8') as lecture_fichier:

        lecture_fichier.read()
        liste.append(lecture_fichier)


