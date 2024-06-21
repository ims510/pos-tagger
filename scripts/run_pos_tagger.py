"""Ce script permet, étant donné un fichier csv en entrée, de détecter 7 types d'erreurs de frappe et de les annoter en POS."""



from identify_errors_lib import ouverture_csv
from datastructure_lib import Ligne, Token
from typing import List, Dict, Tuple
import csv
from tqdm import tqdm
import os
import sys



def get_persons(liste_lignes: List[Ligne]) -> Dict[str, List[Ligne]]:
    """Retourne une liste de dictionnaires, dont la clé est l'id et la valeur une liste de burts.

    Parameters
    ----------
    liste_lignes : List[Ligne]
        liste des lignes du csv

    Returns
    -------
    Dict
        dictionnaire associant chaque personne (id) à la liste des bursts produits par la personne
    """
    personnes = {}
    for ligne in liste_lignes:
        if ligne.ID not in personnes.keys():
            personnes[ligne.ID] = []
        personnes[ligne.ID].append(ligne)
    return personnes



def get_word(index: int, chaine: str) -> Tuple[str, int, int]:
    """Retrouve un mot en fonction de son indice dans une chaîne.

    Parameters
    ----------
    index : int
        indice du mot (position)
    chaine : str
        chaîne dans laquelle se trouve le mot

    Returns
    -------
    Tuple
        triplet (mot, indice de début du mot, indice de fin du mot)
    """
    word_delimiters = [" ", ".", ",", ":", ";"]
    word_start = index
    word_end = index
    if len(chaine) == 0:
        return "", 0, 0
    while word_start > 0:
        if chaine[word_start-1] in word_delimiters:
            break
        word_start -= 1
    while word_end < len(chaine) - 1:
        if chaine[word_end] in word_delimiters:
            break
        word_end += 1
    return chaine[word_start:word_end], word_start, word_end



def add_burst_to_text(existing_text: str, burst: str, position: int) -> str:
    """Ajoute un burst (incluant les backsapces et deletes) au texte existant à sa position.

    Parameters
    ----------
    existing_text : str
        texte qui existe pour le moment
    burst : str
        texte contenant les erreurs de frappe
    position : int
        position du curseur

    Returns
    -------
    str
        chaîne que l'utilisateur a réellement sous les yeux (en tenant compte de ses modifications)
    """
    cursor = position
    result = existing_text
    for char in burst:
        if char == "⌫":
            if cursor > 0:
                result = result[:cursor-1] + result[cursor:]
                cursor -= 1
        elif char == "⌦":
            if cursor < len(result) - 1:
                result = result[:cursor] + result[cursor+1:]
        elif char == "␣":
            result = result[:cursor] + " " + result[cursor:]
            cursor += 1
        else:
            result = result[:cursor] + char + result[cursor:]
            cursor += 1
    return result



def deletion_within_word(line: Ligne) -> List[Token]:
    """Retourne une liste de tokens dont un ou plusieurs caractères ont été supprimés à l'intérieur du mot.

    Parameters
    ----------
    ligne : Ligne
        une ligne du csv

    Returns
    -------
    List
        liste des tokens avec des suppresssions internes
    """
    list_tokens = []
    line_words = line.charBurst.split("␣")
    for line_word in line_words :
        n = 0
        if "⌫" in line_word[1:-1] and len(line_word) > 1:
            formed_word = ""
            for char in line_word:
                if char == "⌫":
                    formed_word = formed_word[:-1]
                    n += 1
                elif char == "⌦":
                    pass
                else:
                    formed_word += char

            token = Token(
                texte = line_word,
                pos_suppose="",
                lemme="",
                erreur=True,
                categ = "Suppression de caractères à l'intérieur d'un mot",
                longueur = n,
                contexte = formed_word,
                pos_reel="Unknown",
                correction=formed_word,
                ligne=line
            )
            token.pos_suppose = token.get_pos_suppose()
            token.lemme = token.get_lemme()
            list_tokens.append(token)

    return list_tokens



