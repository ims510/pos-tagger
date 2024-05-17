from identify_errors import ouverture_csv
from datastructure import Ligne, Token
from typing import List, Dict, Tuple
import csv
from tqdm import tqdm
import argparse


# Gérer les arguments
parser = argparse.ArgumentParser(description="Identification des erreurs")
parser.add_argument("-i", "--input-file", type=str, default="../data/CLEAN_csv_planification.tsv", help="Chemin du fichier csv d'entrée")
parser.add_argument("-o", "--output-file", type=str, default="../data/annotation_erreurs_treetagger.csv", help="Chemin du fichier csv de sortie")
args = parser.parse_args()


liste_lignes = ouverture_csv(args.input_file)


def get_persons(liste_lignes: List[Ligne]) -> Dict[str, List[Ligne]]:
    """Retourne une liste de dictionnaires, dont la clé est l'id et la valeur une liste de burts."""
    personnes = {}
    for ligne in liste_lignes:
        if ligne.ID not in personnes.keys():
            personnes[ligne.ID] = []
        personnes[ligne.ID].append(ligne)
    return personnes

def get_word(index: int, chaine: str) -> Tuple[str, int, int]:
    """Gets a word based on an index into a string."""
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
    """Adds a burst (including backspaces) to existing text at position"""
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
    """Returns a list of tokens where characters have been deleted within a word."""
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
                
                #details="Suppression de caractères à l'intérieur d'un mot",
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

personnes = get_persons(liste_lignes)
tokens: List[Token] = []

for list_lines in tqdm(personnes.values(), desc="Identification des erreurs") :
# for list_lines in list(personnes.values())[:1]:
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
                    # print(list_lines[i].id, len(running_text), list_lines[i-1].docLength, correction_position, list_lines[i].burst)
                    try:
                        word_before, start_of_word, _ = get_word(correction_position, running_text)
                        word_after, _, _ = get_word(start_of_word, running_text_after)
                        token = Token(
                            texte=list_lines[i].burst,
                            pos_suppose="",
                            lemme=" ",
                            erreur=True,
                            
                            #details=f'Lettre unique appartenant à "{word_before}"',
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
                        
                        #details=f'Epace appartenant à "{word_before}"',
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
                        
                        #details=f"{string_length} backspaces supprimant '{deleted_string}'", #### ASK ABOUT THIS: do we need the pos/lemma of the deleted string?
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
                        
                        #details=f"{string_length} delete (⌦) supprimant '{deleted_string}'", #### ASK ABOUT THIS: do we need the pos/lemma of the deleted string?
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
                                
                                #details=f"Mot inseré entre '{previous_word}' et '{next_word}'",
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
                                
                                #details=f"Partie de la chaine '{list_lines[i].burst}' inserée entre '{previous_word}' et '{next_word}'",
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

with open (args.output_file, "w") as f:
    writer = csv.writer(f)
    #writer.writerow(["Id", "n_burst", "Token_texte", "POS Supposé", "Pos réel", "Lemme", "Erreur", "Catégorie", "Longueur", "Contexte", "Correction"])
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
        #writer.writerow([token.ligne.id, token.ligne.n_burst, token.texte, token.pos_suppose, token.pos_reel, token.lemme, token.erreur, token.categ, token.longueur, token.contexte, token.correction])
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

