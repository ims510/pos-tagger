#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 10:02:35 2024

@author: amandine
"""

"""Ce script permet de baliser le texte obtenu pour chaque personne avec les types d'erreurs identifiés."""



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



def baliser_erreurs(productions_par_personne: Dict[str, List[Production]]) -> Dict[str, List[Production]] :
    """Balise chaque running text en fonction des erreurs détectées.

    Parameters
    ----------
    productions_par_personne : Dict
        dictionnaire où la clé est la personne et la valeur la liste des Productions produites par cette personne

    Returns
    -------
    Dict
        le même dictionnaire avec chaque running text balisé
    """

    for personne, prod in productions_par_personne.items() :

        # Pour chaque production de chaque personne :
        for i in range(0, len(prod)) :

            if prod[i].charBurst != "Err :501" :

                # Si la production n'a pas d'erreur :    --> à revoir
                if prod[i].cat_error == "0" :

                    # Si son charBurst commence par ⌫ :
                    if prod[i].charBurst.startswith("⌫") :




                        # On corrige le charBurst en effectuant les suppressions indiquées par les backspaces
                        #rt_avec_charburst = prod[i].rt.replace(prod[i].burst, prod[i].charBurst)
                        rt_avec_charburst = prod[i-1].rt + prod[i].charBurst
                        rt_avec_charburst_corrige = corriger_chaine(rt_avec_charburst)

                        # On balise la correction du charBurst
                        #rt_avec_charburst_corrige_balise = corriger_chaine_avec_balises(rt_avec_charburst, rt_avec_charburst_corrige)
                        rt_avec_charburst_corrige_balise = corriger_chaine_avec_balises(rt_avec_charburst)

                        # On remplace les espaces "␣" par des espaces simples
                        rt_avec_charburst_corrige_balise_espaces = rt_avec_charburst_corrige_balise.replace("␣", " ")

                        # On remplace le burst par le charburst corrigé et balisé dans le running text
                        rt_balise = prod[i].rt.replace(prod[i].burst, rt_avec_charburst_corrige_balise_espaces)

                        # On remplace les balises par <RB> pour "Révision de bord"
                        #rt_balise_balises_ouvrantes_correctes = rt_balise.replace("<SI>", "<RB>")
                        #rt_balises_correctes = rt_balise_balises_ouvrantes_correctes.replace("</SI>", "</RB>")

                        prod[i].rt_balise = rt_balise

                        '''if prod[i].ID == "P+S1" :

                            print("@@@@@@@@@@")

                            print(rt_balise)

                            print("@@@@@@@@@@")'''





                        # On compte le nombre de ⌫ à la suite
                        n=0
                        for char in prod[i].charBurst :
                            if char =="⌫" :
                                n+=1
                            else :
                                break

                        # On supprime autant de caractères qu'il y a de backspaces dans le running text de la production précédente
                        couple = (prod[i-1].rt, n)

                        #partie_a_supprimer = prod[i].rt[prod[i].startPos:prod[i].endPos]

                        rt_avec_suppressions = prod[i-1].rt[:-n]
                        #print(rt_avec_suppressions)

                    else :

                        #print(prod[i-1].rt.replace(" ", "␣"))

                        #toto = prod[i-1].rt.replace(" ", "␣") + prod[i].burst.replace(" ", "␣")

                        prod[i].rt_balise = prod[i].rt


                # Si la production a pour erreur "Lettre unique ajoutée" :
                if prod[i].cat_error == "Lettre unique ajoutée" :

                    # S'il s'agit simplement d'un caractère sans suppression :
                    if len(prod[i].charBurst) == 1 :

                        # S'il s'agit d'un espace :
                        if prod[i].charBurst == "␣" :

                            # On balise le burst <EA> pour "Espace ajouté"
                            burst_balise = f"<EA>{prod[i].charBurst}</EA>"

                            # On incrémente le running text balisé avec l'espace ajouté balisé
                            rt_avant_ajout = prod[i].rt[0:prod[i].startPos]
                            lettre_ajoutee_balisee = burst_balise
                            rt_apres_ajout = prod[i].rt[prod[i].startPos+len(prod[i].charBurst)::]
                            rt_balise = rt_avant_ajout + lettre_ajoutee_balisee + rt_apres_ajout

                            # On ajoute les attributs "char", "mots", "operation", et "suppr"
                            char = len(prod[i].charBurst)
                            mots = len(prod[i].burst.strip().split())
                            operation = 'ajout'
                            suppr = 0
                            rt_balise = rt_balise.replace("<EA>", f"<EA char={char} mots={mots} operation='{operation}' suppr={suppr}>")
                            prod[i].rt_balise = rt_balise

                        # S'il s'agit d'une lettre :
                        if prod[i].charBurst.isalpha() :

                            # On balise le burst <LA> pour "Lettre ajoutée"
                            burst_balise = f"<LA>{prod[i].charBurst}</LA>"

                            # On incrémente le running text balisé avec la lettre ajoutée balisée
                            rt_avant_ajout = prod[i].rt[0:prod[i].startPos]
                            lettre_ajoutee_balisee = burst_balise
                            rt_apres_ajout = prod[i].rt[prod[i].startPos+len(prod[i].charBurst)::]
                            rt_balise = rt_avant_ajout + lettre_ajoutee_balisee + rt_apres_ajout

                            # On ajoute les attributs "char", "mots", "operation", "suppr", et "position"
                            char = len(prod[i].burst)
                            mots = len(prod[i].burst.strip().split())
                            operation = 'ajout'
                            suppr = 0
                            position = get_position_char_unique(rt_balise, 'LA')
                            rt_balise = rt_balise.replace("<LA>", f"<LA char={char} mots={mots} operation='{operation}' suppr={suppr} position='{position}'>")
                            prod[i].rt_balise = rt_balise

                    # Si le charburst contient plusieurs caractères :
                    else :

                        # Si le charburst commence par un backspace :
                        if prod[i].charBurst.startswith("⌫") :

                            # On compte le nombre de backspaces qui se suivent
                            n=0
                            for char in prod[i].charBurst :
                                if char == "⌫" :
                                    n+= 1
                                else :
                                    break

                            # S'il y a un seul backspace :
                            if n == 1 :

                                # On balise la lettre ajoutée <LA> pour "Lettre ajoutée"
                                burst_balise = f"<LA>{prod[i].burst}</LA>"

                                # On incrémente le running text balisé avec la lettre remplaçante balisée
                                rt_avant_ajout = prod[i].rt[0:prod[i].startPos-n]
                                lettre_remplacante_balisee = burst_balise
                                rt_apres_ajout = prod[i-1].rt[prod[i].startPos::]
                                rt_balise = rt_avant_ajout + lettre_remplacante_balisee + rt_apres_ajout

                                # On ajoute les attributs "char", "mots", "operation", "suppr", et "position"
                                char = len(prod[i].burst)
                                mots = len(prod[i].burst.strip().split())
                                operation = 'remplacement'
                                suppr = n
                                position = get_position_char_unique(rt_balise, 'LA')
                                rt_balise = rt_balise.replace("<LA>", f"<LA char={char} mots={mots} operation='{operation}' suppr={suppr} position='{position}'>")
                                prod[i].rt_balise = rt_balise

                            # Sinon (s'il y a plusieurs backspaces) :
                            else :

                                # On balise la lettre ajoutée <LA> pour "Lettre ajoutée"
                                burst_balise = f"<LA>{prod[i].burst}</LA>"

                                # On incrémente le running text balisé avec la lettre supprimante balisée
                                rt_avant_ajout = prod[i].rt[0:prod[i].startPos-n]
                                lettre_remplacante_balisee = burst_balise
                                rt_apres_ajout = prod[i-1].rt[prod[i].startPos::]
                                rt_balise = rt_avant_ajout + lettre_remplacante_balisee + rt_apres_ajout

                                # On ajoute les attributs "char", "mots", "operation", "suppr", et "position"
                                char = len(prod[i].burst)
                                mots = len(prod[i].burst.strip().split())
                                operation = 'suppression'
                                suppr = n
                                position = get_position_char_unique(rt_balise, 'LA')
                                rt_balise = rt_balise.replace("<LA>", f"<LA char={char} mots={mots} operation='{operation}' suppr={suppr} position='{position}'>")
                                prod[i].rt_balise = rt_balise


                # Si la production a pour erreur "Mot inséré entre deux mots" :
                if prod[i].cat_error == "Mot inséré entre deux mots" :

                    # On balise le burst <MI> pour "Mot inséré"
                    burst_balise = f"<MI>{prod[i].burst}</MI>"

                    # On incrémente le running text balisé avec le mot inséré balisé
                    rt_avant_insertion = prod[i-1].rt[0:prod[i].startPos]
                    rt_apres_insertion = prod[i-1].rt[prod[i].startPos::]
                    rt_balise = rt_avant_insertion + burst_balise + rt_apres_insertion

                    # On trouve le nombre de caractères supprimés par le mot et on en déduit l'opération
                    nb_suppr = 0
                    for char in prod[i].charBurst :
                        if char == "⌫" :
                            nb_suppr += 1
                        else :
                            break

                    if nb_suppr == 0 :
                        op = 'ajout'
                    elif nb_suppr == len(prod[i].burst) :
                        op = 'remplacement'
                    else :
                        op = 'suppression'

                    # On ajoute les attributs "char", "mots", "operation", et "suppr"
                    char = len(prod[i].burst.strip())
                    mots = len(prod[i].burst.strip().split())
                    operation = op
                    suppr = nb_suppr
                    rt_balise = rt_balise.replace("<MI>", f"<MI char={char} mots={mots} operation='{operation}' suppr={suppr}>")
                    prod[i].rt_balise = rt_balise


                # Si la production a pour erreur "Partie d'une chaîne insérée entre deux mots" :
                if prod[i].cat_error == "Partie d'une chaîne insérée entre deux mots" :

                    # Si le charburst commence par un backspace :
                    if prod[i].charBurst.startswith("⌫") :

                        # On compte le nombre de backspaces qui se suivent
                        n=0
                        for char in prod[i].charBurst :
                            if char == "⌫" :
                                n+= 1
                            else :
                                break

                        # On balise le burst <CI> pour "Chaîne insérée"
                        burst_balise = f"<CI>{prod[i].burst}</CI>"

                        # On incrémente le running text balisé avec la chaîne insérée balisée
                        rt_avant_ajout = prod[i].rt[0:prod[i].startPos-n]
                        lettre_remplacante_balisee = burst_balise
                        rt_apres_ajout = prod[i-1].rt[prod[i].startPos::]
                        rt_balise = rt_avant_ajout + lettre_remplacante_balisee + rt_apres_ajout

                        # On trouve le nombre de caractères supprimés par le mot et on en déduit l'opération
                        nb_suppr = n

                        if nb_suppr == 0 :
                            op = 'ajout'
                        elif nb_suppr == len(prod[i].burst) :
                            op = 'remplacement'
                        else :
                            op = 'suppression'

                        # On ajoute les attributs "char", "mots", "operation", et "suppr"
                        char = len(prod[i].burst.strip())
                        mots = len(prod[i].burst.strip().split())
                        operation = op
                        suppr = nb_suppr
                        rt_balise = rt_balise.replace(f"<CI>{prod[i].burst}</CI>", f"<CI char={char} mots={mots} operation='{op}' suppr={suppr}>{prod[i].burst}</CI>")
                        prod[i].rt_balise = rt_balise

                    # Sinon (si le charburst ne commence pas par un backspace) :
                    else :

                        # On balise le burst <CI> pour "Chaîne insérée"
                        burst_balise = f"<CI>{prod[i].burst}</CI>"

                        # On incrémente le running text balisé avec la chaîne insérée balisée
                        rt_avant_insertion = prod[i-1].rt[0:prod[i].startPos]
                        rt_apres_insertion = prod[i-1].rt[prod[i].startPos::]
                        rt_balise = rt_avant_insertion + burst_balise + rt_apres_insertion

                        # On trouve le nombre de caractères supprimés par le mot et on en déduit l'opération
                        nb_suppr = 0

                        if nb_suppr == 0 :
                            op = 'ajout'
                        elif nb_suppr == len(prod[i].burst) :
                            op = 'remplacement'
                        else :
                            op = 'suppression'

                        # On ajoute les attributs "char", "mots", "operation", et "suppr"
                        char = len(prod[i].burst.strip())
                        mots = len(prod[i].burst.strip().split())
                        operation = op
                        suppr = nb_suppr
                        rt_balise = rt_balise.replace(f"<CI>{prod[i].burst}</CI>", f"<CI char={char} mots={mots} operation='{op}' suppr={suppr}>{prod[i].burst}</CI>")
                        prod[i].rt_balise = rt_balise


                # Si la production a pour erreur "Backspaces supprimant une chaîne" :
                if prod[i].cat_error == "Backspaces supprimant une chaîne" :

                    # On compte le nombre de backspaces
                    n=0
                    for char in prod[i].charBurst :
                        if char == "⌫" :
                            n+= 1

                    # On balise la chaîne supprimée <SB> pour "Suppression par backspaces"
                    chaine_supprimee_balisee = f"<SB>{prod[i].contexte}</SB>"

                    # On incrémente le running text balisé avec la chaîne supprimée balisée
                    rt_avant_suppression = prod[i-1].rt[0:prod[i].startPos-n]
                    rt_apres_suppression = prod[i-1].rt[prod[i].startPos::]
                    rt_balise = rt_avant_suppression + chaine_supprimee_balisee + rt_apres_suppression

                    # On ajoute les attributs "char", "mots", "operation", et "suppr"
                    char = len(prod[i].charBurst)
                    mots = len(prod[i].contexte.strip().split())
                    operation = 'suppression'
                    suppr = n
                    rt_balise = rt_balise.replace("<SB>", f"<SB char={char} mots={mots} operation='{operation}' suppr={suppr}>")
                    prod[i].rt_balise = rt_balise


                # Si la production a pour erreur "Deletes supprimant une chaîne" :
                if prod[i].cat_error == "Deletes supprimant une chaîne" :

                    # On compte le nombre de backspaces
                    n=0
                    for char in prod[i].charBurst :
                        if char == "⌦" :
                            n+= 1

                    # On balise la chaîne supprimée <SD> pour "Suppression par deletes"
                    chaine_supprimee_balisee = f"<SD>{prod[i].contexte}</SD>"

                    # On incrémente le running text balisé avec la chaîne supprimée balisée
                    rt_avant_suppression = prod[i-1].rt[0:prod[i].startPos]
                    rt_apres_suppression = prod[i-1].rt[prod[i].startPos+n::]
                    rt_balise = rt_avant_suppression + chaine_supprimee_balisee + rt_apres_suppression

                    # On ajoute les attributs "char", "mots", "operation", et "suppr"
                    char = len(prod[i].charBurst)
                    mots = len(prod[i].contexte.strip().split())
                    operation = 'suppression'
                    suppr = n
                    rt_balise = rt_balise.replace("<SD>", f"<SD char={char} mots={mots} operation='{operation}' suppr={suppr}>")
                    prod[i].rt_balise = rt_balise

                    # On compte le nombre de backspaces
                    n=0
                    for char in prod[i].charBurst :
                        if char == "⌦" :
                            n+= 1

                    # On balise la chaîne supprimée <SD> pour "Suppression par deletes"
                    chaine_supprimee_balisee = f"<SD>{prod[i].contexte}</SD>"

                    # On incrémente le running text balisé avec la chaîne supprimée balisée
                    rt_avant_suppression = prod[i-1].rt[0:prod[i].startPos]
                    rt_apres_suppression = prod[i-1].rt[prod[i].startPos+n::]
                    rt_balise = rt_avant_suppression + chaine_supprimee_balisee + rt_apres_suppression

                    # On ajoute les attributs "char", "mots", "operation", et "suppr"
                    char = len(prod[i].charBurst)
                    mots = len(prod[i].contexte.strip().split())
                    operation = 'suppression'
                    suppr = n
                    rt_balise = rt_balise.replace("<SD>", f"<SD char={char} mots={mots} operation='{operation}' suppr={suppr}>")
                    prod[i].rt_balise = rt_balise


                # Si la production a pour erreur "Suppression de caractères à l'intérieur d'un mot" :  --> original
                if prod[i].cat_error == "Suppression de caractères à l'intérieur d'un mot original" :

                    # S'il y a une seule suppression interne :
                    if len(prod[i].token_erronne.split('|')) == 1 :

                        # On corrige le charBurst en effectuant les suppressions indiquées par les backspaces
                        charburst = prod[i].charBurst
                        charburst_corrige = corriger_chaine(charburst)

                        # On balise la correction du charBurst
                        charburst_corrige_balise = corriger_chaine_avec_balises(charburst, charburst_corrige)

                        # On remplace les espaces "␣" par des espaces simples
                        charburst_corrige_balise_espaces = charburst_corrige_balise.replace("␣", " ")

                        # On remplace le burst par le charburst corrigé et balisé dans le running text
                        rt_balise = prod[i].rt.replace(prod[i].burst, charburst_corrige_balise_espaces)

                        # On incrémente le running text balisé avec la suppression interne balisée
                        prod[i].rt_balise = rt_balise

                    # S'il y a plusieurs suppressions internes :
                    if len(prod[i].token_erronne.split('|')) > 1 :

                        # On recrée les couples (token_errone, correction)
                        err = prod[i].token_erronne.split('|')
                        corr = prod[i].correction.split('|')
                        couples = list(zip(err, corr))

                        # On initialise le charburst qu'on va baliser
                        charburst_balise = prod[i].charBurst

                        # Pour chaque couple, on balise le charburst balisé
                        for couple in couples :
                            charburst_balise = charburst_balise.replace(couple[0], f"<SI>{couple[1]}</SI>")
                        prod[i].charBurst = charburst_balise.replace("␣", " ")

                        # On intègre les balises au running text balisé
                        burst_sans_balises = prod[i].charBurst.replace("<SI>", "")
                        burst_sans_balises = burst_sans_balises.replace("</SI>", "")
                        #rt_balise = prod[i].rt_balise.replace(burst_sans_balises, prod[i].charBurst)
                        rt_balise = prod[i].rt.replace(prod[i].burst, prod[i].charBurst)

                        # On vérifie si le burst est la dernière partie du running text
                        est_derniere_partie = prod[i].rt.strip().endswith(prod[i].burst.strip())

                        # Si oui :
                        if est_derniere_partie == True :

                            # On effectue les suppressions indiquées par le charburst et on incrémente le running text balisé avec les suppressions internes balisées
                            prod[i].rt_balise = corriger_chaine(rt_balise)

                        # Sinon :
                        else :

                            # On balise toute la chaîne contenant les suppressions internes <CI> pour "Chaîne insérée"
                            rt_balise = rt_balise.replace(prod[i].charBurst, f"<CI>{prod[i].charBurst}</CI>")

                            # On incrémente le running text balisé avec les suppressions internes balisées
                            prod[i].rt_balise = corriger_chaine(rt_balise)


                # Si la production a pour erreur "Suppression de caractères à l'intérieur d'un mot" :  --> révision
                if prod[i].cat_error == "Suppression de caractères à l'intérieur d'un mot" :

                    # On regarde si les suppressions de la production affectent le running text
                    nb_char_avant_suppr, nb_suppr = detecter_rb(prod[i].charBurst)

                    '''# On regarde si la production a bien été ajouté à la suite du running text
                    if prod[i].startPos == prod[i-1].docLength :
                        est_derniere_partie = True
                    else :
                        est_derniere_partie = False'''

                    '''# Si les suppressions n'affectent pas le running text :
                    if nb_char_avant_suppr >= nb_suppr :

                        # On balise le charburst avec les suppressions internes
                        charburst_balise = corriger_chaine_avec_balises(prod[i].charBurst)

                        # On insère le charburst balisé à la position de départ dans le running text
                        rt_avant_revision = prod[i-1].rt[0:prod[i].startPos]
                        rt_apres_revision = prod[i-1].rt[prod[i].startPos::]
                        rt_balise = rt_avant_revision + charburst_balise + rt_apres_revision

                    # Sinon (si les modifications affectent le running text) :
                    else :

                        # On insère le charburst
                        rt_avant_revision = prod[i-1].rt[0:prod[i].startPos]
                        rt_apres_revision = prod[i-1].rt[prod[i].startPos::]
                        rt_balise = rt_avant_revision + prod[i].charBurst + rt_apres_revision
                        rt_balise = corriger_chaine_avec_balises(rt_balise)'''

                    # Si les suppressions n'affectent pas le running text :
                    #if nb_char_avant_suppr >= nb_suppr :

                    '''# On balise le charburst avec les suppressions internes
                    charburst_balise = corriger_chaine_avec_balises(prod[i].charBurst)

                    # On insère le charburst balisé à la position de départ dans le running text
                    rt_avant_revision = prod[i-1].rt[0:prod[i].startPos]
                    rt_apres_revision = prod[i-1].rt[prod[i].startPos::]
                    rt_balise = rt_avant_revision + charburst_balise + rt_apres_revision'''


                    # On insère le charburst à la position de départ du curseur dans le running text
                    rt_avant_revision = prod[i-1].rt[0:prod[i].startPos]
                    rt_apres_revision = prod[i-1].rt[prod[i].startPos::]
                    rt_balise = rt_avant_revision + prod[i].charBurst + rt_apres_revision

                    # On balise les suppressions internes
                    rt_balise = corriger_chaine_avec_balises(rt_balise)

                    # On remplace les espaces "␣" par des espaces simples
                    rt_balise = rt_balise.replace("␣", " ")

                    # On incrémente le running text balisé avec le balisage
                    prod[i].rt_balise = rt_balise


                if prod[i].ID == "P+S1" and prod[i].cat_error == "Suppression de caractères à l'intérieur d'un mot" :
                    print(prod[i].n_burst)
                    print()
                    print(prod[i].charBurst)
                    print()
                    print(prod[i].cat_error)
                    print("***")
                    print(prod[i].rt)
                    print()
                    print(prod[i].burst)
                    print("***")
                    print()
                    print(f"Production : {nb_char_avant_suppr >= nb_suppr}")
                    print(f"Est ajouté à la suite du running text : {prod[i].rt.strip().endswith(prod[i].burst.strip())}")
                    print()
                    print(prod[i].rt_balise)
                    print("-"*120)






def main() :

    # Charger les lignes du csv planification
    liste_lignes = ouvrir_csv('CLEAN_csv_planification.tsv')

    # Charger les lignes erronnées
    lignes_erronnees = csv_to_lines('annotation_erreurs_treetagger.csv')

    # Obtenir une ligne par burst en combinant les erreurs au sein de la même ligne
    lignes_erronnees_combinees = combiner_lignes(lignes_erronnees)

    # Enrichir les lignes du csv planification avec les erreurs détectées
    lignes_enrichies = enrichir_productions(liste_lignes, lignes_erronnees_combinees)

    # Trouver les bursts produits par chaque participant
    participants = get_persons(lignes_enrichies)

    # Trier les productions par n_burst pour chaque personne
    participants_ordre_nburst = trier_nburst(participants)

    # Recuperer la liste des productions enrichies de chaque participant
    prods_par_personne = recuperer_productions(lignes_enrichies, participants_ordre_nburst)

    # Baliser le texte de chaque personne en fonction des types d'erreurs
    annotation_erreurs = baliser_erreurs(prods_par_personne)



if __name__ == "__main__":
    main()