def annotate_errors(list_lines: List[Ligne], personnes: Dict[str, List[Ligne]]) -> List[Token] :
    """Détecte et annote les erreurs de frappe.

    Parameters
    ----------
    list_lines : List
        liste des lignes du csv
    personnes : Dict
        dictionnaire associant à chaque personne les bursts qu'elle a produits

    Returns
    -------
    List
        liste des tokens erronés
    """

    tokens: List[Token] = []

    for list_lines in tqdm(personnes.values(), desc="Identification des erreurs") :
        running_text = list_lines[0].burst
        tokens += deletion_within_word(list_lines[0])

        for i in range(1,len(list_lines)):

            # Fix issue where some start positions are after the end of the text
            if list_lines[i].startPos > list_lines[i-1].docLength:
                list_lines[i].startPos = list_lines[i-1].docLength

            tokens += deletion_within_word(list_lines[i])

            # Add this line to the document text so far
            running_text_after = add_burst_to_text(running_text, list_lines[i].charBurst, list_lines[i].startPos)

            if list_lines[i].startPos != list_lines[i-1].endPos and list_lines[i].startPos != len(running_text):
                correction_position = list_lines[i].startPos
                # if it's one character
                if len(list_lines[i].burst.strip()) == 1:
                    if list_lines[i].burst.isalpha():
                        # if it's just one letter
                        try:
                            word_before, start_of_word, _ = get_word(correction_position, running_text)
                            word_after, _, _ = get_word(start_of_word, running_text_after)
                            token = Token(
                                texte=list_lines[i].burst,
                                pos_suppose="",
                                lemme=" ",
                                erreur=True,

                                categ = "Lettre unique ajoutée",
                                longueur = 1,
                                contexte = word_before,

                                pos_reel="Unknown",
                                correction=word_after,
                                ligne=list_lines[i]
                            )
                            token.pos_suppose = token.get_pos_suppose()
                            token.lemme = token.get_lemme()
                            tokens.append(token)
                        except IndexError:
                            print(list_lines[i].id, len(running_text), list_lines[i-1].docLength, correction_position, list_lines[i].burst)
                    elif list_lines[i].charBurst == "␣":
                        # if it's a space
                        word_before, start_of_word, _ = get_word(correction_position, running_text)
                        word_after, _, _ = get_word(start_of_word, running_text_after)
                        token = Token(
                            texte=list_lines[i].burst,
                            pos_suppose="",
                            lemme=" ",
                            erreur=True,

                            categ = "Espace ajouté",
                            longueur = 1,
                            contexte = word_before,

                            pos_reel="SPACE",
                            correction=word_after,
                            ligne=list_lines[i]
                        )
                        token.pos_suppose = token.get_pos_suppose()
                        token.lemme = token.get_lemme()
                        tokens.append(token)
                else:
                    # if it's multiple characters
                    string_length = len(list_lines[i].charBurst)
                    if list_lines[i].charBurst == "⌫" * string_length:
                        # if it's just backspaces on the entire line
                        word_after, _, _ = get_word(correction_position - string_length, running_text_after)
                        deleted_string = running_text[correction_position - string_length:correction_position]
                        token = Token(
                            texte=list_lines[i].charBurst,
                            pos_suppose="",
                            lemme=" ",
                            erreur=True,

                            categ = "Backspaces supprimant une chaîne",
                            longueur = string_length,
                            contexte = deleted_string,

                            pos_reel="BACKSPACE",
                            correction=word_after,
                            ligne=list_lines[i]
                        )
                        token.pos_suppose = token.get_pos_suppose()
                        token.lemme = token.get_lemme()
                        tokens.append(token)
                    elif list_lines[i].charBurst == "⌦" * string_length:
                        # if it's just delete on the entire line
                        word_after, _, _ = get_word(correction_position, running_text_after)
                        deleted_string = running_text[correction_position : correction_position + string_length]
                        token = Token(
                            texte=list_lines[i].charBurst,
                            pos_suppose="",
                            lemme=" ",
                            erreur=True,

                            categ = "Deletes supprimant une chaîne",
                            longueur = string_length,
                            contexte = deleted_string,

                            pos_reel="DELETE",
                            correction=word_after,
                            ligne=list_lines[i]
                        )
                        token.pos_suppose = token.get_pos_suppose()
                        token.lemme = token.get_lemme()
                        tokens.append(token)
                    elif len(list_lines[i].burst) > 0:
                        # if it's a word
                        begins_with_space = list_lines[i].burst[0] == " "
                        ends_with_space = list_lines[i].burst[-1] == " "
                        inserted_after_space = running_text[correction_position - 1] == " "
                        inserted_before_space = running_text[correction_position] == " "
                        if len(list_lines[i].burst.split()) == 1:
                            # if it's one word, not just multiple letters
                            if (begins_with_space or inserted_after_space) and (ends_with_space or inserted_before_space):
                                previous_word, _, _ = get_word(correction_position - 1, running_text)
                                next_word, _, _ = get_word(correction_position+1, running_text)
                                token = Token(
                                    texte=list_lines[i].burst,
                                    pos_suppose="",
                                    lemme=" ",
                                    erreur=True,

                                    categ = "Mot inséré entre deux mots",
                                    longueur = len(list_lines[i].burst),
                                    contexte = f"{previous_word} ; {next_word}",

                                    pos_reel= "",
                                    correction=f"{previous_word}{list_lines[i].burst}{next_word}",
                                    ligne=list_lines[i]
                                )
                                token.pos_suppose = token.get_pos_suppose()
                                token.pos_reel = token.pos_suppose
                                token.lemme = token.get_lemme()
                                tokens.append(token)
                        else:
                            # if it's multiple words
                            words = list_lines[i].burst.split()
                            previous_word, _, _ = get_word(correction_position - 1, running_text)
                            next_word, _, _ = get_word(correction_position+1, running_text)
                            for word in words:
                                token = Token(
                                    texte=word,
                                    pos_suppose="",
                                    lemme=" ",
                                    erreur=True,

                                    categ = "Partie d'une chaîne insérée entre deux mots",
                                    longueur = len(list_lines[i].burst),
                                    contexte = f"{previous_word} ; {next_word}",

                                    pos_reel= "",
                                    correction=f"{previous_word}{list_lines[i].burst}{next_word}",
                                    ligne=list_lines[i]
                                )
                                token.pos_suppose = token.get_pos_suppose()
                                token.pos_reel = token.pos_suppose
                                token.lemme = token.get_lemme()
                                tokens.append(token)
                            pass


            # Update text for next iteration
            running_text = running_text_after
    return tokens




