from identify_errors import ouverture_csv
from datastructure import Ligne
from typing import List, Dict, Tuple

liste_lignes = ouverture_csv("/Users/madalina/Documents/M1TAL/Enrichissement de corpus/Docs/csv_planification.csv")

def get_persons(liste_lignes: List[Ligne]) -> Dict[str, List[Ligne]]:
    """Retourne une liste de dictionnaires, dont la clé est l'id et la valeur une liste de burts."""
    personnes = {}
    for ligne in liste_lignes:
        if ligne.id not in personnes.keys():
            personnes[ligne.id] = []
        personnes[ligne.id].append(ligne)
    return personnes

def get_word(index: int, chaine: str) -> Tuple[str, int, int]:
    """Gets a word based on an index into a string."""
    word_delimiters = [" ", ".", ",", ":", ";"]
    word_start = index
    word_end = index
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
        elif char == "␣":
            result = result[:cursor] + " " + result[cursor:]
            cursor += 1
        else: 
            result = result[:cursor] + char + result[cursor:]
            cursor += 1
    return result

personnes = get_persons(liste_lignes)
for list_lines in personnes.values():
# for list_lines in list(personnes.values())[:1]:
    running_text = list_lines[0].texte_simple

    for i in range(1,len(list_lines)):
        # Fix issue where some start positions are after the end of the text
        if list_lines[i].start_position > list_lines[i-1].doc_length:
            list_lines[i].start_position = list_lines[i-1].doc_length

        # Add this line to the document text so far
        running_text_after = add_burst_to_text(running_text, list_lines[i].texte_complete, list_lines[i].start_position)

        if list_lines[i].start_position != list_lines[i-1].end_position:
            correction_position = list_lines[i].start_position
            if len(list_lines[i].texte_simple) == 1 and list_lines[i].texte_simple.isalpha():
                # if it's just one letter
                # print(list_lines[i].id, len(running_text), list_lines[i-1].doc_length, correction_position, list_lines[i].texte_simple)
                try:
                    word_before, start_of_word, _ = get_word(correction_position, running_text)
                    word_after, _, _ = get_word(start_of_word, running_text_after)
                    print(f"{list_lines[i].texte_simple} belongs to {word_before} -> {word_after}")
                except IndexError:
                    print(list_lines[i].id, len(running_text), list_lines[i-1].doc_length, correction_position, list_lines[i].texte_simple)
        # Update text for next iteration
        running_text = running_text_after


