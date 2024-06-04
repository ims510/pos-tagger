"""Ce script contient les fonctions qui sont utilisées dans le balisage des données."""



from ch_enrichir_donnees import ouvrir_csv, csv_to_lines, combiner_lignes, enrichir_productions, get_persons, trier_nburst, recuperer_productions
from ch_datastructure import Diff, Production
from typing import Dict, List
import re


def corriger_chaine(chaine: str) -> str :
    """Effectue les suppressions dans une chaîne contenant des backspaces.

    Parameters
    ----------
    chaine : str
        chaîne contenant des backspaces

    Returns
    -------
    str
        chaîne avec les suppressions effectuées
    """
    result = []
    for char in chaine :
        if char == "⌫" :
            if result :
                result.pop()  # Supprime le dernier caractère ajouté
        else :
            result.append(char)  # Ajoute le caractère au résultat
    return ''.join(result)




def corriger_chaine_avec_balises(chaine: str) -> str:
    """Balise les suppressions dans une chaîne corrigée selon les caractères de suppression dans la chaîne originale.

    Parameters
    ----------
    chaine : str
        chaîne originale contenant des backspaces

    Returns
    -------
    str
        chaîne avec des balises autour des caractères supprimés.
    """
    result = []
    suppr_char = []

    i = 0
    while i < len(chaine):
        if chaine[i] == '⌫':
            if result:
                suppr_char.append(result.pop())
        else:
            if suppr_char:
                result.append('<SI>' + ''.join(suppr_char[::-1]) + '</SI>')
                suppr_char = []
            result.append(chaine[i])
        i += 1

    if suppr_char:
        result.append('<SI>' + ''.join(suppr_char[::-1]) + '</SI>')

    return ''.join(result)



def detecter_rb(chaine: str) -> tuple[int, int] :
    """Renvoie le nombre de caractères situés avant le premier caractère de suppression et le nombre de caractères de suppression à la suite

    Parameters
    ----------
    chaine : str
        chaîne contenant des backspaces

    Returns
    -------
    tuple
        tuple dont le premier élément est le nombre de caractères situés avant le premier caractère de suppression et le second le nombre de caractères de suppression à la suite
    """
    avant_suppression = 0
    suppression = 0
    suppression_commence = False
    for char in chaine :
        if char == "⌫" :
            suppression_commence = True
            suppression += 1
        elif not suppression_commence :
            avant_suppression += 1
        else:
            break
    while suppression_commence and avant_suppression + suppression < len(chaine) and chaine[avant_suppression + suppression] == "⌫" :
        suppression += 1
    return avant_suppression, suppression



def difference_between(chaine_1: str, chaine_2: str) -> Diff :
    """Renvoie la différence entre deux chaînes de caractères.

    Parameters
    ----------
    chaine_1 : str
        première chaine à comparer
    chaine_1 : str
        deuxième chaine à comparer

    Returns
    -------
    Diff
        différence détectée entre les deux chaînes avec l'indice de début et de fin
    """

    # Ajout
    if len(chaine_2) > len(chaine_1) :

        # S'il s'agit d'un simple ajout à la suite :
        if chaine_2[0:len(chaine_1)] == chaine_1 :
            diff = Diff(None, None, None)

        # Si la modification apportÃ©e affecte la premiÃ¨re chaÃ®ne :
        else :

            # Trouver l'indice du premier caractÃ¨re diffÃ©rent
            for index, (char1, char2) in enumerate(zip(chaine_1, chaine_2)) :
                if char1 != char2 :
                    start_diff_index = index
                    break

            # Trouver l'indice du dernier caractÃ¨re diffÃ©rent
            for index, (char1, char2) in enumerate(zip(reversed(chaine_1), reversed(chaine_2))) :
                if char1 != char2 :
                    end_diff_index = len(chaine_2)+1 - index
                    break
                else :
                    end_diff_index = len(chaine_2)-1

            # Trouver la chaÃ®ne correspondant Ã  la diffÃ©rence
            diff = Diff(start_diff_index, end_diff_index, chaine_2[start_diff_index:end_diff_index])

        return diff




    # Suppression  --> peut-être à enlever ?
    if len(chaine_2) < len(chaine_1) :

        # Erreur liÃ©e aux donnÃ©es d'origine
        if chaine_2 == '' :
            diff = Diff(None, None, None)

        # S'il n'y a pas d'erreur dans les donnÃ©es d'origine :
        else :
            # Trouver l'indice du premier caractÃ¨re diffÃ©rent
            for index, (char1, char2) in enumerate(zip(chaine_1, chaine_2)) :
                if char1 != char2 :
                    start_diff_index = index
                    break
                else :
                    start_diff_index = len(chaine_2)

            # Trouver l'indice du dernier caractÃ¨re diffÃ©rent
            for index, (char1, char2) in enumerate(zip(reversed(chaine_1), reversed(chaine_2))) :
                if char1 != char2 :
                    end_diff_index = len(chaine_1) - index
                    break
                else :
                    end_diff_index = len(chaine_2)

            diff = Diff(start_diff_index, end_diff_index, chaine_1[start_diff_index:end_diff_index])
        return diff




    # Si les deux chaÃ®nes sont de mÃªme longueur :
    if len(chaine_2) == len(chaine_1) :

        # Trouver l'indice du premier caractÃ¨re diffÃ©rent
        for index, (char1, char2) in enumerate(zip(chaine_1, chaine_2)) :
            if char1 != char2 :
                start_diff_index = index
                break
            else :
                start_diff_index = None

        # Trouver l'indice du dernier caractÃ¨re diffÃ©rent
        for index, (char1, char2) in enumerate(zip(reversed(chaine_1), reversed(chaine_2))) :
            if char1 != char2 :
                end_diff_index = len(chaine_1) - index
                break
            else :
                end_diff_index = None


        # Trouver la chaîne correspondant à la différence
        diff = Diff(start_diff_index, end_diff_index, chaine_1[start_diff_index:end_diff_index])

        return diff



def get_position_char_unique(chaine: str, balise: str) -> str :
    """Renvoie la position de la balise dans le mot dans lequel un caractère a été ajouté.

    Parameters
    ----------
    chaine : str
        chaine contenant le mot auquel on a ajouté une lettre balisée
    balise : str
        type de balise

    Returns
    -------
    str
        position de la modification dans le mot (début, milieu, ou fin)
    """

    # On découpe le texte en mots
    mots = chaine.split()

    # Pour chaque mot :
    for mot in mots :

        # S'il contient la balise recherchée :
        if mot.__contains__(f"<{balise}>") :
            mot_balise = mot

            # On trouve la position du caractère balisé
            position = 1
            for char in mot_balise :
                if char != "<" :
                    position += 1
                else :
                    break

            # On enlève les balises au mot
            mot_balise_sans_balises = mot_balise.replace(f"<{balise}>", "")
            mot_balise_sans_balises = mot_balise_sans_balises.replace(f"</{balise}>", "")

            # On enlève aussi les éventuelles ponctuations
            mot_sans_ponctuations = ''
            for char in mot_balise_sans_balises :
                if char.isalpha() and char != "⌫" :
                    mot_sans_ponctuations += char
                else :
                    break

            # On trouve le nombre de caractères du mot
            nb_char = len(mot_sans_ponctuations)

            # On reconstitue un tuple dont le premier élément est la position du carcatère balisé et le second le nombre de caractères du mot
            #position_lettre = (position, nb_char)

            # Associer au tuple une valeur entre début, milieu, et fin
            if position == 1 :
                position_str = "début"
            if position == nb_char :
                position_str = "fin"
            else :
                position_str = "milieu"


            return position_str