def save_to_csv(tokens: List[Token], fichier: str) -> None :
    """Sauvegarde la liste de tokens erronés dans un dichier csv

    Parameters
    ----------
    tokens : List
        liste des tokens erronés annotés
    fichier : str
        chemin du fichier csv de sauvegarde

    Returns
    -------
    None
    """

    with open (fichier, "w") as f:
        writer = csv.writer(f)
        writer.writerow(['ID',
                         'Token erroné',
                         'POS réelle',
                         'POS supposée',
                         'Lemme supposé',
                         'Erreur',
                         'Catégorie',
                         'Longueur',
                         'Contexte',
                         'Correction',
                         'charge',
                         'outil',
                         'n_burst',
                         'debut_burst',
                         'duree_burst',
                         'duree_pause',
                         'duree_cycle',
                         'pct_burst',
                         'pct_pause',
                         'longueur_burst',
                         'burst',
                         'startPos',
                         'endPos',
                         'docLength',
                         'categ',
                         'charBurst',
                         'ratio'])

        for token in tqdm(tokens, desc='Ecriture du csv contenant les erreurs'):
            writer.writerow([token.ligne.ID,
                             token.texte,
                             token.pos_reel,
                             token.pos_suppose,
                             token.lemme,
                             token.erreur,
                             token.categ,
                             token.longueur,
                             token.contexte,
                             token.correction,
                             token.ligne.charge,
                             token.ligne.outil,
                             token.ligne.n_burst,
                             token.ligne.debut_burst,
                             token.ligne.duree_burst,
                             token.ligne.duree_pause,
                             token.ligne.duree_cycle,
                             token.ligne.pct_burst,
                             token.ligne.pct_pause,
                             token.ligne.longueur_burst,
                             token.ligne.burst,
                             token.ligne.startPos,
                             token.ligne.endPos,
                             token.ligne.docLength,
                             token.ligne.categ,
                             token.ligne.charBurst,
                             token.ligne.ratio,
                             ])

    print(f"Les données ont bien été sauvegardées dans le fichier {fichier}.")



def main() :

    # Demander à l'utilisateur les fichiers d'entrée et de sortie
    input_file = input('Nom du fichier csv ou tsv contenant les données : ')
    output_file = input("Nom du fichier csv pour sauvegarder l'annotation des erreurs : ")

    # Ouvrir le fichier csv et en extraire les lignes
    liste_lignes = ouverture_csv(input_file)

    # Trouver les bursts produits par chaque participant
    participants = get_persons(liste_lignes)

    # Identification des erreurs et annotation
    erreurs = annotate_errors(liste_lignes, participants)

    # Sauvegarde de l'analyse dans un fichier csv
    save_to_csv(erreurs, output_file)



if __name__ == "__main__":
    main()
