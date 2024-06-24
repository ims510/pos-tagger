#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 10:02:35 2024

@author: amandine
"""

"""Ce script permet de baliser le texte obtenu pour chaque personne avec les types d'erreurs identifiés."""



from enrichir_donnees_lib import ouvrir_csv, csv_to_lines, combiner_lignes, enrichir_productions, get_persons, trier_nburst, recuperer_productions
from typing import Dict, List
from datastructure_lib import Production, Annotation
from outils_balisage_lib import corriger_chaine_avec_balises, detecter_rb, get_position_char_unique, remplacer_balise_si, get_nb_char, process_deletions, extraire_sequence, nettoyer_texte
from tqdm import tqdm
import re
import os
import sys



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
    resultat = {}

    for personne, prod in tqdm(productions_par_personne.items(), desc="Balisage des erreurs") :

        annotations = []

        # Pour chaque production de chaque personne :
        for i in range(0, len(prod)) :

            if prod[i].charBurst != "Err :501" :

                # Si la production n'a pas d'erreur :
                if prod[i].cat_error == "0" :

                    # On regarde si les suppressions de la production affectent le running text
                    nb_char_avant_suppr, nb_suppr = detecter_rb(prod[i].charBurst)

                    # Si son charBurst commence par ⌫ :
                    if prod[i].charBurst.startswith("⌫") :

                        # On va la traiter comme une erreur de suppression interne

                        # On regarde si les suppressions de la production affectent le running text
                        nb_char_avant_suppr, nb_suppr = detecter_rb(prod[i].charBurst)

                        # On identifie la partie du running text située avant et après la modification
                        rt_avant_revision = prod[i-1].rt[0:prod[i].startPos]
                        rt_apres_revision = prod[i-1].rt[prod[i].startPos::]

                        # On insère le charburst de la production entre les parties du running text avant et après la modification
                        rt_normal = rt_avant_revision + prod[i].charBurst + rt_apres_revision

                        # On effectue le balisage des suppressions internes
                        rt_balise_normal = corriger_chaine_avec_balises(rt_normal)

                        # On remplace les espaces "␣" par des espaces simples
                        rt_balise_normal_espaces = rt_balise_normal.replace("␣", " ")

                        # On récupère toutes les balises avec leur contenu
                        pattern = re.compile(r'(<ID>)(.*?)(</ID>)')

                        # On ajoute les attributs "prod" et "char" aux balises <ID>
                        pattern = re.compile(r'(<ID>)(.*?)(</ID>)')  # Récupération de toutes les balises avec leur contenu
                        compteur = [0]  # Utilisation d'une liste pour permettre la mise à jour dans lambda
                        rt_balise_normal_espaces_attributs = re.sub(
                            pattern,
                            lambda match: remplacer_balise_si(match, compteur),
                            rt_balise_normal_espaces
                        )

                        # On incrémente le running text balisé
                        prod[i].rt_balise = rt_balise_normal_espaces_attributs

                        # On compte le nombre de suppressions successives
                        char = get_nb_char(prod[i].charBurst)

                        an = Annotation(ID = prod[i].ID, charge = prod[i].charge, outil = prod[i].outil, n_burst = prod[i].n_burst, debut_burst = prod[i].debut_burst, duree_burst = prod[i].duree_burst, duree_pause = prod[i].duree_pause, duree_cycle = prod[i].duree_cycle, pct_burst = prod[i].pct_burst, pct_pause = prod[i].pct_pause, longueur_burst = prod[i].longueur_burst, burst = prod[i].burst, startPos = prod[i].startPos, endPos = prod[i].endPos, docLength = prod[i].docLength, categ = prod[i].categ, charBurst = prod[i].charBurst, ratio = prod[i].ratio,
                        erreur = "True", cat_error = "ID", token_erronne = prod[i].token_erronne, lemme = prod[i].lemme, pos_suppose = prod[i].pos_suppose, pos_reel = prod[i].pos_reel, longueur = prod[i].longueur, contexte = prod[i].contexte, correction = prod[i].correction,
                        nb_char = char, nb_words = None, type_operation = None, nb_deletion = None, abs_position = None, rel_position = None, scope = "preceding",
                        rt = prod[i].rt, rt_balise = prod[i].rt_balise)

                        annotations.append(an)

                    # Sinon (si son charBurst ne commence par ⌫) :
                    else :

                        # Le running text balisé est égal au running text
                        prod[i].rt_balise = prod[i].rt

                        an = Annotation(ID = prod[i].ID, charge = prod[i].charge, outil = prod[i].outil, n_burst = prod[i].n_burst, debut_burst = prod[i].debut_burst, duree_burst = prod[i].duree_burst, duree_pause = prod[i].duree_pause, duree_cycle = prod[i].duree_cycle, pct_burst = prod[i].pct_burst, pct_pause = prod[i].pct_pause, longueur_burst = prod[i].longueur_burst, burst = prod[i].burst, startPos = prod[i].startPos, endPos = prod[i].endPos, docLength = prod[i].docLength, categ = prod[i].categ, charBurst = prod[i].charBurst, ratio = prod[i].ratio,
                        erreur = prod[i].erreur, cat_error = "0", token_erronne = prod[i].token_erronne, lemme = prod[i].lemme, pos_suppose = prod[i].pos_suppose, pos_reel = prod[i].pos_reel, longueur = prod[i].longueur, contexte = prod[i].contexte, correction = prod[i].correction,
                        nb_char = None, nb_words = None, type_operation = None, nb_deletion = None, abs_position = None, rel_position = None, scope = None,
                        rt = prod[i].rt, rt_balise = prod[i].rt_balise)

                        annotations.append(an)


                # Si la production a pour erreur "Lettre unique ajoutée" :
                elif prod[i].cat_error == "Lettre unique ajoutée" or prod[i].cat_error == "Espace unique ajouté" :

                    # S'il s'agit simplement d'un caractère sans suppression :
                    if len(prod[i].charBurst) == 1 :

                        # S'il s'agit d'un espace :
                        if prod[i].charBurst == "␣" :

                            # On balise le burst <AS> pour "Espace ajouté"
                            burst_balise = f"<AS>{prod[i].charBurst}</AS>"

                            # On incrémente le running text balisé avec l'espace ajouté balisé
                            rt_avant_ajout = prod[i].rt[0:prod[i].startPos]
                            lettre_ajoutee_balisee = burst_balise
                            rt_apres_ajout = prod[i].rt[prod[i].startPos+len(prod[i].charBurst)::]
                            rt_balise = rt_avant_ajout + lettre_ajoutee_balisee + rt_apres_ajout

                            # On ajoute les attributs "char", "mots", "operation", et "suppr"
                            char = len(prod[i].charBurst)
                            mots = len(prod[i].burst.strip().split())
                            operation = 'addition'
                            suppr = 0
                            rt_balise = rt_balise.replace("<AS>", f"<AS char={char} words={mots} operation='{operation}' deletion={suppr}>")
                            prod[i].rt_balise = rt_balise

                            an = Annotation(ID = prod[i].ID, charge = prod[i].charge, outil = prod[i].outil, n_burst = prod[i].n_burst, debut_burst = prod[i].debut_burst, duree_burst = prod[i].duree_burst, duree_pause = prod[i].duree_pause, duree_cycle = prod[i].duree_cycle, pct_burst = prod[i].pct_burst, pct_pause = prod[i].pct_pause, longueur_burst = prod[i].longueur_burst, burst = prod[i].burst, startPos = prod[i].startPos, endPos = prod[i].endPos, docLength = prod[i].docLength, categ = prod[i].categ, charBurst = prod[i].charBurst, ratio = prod[i].ratio,
                            erreur = prod[i].erreur, cat_error = "AS", token_erronne = prod[i].token_erronne, lemme = prod[i].lemme, pos_suppose = prod[i].pos_suppose, pos_reel = prod[i].pos_reel, longueur = prod[i].longueur, contexte = prod[i].contexte, correction = prod[i].correction,
                            nb_char = char, nb_words = mots, type_operation = operation, nb_deletion = suppr, abs_position = None, rel_position = None, scope = None,
                            rt = prod[i].rt, rt_balise = prod[i].rt_balise)

                            annotations.append(an)


                        # S'il s'agit d'une lettre :
                        elif prod[i].burst.isalpha() :

                            # On balise le burst <AL> pour "Lettre ajoutée"
                            burst_balise = f"<AL>{prod[i].charBurst}</AL>"

                            # On incrémente le running text balisé avec la lettre ajoutée balisée
                            rt_avant_ajout = prod[i].rt[0:prod[i].startPos]
                            lettre_ajoutee_balisee = burst_balise
                            rt_apres_ajout = prod[i].rt[prod[i].startPos+len(prod[i].charBurst)::]
                            rt_balise = rt_avant_ajout + lettre_ajoutee_balisee + rt_apres_ajout

                            # On ajoute les attributs "char", "mots", "operation", "suppr", et "position"
                            char = len(prod[i].burst)
                            mots = len(prod[i].burst.strip().split())
                            operation = 'addition'
                            suppr = 0
                            absolute_position = get_position_char_unique(rt_balise, 'AL')[0]
                            relative_position = get_position_char_unique(rt_balise, 'AL')[1]
                            rt_balise = rt_balise.replace("<AL>", f"<AL char={char} words={mots} operation='{operation}' deletion={suppr} abs_position='{absolute_position}' rel_position='{relative_position}'>")
                            prod[i].rt_balise = rt_balise

                            an = Annotation(ID = prod[i].ID, charge = prod[i].charge, outil = prod[i].outil, n_burst = prod[i].n_burst, debut_burst = prod[i].debut_burst, duree_burst = prod[i].duree_burst, duree_pause = prod[i].duree_pause, duree_cycle = prod[i].duree_cycle, pct_burst = prod[i].pct_burst, pct_pause = prod[i].pct_pause, longueur_burst = prod[i].longueur_burst, burst = prod[i].burst, startPos = prod[i].startPos, endPos = prod[i].endPos, docLength = prod[i].docLength, categ = prod[i].categ, charBurst = prod[i].charBurst, ratio = prod[i].ratio,
                            erreur = prod[i].erreur, cat_error = "AL", token_erronne = prod[i].token_erronne, lemme = prod[i].lemme, pos_suppose = prod[i].pos_suppose, pos_reel = prod[i].pos_reel, longueur = prod[i].longueur, contexte = prod[i].contexte, correction = prod[i].correction,
                            nb_char = char, nb_words = mots, type_operation = operation, nb_deletion = suppr, abs_position = absolute_position, rel_position = relative_position, scope = None,
                            rt = prod[i].rt, rt_balise = prod[i].rt_balise)

                            annotations.append(an)



                        # Sinon (s'il s'agit d'une ponctuation) :
                        else :

                            # On balise le burst <AP> pour "Ponctuation ajoutée"
                            burst_balise = f"<AP>{prod[i].charBurst}</AP>"

                            # On incrémente le running text balisé avec la ponctuation ajoutée balisée
                            rt_avant_ajout = prod[i].rt[0:prod[i].startPos]
                            lettre_ajoutee_balisee = burst_balise
                            rt_apres_ajout = prod[i].rt[prod[i].startPos+len(prod[i].charBurst)::]
                            rt_balise = rt_avant_ajout + lettre_ajoutee_balisee + rt_apres_ajout

                            # On ajoute les attributs "char", "mots", "operation", "suppr", et "position"
                            char = len(prod[i].burst)
                            mots = len(prod[i].burst.strip().split())
                            operation = 'addition'
                            suppr = 0
                            rt_balise = rt_balise.replace("<AP>", f"<AP char={char} words={mots} operation='{operation}' deletion={suppr}>")
                            prod[i].rt_balise = rt_balise

                            an = Annotation(ID = prod[i].ID, charge = prod[i].charge, outil = prod[i].outil, n_burst = prod[i].n_burst, debut_burst = prod[i].debut_burst, duree_burst = prod[i].duree_burst, duree_pause = prod[i].duree_pause, duree_cycle = prod[i].duree_cycle, pct_burst = prod[i].pct_burst, pct_pause = prod[i].pct_pause, longueur_burst = prod[i].longueur_burst, burst = prod[i].burst, startPos = prod[i].startPos, endPos = prod[i].endPos, docLength = prod[i].docLength, categ = prod[i].categ, charBurst = prod[i].charBurst, ratio = prod[i].ratio,
                            erreur = prod[i].erreur, cat_error = "AP", token_erronne = prod[i].token_erronne, lemme = prod[i].lemme, pos_suppose = prod[i].pos_suppose, pos_reel = prod[i].pos_reel, longueur = prod[i].longueur, contexte = prod[i].contexte, correction = prod[i].correction,
                            nb_char = char, nb_words = mots, type_operation = operation, nb_deletion = suppr, abs_position = None, rel_position = None, scope = None,
                            rt = prod[i].rt, rt_balise = prod[i].rt_balise)

                            annotations.append(an)


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


                            # Si le caractère ajouté est un espace :
                            if prod[i].burst == " " :

                                # S'il y a un seul backspace :
                                if n == 1 :

                                    # On balise l'espace ajouté <AS> pour "Espace ajouté"
                                    burst_balise = f"<AS>{prod[i].burst}</AS>"

                                    # On incrémente le running text balisé avec l'espace remplaçant balisé
                                    rt_avant_ajout = prod[i].rt[0:prod[i].startPos-n]
                                    lettre_remplacante_balisee = burst_balise
                                    rt_apres_ajout = prod[i-1].rt[prod[i].startPos::]
                                    rt_balise = rt_avant_ajout + lettre_remplacante_balisee + rt_apres_ajout

                                    # On ajoute les attributs "char", "mots", "operation", "suppr", et "position"
                                    char = len(prod[i].burst)
                                    mots = len(prod[i].burst.strip().split())
                                    operation = 'substitution'
                                    suppr = n
                                    rt_balise = rt_balise.replace("<AS>", f"<AS char={char} words={mots} operation='{operation}' deletion={suppr}>")
                                    prod[i].rt_balise = rt_balise

                                    an = Annotation(ID = prod[i].ID, charge = prod[i].charge, outil = prod[i].outil, n_burst = prod[i].n_burst, debut_burst = prod[i].debut_burst, duree_burst = prod[i].duree_burst, duree_pause = prod[i].duree_pause, duree_cycle = prod[i].duree_cycle, pct_burst = prod[i].pct_burst, pct_pause = prod[i].pct_pause, longueur_burst = prod[i].longueur_burst, burst = prod[i].burst, startPos = prod[i].startPos, endPos = prod[i].endPos, docLength = prod[i].docLength, categ = prod[i].categ, charBurst = prod[i].charBurst, ratio = prod[i].ratio,
                                    erreur = prod[i].erreur, cat_error = "AS", token_erronne = prod[i].token_erronne, lemme = prod[i].lemme, pos_suppose = prod[i].pos_suppose, pos_reel = prod[i].pos_reel, longueur = prod[i].longueur, contexte = prod[i].contexte, correction = prod[i].correction,
                                    nb_char = char, nb_words = mots, type_operation = operation, nb_deletion = suppr, abs_position = None, rel_position = None, scope = None,
                                    rt = prod[i].rt, rt_balise = prod[i].rt_balise)

                                    annotations.append(an)


                                # Sinon (s'il y a plusieurs backspaces) :
                                else :

                                    # On balise l'espace ajouté <AS> pour "Espace ajouté"
                                    burst_balise = f"<AS>{prod[i].burst}</AS>"

                                    # On incrémente le running text balisé avec l'espace supprimant balisé
                                    rt_avant_ajout = prod[i].rt[0:prod[i].startPos-n]
                                    lettre_remplacante_balisee = burst_balise
                                    rt_apres_ajout = prod[i-1].rt[prod[i].startPos::]
                                    rt_balise = rt_avant_ajout + lettre_remplacante_balisee + rt_apres_ajout

                                    # On ajoute les attributs "char", "mots", "operation", "suppr", et "position"
                                    char = len(prod[i].burst)
                                    mots = len(prod[i].burst.strip().split())
                                    operation = 'deletion'
                                    suppr = n
                                    rt_balise = rt_balise.replace("<AS>", f"<AS char={char} words={mots} operation='{operation}' deletion={suppr}>")
                                    prod[i].rt_balise = rt_balise

                                    an = Annotation(ID = prod[i].ID, charge = prod[i].charge, outil = prod[i].outil, n_burst = prod[i].n_burst, debut_burst = prod[i].debut_burst, duree_burst = prod[i].duree_burst, duree_pause = prod[i].duree_pause, duree_cycle = prod[i].duree_cycle, pct_burst = prod[i].pct_burst, pct_pause = prod[i].pct_pause, longueur_burst = prod[i].longueur_burst, burst = prod[i].burst, startPos = prod[i].startPos, endPos = prod[i].endPos, docLength = prod[i].docLength, categ = prod[i].categ, charBurst = prod[i].charBurst, ratio = prod[i].ratio,
                                    erreur = prod[i].erreur, cat_error = "AS", token_erronne = prod[i].token_erronne, lemme = prod[i].lemme, pos_suppose = prod[i].pos_suppose, pos_reel = prod[i].pos_reel, longueur = prod[i].longueur, contexte = prod[i].contexte, correction = prod[i].correction,
                                    nb_char = char, nb_words = mots, type_operation = operation, nb_deletion = suppr, abs_position = None, rel_position = None, scope = None,
                                    rt = prod[i].rt, rt_balise = prod[i].rt_balise)

                                    annotations.append(an)


                            # S'il s'agit d'une lettre :
                            elif prod[i].burst.isalpha() :

                                # S'il y a un seul backspace :
                                if n == 1 :

                                    # On balise la lettre ajoutée <AL> pour "Lettre ajoutée"
                                    burst_balise = f"<AL>{prod[i].burst}</AL>"

                                    # On incrémente le running text balisé avec la lettre remplaçante balisée
                                    rt_avant_ajout = prod[i].rt[0:prod[i].startPos-n]
                                    lettre_remplacante_balisee = burst_balise
                                    rt_apres_ajout = prod[i-1].rt[prod[i].startPos::]
                                    rt_balise = rt_avant_ajout + lettre_remplacante_balisee + rt_apres_ajout

                                    # On ajoute les attributs "char", "mots", "operation", "suppr", et "position"
                                    char = len(prod[i].burst)
                                    mots = len(prod[i].burst.strip().split())
                                    operation = 'substitution'
                                    suppr = n
                                    absolute_position = get_position_char_unique(rt_balise, 'AL')[0]
                                    relative_position = get_position_char_unique(rt_balise, 'AL')[1]
                                    rt_balise = rt_balise.replace("<AL>", f"<AL char={char} words={mots} operation='{operation}' deletion={suppr} abs_position='{absolute_position}' rel_position='{relative_position}'>")
                                    prod[i].rt_balise = rt_balise

                                    an = Annotation(ID = prod[i].ID, charge = prod[i].charge, outil = prod[i].outil, n_burst = prod[i].n_burst, debut_burst = prod[i].debut_burst, duree_burst = prod[i].duree_burst, duree_pause = prod[i].duree_pause, duree_cycle = prod[i].duree_cycle, pct_burst = prod[i].pct_burst, pct_pause = prod[i].pct_pause, longueur_burst = prod[i].longueur_burst, burst = prod[i].burst, startPos = prod[i].startPos, endPos = prod[i].endPos, docLength = prod[i].docLength, categ = prod[i].categ, charBurst = prod[i].charBurst, ratio = prod[i].ratio,
                                    erreur = prod[i].erreur, cat_error = "AL", token_erronne = prod[i].token_erronne, lemme = prod[i].lemme, pos_suppose = prod[i].pos_suppose, pos_reel = prod[i].pos_reel, longueur = prod[i].longueur, contexte = prod[i].contexte, correction = prod[i].correction,
                                    nb_char = char, nb_words = mots, type_operation = operation, nb_deletion = suppr, abs_position = absolute_position, rel_position = relative_position, scope = None,
                                    rt = prod[i].rt, rt_balise = prod[i].rt_balise)

                                    annotations.append(an)


                                # Sinon (s'il y a plusieurs backspaces) :
                                else :

                                    # On balise la lettre ajoutée <AL> pour "Lettre ajoutée"
                                    burst_balise = f"<AL>{prod[i].burst}</AL>"

                                    # On incrémente le running text balisé avec la lettre supprimante balisée
                                    rt_avant_ajout = prod[i].rt[0:prod[i].startPos-n]
                                    lettre_remplacante_balisee = burst_balise
                                    rt_apres_ajout = prod[i-1].rt[prod[i].startPos::]
                                    rt_balise = rt_avant_ajout + lettre_remplacante_balisee + rt_apres_ajout

                                    # On ajoute les attributs "char", "mots", "operation", "suppr", et "position"
                                    char = len(prod[i].burst)
                                    mots = len(prod[i].burst.strip().split())
                                    operation = 'deletion'
                                    suppr = n
                                    absolute_position = get_position_char_unique(rt_balise, 'AL')[0]
                                    relative_position = get_position_char_unique(rt_balise, 'AL')[1]
                                    rt_balise = rt_balise.replace("<AL>", f"<AL char={char} words={mots} operation='{operation}' deletion={suppr} abs_position='{absolute_position}' rel_position='{relative_position}'>")
                                    prod[i].rt_balise = rt_balise

                                    an = Annotation(ID = prod[i].ID, charge = prod[i].charge, outil = prod[i].outil, n_burst = prod[i].n_burst, debut_burst = prod[i].debut_burst, duree_burst = prod[i].duree_burst, duree_pause = prod[i].duree_pause, duree_cycle = prod[i].duree_cycle, pct_burst = prod[i].pct_burst, pct_pause = prod[i].pct_pause, longueur_burst = prod[i].longueur_burst, burst = prod[i].burst, startPos = prod[i].startPos, endPos = prod[i].endPos, docLength = prod[i].docLength, categ = prod[i].categ, charBurst = prod[i].charBurst, ratio = prod[i].ratio,
                                    erreur = prod[i].erreur, cat_error = "AL", token_erronne = prod[i].token_erronne, lemme = prod[i].lemme, pos_suppose = prod[i].pos_suppose, pos_reel = prod[i].pos_reel, longueur = prod[i].longueur, contexte = prod[i].contexte, correction = prod[i].correction,
                                    nb_char = char, nb_words = mots, type_operation = operation, nb_deletion = suppr, abs_position = absolute_position, rel_position = relative_position, scope = None,
                                    rt = prod[i].rt, rt_balise = prod[i].rt_balise)

                                    annotations.append(an)



                            # Sinon (si le caractère ajouté est une ponctuation) :
                            else :

                                # S'il y a un seul backspace :
                                if n == 1 :

                                    # On balise la ponctuation ajoutée <AP> pour "Ponctuation ajoutée"
                                    burst_balise = f"<AP>{prod[i].burst}</AP>"

                                    # On incrémente le running text balisé avec la ponctuation remplaçante balisée
                                    rt_avant_ajout = prod[i].rt[0:prod[i].startPos-n]
                                    lettre_remplacante_balisee = burst_balise
                                    rt_apres_ajout = prod[i-1].rt[prod[i].startPos::]
                                    rt_balise = rt_avant_ajout + lettre_remplacante_balisee + rt_apres_ajout

                                    # On ajoute les attributs "char", "mots", "operation", "suppr", et "position"
                                    char = len(prod[i].burst)
                                    mots = len(prod[i].burst.strip().split())
                                    operation = 'substitution'
                                    suppr = n
                                    rt_balise = rt_balise.replace("<AP>", f"<AP char={char} words={mots} operation='{operation}' deletion={suppr}>")
                                    prod[i].rt_balise = rt_balise

                                    an = Annotation(ID = prod[i].ID, charge = prod[i].charge, outil = prod[i].outil, n_burst = prod[i].n_burst, debut_burst = prod[i].debut_burst, duree_burst = prod[i].duree_burst, duree_pause = prod[i].duree_pause, duree_cycle = prod[i].duree_cycle, pct_burst = prod[i].pct_burst, pct_pause = prod[i].pct_pause, longueur_burst = prod[i].longueur_burst, burst = prod[i].burst, startPos = prod[i].startPos, endPos = prod[i].endPos, docLength = prod[i].docLength, categ = prod[i].categ, charBurst = prod[i].charBurst, ratio = prod[i].ratio,
                                    erreur = prod[i].erreur, cat_error = "AP", token_erronne = prod[i].token_erronne, lemme = prod[i].lemme, pos_suppose = prod[i].pos_suppose, pos_reel = prod[i].pos_reel, longueur = prod[i].longueur, contexte = prod[i].contexte, correction = prod[i].correction,
                                    nb_char = char, nb_words = mots, type_operation = operation, nb_deletion = suppr, abs_position = None, rel_position = None, scope = None,
                                    rt = prod[i].rt, rt_balise = prod[i].rt_balise)

                                    annotations.append(an)


                                # Sinon (s'il y a plusieurs backspaces) :
                                else :

                                    # On balise la ponctuation ajoutée <AP> pour "Ponctuation ajoutée"
                                    burst_balise = f"<AP>{prod[i].burst}</AP>"

                                    # On incrémente le running text balisé avec la ponctuation supprimante balisée
                                    rt_avant_ajout = prod[i].rt[0:prod[i].startPos-n]
                                    lettre_remplacante_balisee = burst_balise
                                    rt_apres_ajout = prod[i-1].rt[prod[i].startPos::]
                                    rt_balise = rt_avant_ajout + lettre_remplacante_balisee + rt_apres_ajout

                                    # On ajoute les attributs "char", "mots", "operation", "suppr", et "position"
                                    char = len(prod[i].burst)
                                    mots = len(prod[i].burst.strip().split())
                                    operation = 'deletion'
                                    suppr = n
                                    rt_balise = rt_balise.replace("<AP>", f"<AP char={char} words={mots} operation='{operation}' deletion={suppr}>")
                                    prod[i].rt_balise = rt_balise

                                    an = Annotation(ID = prod[i].ID, charge = prod[i].charge, outil = prod[i].outil, n_burst = prod[i].n_burst, debut_burst = prod[i].debut_burst, duree_burst = prod[i].duree_burst, duree_pause = prod[i].duree_pause, duree_cycle = prod[i].duree_cycle, pct_burst = prod[i].pct_burst, pct_pause = prod[i].pct_pause, longueur_burst = prod[i].longueur_burst, burst = prod[i].burst, startPos = prod[i].startPos, endPos = prod[i].endPos, docLength = prod[i].docLength, categ = prod[i].categ, charBurst = prod[i].charBurst, ratio = prod[i].ratio,
                                    erreur = prod[i].erreur, cat_error = "AP", token_erronne = prod[i].token_erronne, lemme = prod[i].lemme, pos_suppose = prod[i].pos_suppose, pos_reel = prod[i].pos_reel, longueur = prod[i].longueur, contexte = prod[i].contexte, correction = prod[i].correction,
                                    nb_char = char, nb_words = mots, type_operation = operation, nb_deletion = suppr, abs_position = None, rel_position = None, scope = None,
                                    rt = prod[i].rt, rt_balise = prod[i].rt_balise)

                                    annotations.append(an)



                # Si la production a pour erreur "Mot inséré entre deux mots" :
                elif prod[i].cat_error == "Mot inséré entre deux mots" :

                    # On balise le burst <IW> pour "Mot inséré"
                    burst_balise = f"<IW>{prod[i].burst}</IW>"

                    # On trouve le nombre de caractères supprimés par le mot et on en déduit l'opération
                    nb_suppr = 0
                    for char in prod[i].charBurst :
                        if char == "⌫" :
                            nb_suppr += 1
                        else :
                            break

                    if nb_suppr == 0 :
                        op = 'addition'
                    elif nb_suppr == len(prod[i].burst) :
                        op = 'substitution'
                    else :
                        op = 'deletion'

                    # On incrémente le running text balisé avec le mot inséré balisé
                    rt_avant_insertion = prod[i-1].rt[0:prod[i].startPos-nb_suppr]
                    rt_apres_insertion = prod[i-1].rt[prod[i].startPos::]
                    rt_balise = rt_avant_insertion + burst_balise + rt_apres_insertion

                    # On ajoute les attributs "char", "mots", "operation", et "suppr"
                    char = len(prod[i].burst.strip())
                    mots = len(prod[i].burst.strip().split())
                    operation = op
                    suppr = nb_suppr
                    rt_balise = rt_balise.replace("<IW>", f"<IW char={char} words={mots} operation='{operation}' deletion={suppr}>")
                    prod[i].rt_balise = rt_balise

                    an = Annotation(ID = prod[i].ID, charge = prod[i].charge, outil = prod[i].outil, n_burst = prod[i].n_burst, debut_burst = prod[i].debut_burst, duree_burst = prod[i].duree_burst, duree_pause = prod[i].duree_pause, duree_cycle = prod[i].duree_cycle, pct_burst = prod[i].pct_burst, pct_pause = prod[i].pct_pause, longueur_burst = prod[i].longueur_burst, burst = prod[i].burst, startPos = prod[i].startPos, endPos = prod[i].endPos, docLength = prod[i].docLength, categ = prod[i].categ, charBurst = prod[i].charBurst, ratio = prod[i].ratio,
                    erreur = prod[i].erreur, cat_error = "IW", token_erronne = prod[i].token_erronne, lemme = prod[i].lemme, pos_suppose = prod[i].pos_suppose, pos_reel = prod[i].pos_reel, longueur = prod[i].longueur, contexte = prod[i].contexte, correction = prod[i].correction,
                    nb_char = char, nb_words = mots, type_operation = operation, nb_deletion = suppr, abs_position = None, rel_position = None, scope = None,
                    rt = prod[i].rt, rt_balise = prod[i].rt_balise)

                    annotations.append(an)



                # Si la production a pour erreur "Partie d'une chaîne insérée entre deux mots" :
                elif prod[i].cat_error == "Partie d'une chaîne insérée entre deux mots" :

                    # Si le charburst commence par un backspace :
                    if prod[i].charBurst.startswith("⌫") :

                        # On compte le nombre de backspaces qui se suivent
                        n=0
                        for char in prod[i].charBurst :
                            if char == "⌫" :
                                n+= 1
                            else :
                                break

                        # On balise le burst <IS> pour "Chaîne insérée"
                        burst_balise = f"<IS>{prod[i].burst}</IS>"

                        # On incrémente le running text balisé avec la chaîne insérée balisée
                        rt_avant_ajout = prod[i].rt[0:prod[i].startPos-n]
                        lettre_remplacante_balisee = burst_balise
                        rt_apres_ajout = prod[i-1].rt[prod[i].startPos::]
                        rt_balise = rt_avant_ajout + lettre_remplacante_balisee + rt_apres_ajout

                        # On trouve le nombre de caractères supprimés par le mot et on en déduit l'opération
                        nb_suppr = n

                        if nb_suppr == 0 :
                            op = 'addition'
                        elif nb_suppr == len(prod[i].burst) :
                            op = 'substitution'
                        else :
                            op = 'deletion'

                        # On ajoute les attributs "char", "mots", "operation", et "suppr"
                        char = len(prod[i].burst.strip())
                        mots = len(prod[i].burst.strip().split())
                        operation = op
                        suppr = nb_suppr
                        rt_balise = rt_balise.replace(f"<IS>{prod[i].burst}</IS>", f"<IS char={char} words={mots} operation='{op}' deletion={suppr}>{prod[i].burst}</IS>")

                        if rt_balise.strip().endswith("</IS>") :
                            prod[i].rt_balise = prod[i].rt
                            an = Annotation(ID = prod[i].ID, charge = prod[i].charge, outil = prod[i].outil, n_burst = prod[i].n_burst, debut_burst = prod[i].debut_burst, duree_burst = prod[i].duree_burst, duree_pause = prod[i].duree_pause, duree_cycle = prod[i].duree_cycle, pct_burst = prod[i].pct_burst, pct_pause = prod[i].pct_pause, longueur_burst = prod[i].longueur_burst, burst = prod[i].burst, startPos = prod[i].startPos, endPos = prod[i].endPos, docLength = prod[i].docLength, categ = prod[i].categ, charBurst = prod[i].charBurst, ratio = prod[i].ratio,
                            erreur = "False", cat_error = "0", token_erronne = prod[i].token_erronne, lemme = prod[i].lemme, pos_suppose = prod[i].pos_suppose, pos_reel = prod[i].pos_reel, longueur = prod[i].longueur, contexte = prod[i].contexte, correction = prod[i].correction,
                            nb_char = None, nb_words = None, type_operation = None, nb_deletion = None, abs_position = None, rel_position = None, scope = None,
                            rt = prod[i].rt, rt_balise = prod[i].rt_balise)

                        else :
                            prod[i].rt_balise = rt_balise
                            an = Annotation(ID = prod[i].ID, charge = prod[i].charge, outil = prod[i].outil, n_burst = prod[i].n_burst, debut_burst = prod[i].debut_burst, duree_burst = prod[i].duree_burst, duree_pause = prod[i].duree_pause, duree_cycle = prod[i].duree_cycle, pct_burst = prod[i].pct_burst, pct_pause = prod[i].pct_pause, longueur_burst = prod[i].longueur_burst, burst = prod[i].burst, startPos = prod[i].startPos, endPos = prod[i].endPos, docLength = prod[i].docLength, categ = prod[i].categ, charBurst = prod[i].charBurst, ratio = prod[i].ratio,
                            erreur = prod[i].erreur, cat_error = "IS", token_erronne = prod[i].token_erronne, lemme = prod[i].lemme, pos_suppose = prod[i].pos_suppose, pos_reel = prod[i].pos_reel, longueur = prod[i].longueur, contexte = prod[i].contexte, correction = prod[i].correction,
                            nb_char = char, nb_words = mots, type_operation = operation, nb_deletion = suppr, abs_position = None, rel_position = None, scope = None,
                            rt = prod[i].rt, rt_balise = prod[i].rt_balise)

                        annotations.append(an)


                    # Sinon (si le charburst ne commence pas par un backspace) :
                    else :

                        # On balise le burst <IS> pour "Chaîne insérée"
                        burst_balise = f"<IS>{prod[i].burst}</IS>"

                        # On incrémente le running text balisé avec la chaîne insérée balisée
                        rt_avant_insertion = prod[i-1].rt[0:prod[i].startPos]
                        rt_apres_insertion = prod[i-1].rt[prod[i].startPos::]
                        rt_balise = rt_avant_insertion + burst_balise + rt_apres_insertion

                        # On trouve le nombre de caractères supprimés par le mot et on en déduit l'opération
                        nb_suppr = 0

                        if nb_suppr == 0 :
                            op = 'addition'
                        elif nb_suppr == len(prod[i].burst) :
                            op = 'substitution'
                        else :
                            op = 'deletion'

                        # On ajoute les attributs "char", "mots", "operation", et "suppr"
                        char = len(prod[i].burst.strip())
                        mots = len(prod[i].burst.strip().split())
                        operation = op
                        suppr = nb_suppr
                        rt_balise = rt_balise.replace(f"<IS>{prod[i].burst}</IS>", f"<IS char={char} words={mots} operation='{op}' deletion={suppr}>{prod[i].burst}</IS>")
                        prod[i].rt_balise = rt_balise

                        an = Annotation(ID = prod[i].ID, charge = prod[i].charge, outil = prod[i].outil, n_burst = prod[i].n_burst, debut_burst = prod[i].debut_burst, duree_burst = prod[i].duree_burst, duree_pause = prod[i].duree_pause, duree_cycle = prod[i].duree_cycle, pct_burst = prod[i].pct_burst, pct_pause = prod[i].pct_pause, longueur_burst = prod[i].longueur_burst, burst = prod[i].burst, startPos = prod[i].startPos, endPos = prod[i].endPos, docLength = prod[i].docLength, categ = prod[i].categ, charBurst = prod[i].charBurst, ratio = prod[i].ratio,
                        erreur = prod[i].erreur, cat_error = "IS", token_erronne = prod[i].token_erronne, lemme = prod[i].lemme, pos_suppose = prod[i].pos_suppose, pos_reel = prod[i].pos_reel, longueur = prod[i].longueur, contexte = prod[i].contexte, correction = prod[i].correction,
                        nb_char = char, nb_words = mots, type_operation = operation, nb_deletion = suppr, abs_position = None, rel_position = None, scope = None,
                        rt = prod[i].rt, rt_balise = prod[i].rt_balise)

                        annotations.append(an)



                # Si la production a pour erreur "Backspaces supprimant une chaîne" :
                elif prod[i].cat_error == "Backspaces supprimant une chaîne" :

                    # On compte le nombre de backspaces
                    n=0
                    for char in prod[i].charBurst :
                        if char == "⌫" :
                            n+= 1

                    # On balise la chaîne supprimée <BD> pour "Suppression par backspaces"
                    chaine_supprimee_balisee = f"<BD>{prod[i].contexte}</BD>"

                    # On incrémente le running text balisé avec la chaîne supprimée balisée
                    rt_avant_suppression = prod[i-1].rt[0:prod[i].startPos-n]
                    rt_apres_suppression = prod[i-1].rt[prod[i].startPos::]
                    rt_balise = rt_avant_suppression + chaine_supprimee_balisee + rt_apres_suppression

                    # On ajoute les attributs "char", "mots", "operation", et "suppr"
                    char = len(prod[i].charBurst)
                    mots = len(prod[i].contexte.strip().split())
                    operation = 'deletion'
                    suppr = n
                    rt_balise = rt_balise.replace("<BD>", f"<BD char={char} words={mots} operation='{operation}' deletion={suppr}>")
                    prod[i].rt_balise = rt_balise

                    an = Annotation(ID = prod[i].ID, charge = prod[i].charge, outil = prod[i].outil, n_burst = prod[i].n_burst, debut_burst = prod[i].debut_burst, duree_burst = prod[i].duree_burst, duree_pause = prod[i].duree_pause, duree_cycle = prod[i].duree_cycle, pct_burst = prod[i].pct_burst, pct_pause = prod[i].pct_pause, longueur_burst = prod[i].longueur_burst, burst = prod[i].burst, startPos = prod[i].startPos, endPos = prod[i].endPos, docLength = prod[i].docLength, categ = prod[i].categ, charBurst = prod[i].charBurst, ratio = prod[i].ratio,
                    erreur = prod[i].erreur, cat_error = "BD", token_erronne = prod[i].token_erronne, lemme = prod[i].lemme, pos_suppose = prod[i].pos_suppose, pos_reel = prod[i].pos_reel, longueur = prod[i].longueur, contexte = prod[i].contexte, correction = prod[i].correction,
                    nb_char = char, nb_words = mots, type_operation = operation, nb_deletion = suppr, abs_position = None, rel_position = None, scope = None,
                    rt = prod[i].rt, rt_balise = prod[i].rt_balise)

                    annotations.append(an)



                # Si la production a pour erreur "Deletes supprimant une chaîne" :
                elif prod[i].cat_error == "Deletes supprimant une chaîne" :

                    # On compte le nombre de backspaces
                    n=0
                    for char in prod[i].charBurst :
                        if char == "⌦" :
                            n+= 1

                    # On balise la chaîne supprimée <DD> pour "Suppression par deletes"
                    chaine_supprimee_balisee = f"<DD>{prod[i].contexte}</DD>"

                    # On incrémente le running text balisé avec la chaîne supprimée balisée
                    rt_avant_suppression = prod[i-1].rt[0:prod[i].startPos]
                    rt_apres_suppression = prod[i-1].rt[prod[i].startPos+n::]
                    rt_balise = rt_avant_suppression + chaine_supprimee_balisee + rt_apres_suppression

                    # On ajoute les attributs "char", "mots", "operation", et "suppr"
                    char = len(prod[i].charBurst)
                    mots = len(prod[i].contexte.strip().split())
                    operation = 'deletion'
                    suppr = n
                    rt_balise = rt_balise.replace("<DD>", f"<DD char={char} words={mots} operation='{operation}' deletion={suppr}>")
                    prod[i].rt_balise = rt_balise

                    an = Annotation(ID = prod[i].ID, charge = prod[i].charge, outil = prod[i].outil, n_burst = prod[i].n_burst, debut_burst = prod[i].debut_burst, duree_burst = prod[i].duree_burst, duree_pause = prod[i].duree_pause, duree_cycle = prod[i].duree_cycle, pct_burst = prod[i].pct_burst, pct_pause = prod[i].pct_pause, longueur_burst = prod[i].longueur_burst, burst = prod[i].burst, startPos = prod[i].startPos, endPos = prod[i].endPos, docLength = prod[i].docLength, categ = prod[i].categ, charBurst = prod[i].charBurst, ratio = prod[i].ratio,
                    erreur = prod[i].erreur, cat_error = "DD", token_erronne = prod[i].token_erronne, lemme = prod[i].lemme, pos_suppose = prod[i].pos_suppose, pos_reel = prod[i].pos_reel, longueur = prod[i].longueur, contexte = prod[i].contexte, correction = prod[i].correction,
                    nb_char = char, nb_words = mots, type_operation = operation, nb_deletion = suppr, abs_position = None, rel_position = None, scope = None,
                    rt = prod[i].rt, rt_balise = prod[i].rt_balise)

                    annotations.append(an)


                # Si la production a pour erreur "Suppression de caractères à l'intérieur d'un mot" :
                elif prod[i].cat_error == "Suppression de caractères à l'intérieur d'un mot" :

                    # On regarde si les suppressions de la production affectent le running text
                    nb_char_avant_suppr, nb_suppr = detecter_rb(prod[i].charBurst)

                    # On identifie la partie du running text située avant et après la modification
                    rt_avant_revision = prod[i-1].rt[0:prod[i].startPos]
                    rt_apres_revision = prod[i-1].rt[prod[i].startPos::]

                    # Si la production est bien ajoutée à la suite du running text :
                    if prod[i].rt.strip().endswith(prod[i].burst.strip()) == True :

                        # Si les suppressions de la production n'affectent pas le running text :
                        if nb_char_avant_suppr >= nb_suppr :

                            # On insère le charburst de la production entre les parties du running text avant et après la modification
                            rt_normal = rt_avant_revision + prod[i].charBurst + rt_apres_revision

                            # On effectue le balisage des suppressions internes
                            rt_balise_normal = corriger_chaine_avec_balises(rt_normal)

                            # On remplace les espaces "␣" par des espaces simples
                            rt_balise_normal_espaces = rt_balise_normal.replace("␣", " ")

                            # On récupère toutes les balises avec leur contenu
                            pattern = re.compile(r'(<ID>)(.*?)(</ID>)')

                            # On ajoute les attributs "prod" et "char" aux balises <ID>
                            rt_balise_normal_espaces_attributs = re.sub(pattern, lambda match: f"<ID scope='local' char={len(match.group(2))}>{match.group(2)}</ID>", rt_balise_normal_espaces)

                            # On incrémente le running text balisé
                            prod[i].rt_balise = rt_balise_normal_espaces_attributs

                            # On compte le nombre de suppressions successives
                            char = get_nb_char(prod[i].charBurst)

                            an = Annotation(ID = prod[i].ID, charge = prod[i].charge, outil = prod[i].outil, n_burst = prod[i].n_burst, debut_burst = prod[i].debut_burst, duree_burst = prod[i].duree_burst, duree_pause = prod[i].duree_pause, duree_cycle = prod[i].duree_cycle, pct_burst = prod[i].pct_burst, pct_pause = prod[i].pct_pause, longueur_burst = prod[i].longueur_burst, burst = prod[i].burst, startPos = prod[i].startPos, endPos = prod[i].endPos, docLength = prod[i].docLength, categ = prod[i].categ, charBurst = prod[i].charBurst, ratio = prod[i].ratio,
                            erreur = prod[i].erreur, cat_error = "ID", token_erronne = prod[i].token_erronne, lemme = prod[i].lemme, pos_suppose = prod[i].pos_suppose, pos_reel = prod[i].pos_reel, longueur = prod[i].longueur, contexte = prod[i].contexte, correction = prod[i].correction,
                            nb_char = char, nb_words = None, type_operation = None, nb_deletion = None, abs_position = None, rel_position = None, scope = 'local',
                            rt = prod[i].rt, rt_balise = prod[i].rt_balise)

                            annotations.append(an)

                        # Sinon (si les suppressions de la production affectent le running text) :
                        else :

                            # On insère le charburst de la production entre les parties du running text avant et après la modification
                            rt_normal = rt_avant_revision + prod[i].charBurst + rt_apres_revision

                            # On effectue le balisage des suppressions internes
                            rt_balise_normal = corriger_chaine_avec_balises(rt_normal)

                            # On remplace les espaces "␣" par des espaces simples
                            rt_balise_normal_espaces = rt_balise_normal.replace("␣", " ")

                            # On récupère toutes les balises avec leur contenu
                            pattern = re.compile(r'(<ID>)(.*?)(</ID>)')

                            # On ajoute les attributs "prod" et "char" aux balises <ID>
                            pattern = re.compile(r'(<ID>)(.*?)(</ID>)')  # Récupération de toutes les balises avec leur contenu
                            compteur = [0]  # Utilisation d'une liste pour permettre la mise à jour dans lambda
                            rt_balise_normal_espaces_attributs = re.sub(
                                pattern,
                                lambda match: remplacer_balise_si(match, compteur),
                                rt_balise_normal_espaces
                            )

                            # On incrémente le running text balisé
                            prod[i].rt_balise = rt_balise_normal_espaces_attributs

                            # On compte le nombre de suppressions successives
                            char = get_nb_char(prod[i].charBurst)

                            an = Annotation(ID = prod[i].ID, charge = prod[i].charge, outil = prod[i].outil, n_burst = prod[i].n_burst, debut_burst = prod[i].debut_burst, duree_burst = prod[i].duree_burst, duree_pause = prod[i].duree_pause, duree_cycle = prod[i].duree_cycle, pct_burst = prod[i].pct_burst, pct_pause = prod[i].pct_pause, longueur_burst = prod[i].longueur_burst, burst = prod[i].burst, startPos = prod[i].startPos, endPos = prod[i].endPos, docLength = prod[i].docLength, categ = prod[i].categ, charBurst = prod[i].charBurst, ratio = prod[i].ratio,
                            erreur = prod[i].erreur, cat_error = "ID", token_erronne = prod[i].token_erronne, lemme = prod[i].lemme, pos_suppose = prod[i].pos_suppose, pos_reel = prod[i].pos_reel, longueur = prod[i].longueur, contexte = prod[i].contexte, correction = prod[i].correction,
                            nb_char = char, nb_words = None, type_operation = None, nb_deletion = None, abs_position = None, rel_position = None, scope = 'preceding',
                            rt = prod[i].rt, rt_balise = prod[i].rt_balise)

                            annotations.append(an)


                    # Sinon (si la production n'est pas ajoutée à la suite du running text) :
                    else :

                        # Si les suppressions de la production n'affectent pas le running text :
                        if nb_char_avant_suppr >= nb_suppr :

                            # On insère le charburst de la production entre les parties du running text avant et après la modification entre balises <IS> pour "Chaîne insérée"
                            rt_ci_suite = rt_avant_revision + "<IS>" + prod[i].charBurst + "</IS>" + rt_apres_revision

                            # On effectue le balisage des suppressions internes
                            rt_balise_ci_suite = corriger_chaine_avec_balises(rt_ci_suite)

                            # On remplace les espaces "␣" par des espaces simples
                            rt_balise_ci_espaces_suite = rt_balise_ci_suite.replace("␣", " ")

                            # On récupère toutes les balises avec leur contenu
                            pattern = re.compile(r'(<ID>)(.*?)(</ID>)')

                            # On ajoute les attributs "prod" et "char" aux balises <ID>
                            rt_balise_ci_espaces_suite_attributs = re.sub(pattern, lambda match: f"<ID scope='local' char={len(match.group(2))}>{match.group(2)}</ID>", rt_balise_ci_espaces_suite)

                            # On ajoute les attributs "char", "mots", "operation", et "suppr" à la balise <IS>
                            char = len(prod[i].burst)
                            mots = len(prod[i].burst.strip().split())
                            operation = 'addition'
                            suppr = 0
                            rt_balise_ci_espaces_suite_attributs_ci = rt_balise_ci_espaces_suite_attributs.replace("<IS>", f"<IS char={char} words={mots} operation='{op}' deletion={suppr}>")
                            prod[i].rt_balise = rt_balise_ci_espaces_suite_attributs_ci

                            an = Annotation(ID = prod[i].ID, charge = prod[i].charge, outil = prod[i].outil, n_burst = prod[i].n_burst, debut_burst = prod[i].debut_burst, duree_burst = prod[i].duree_burst, duree_pause = prod[i].duree_pause, duree_cycle = prod[i].duree_cycle, pct_burst = prod[i].pct_burst, pct_pause = prod[i].pct_pause, longueur_burst = prod[i].longueur_burst, burst = prod[i].burst, startPos = prod[i].startPos, endPos = prod[i].endPos, docLength = prod[i].docLength, categ = prod[i].categ, charBurst = prod[i].charBurst, ratio = prod[i].ratio,
                            erreur = prod[i].erreur, cat_error = "ID", token_erronne = prod[i].token_erronne, lemme = prod[i].lemme, pos_suppose = prod[i].pos_suppose, pos_reel = prod[i].pos_reel, longueur = prod[i].longueur, contexte = prod[i].contexte, correction = prod[i].correction,
                            nb_char = char, nb_words = mots, type_operation = operation, nb_deletion = suppr, abs_position = None, rel_position = None, scope = 'local',
                            rt = prod[i].rt, rt_balise = prod[i].rt_balise)

                            annotations.append(an)

                        # Sinon (si les suppressions de la production affectent le running text) :
                        else :

                            # On insère le charburst de la production entre les parties du running text avant et après la modification
                            rt_ci_milieu = rt_avant_revision + prod[i].charBurst + rt_apres_revision

                            # On effectue le balisage des suppressions internes
                            rt_balise_ci_milieu = corriger_chaine_avec_balises(rt_ci_milieu)

                            # On remplace les espaces "␣" par des espaces simples
                            rt_balise_ci_espaces_milieu = rt_balise_ci_milieu.replace("␣", " ")

                            # On identifie la partie du running text avant la modification QUI N'A PAS ETE AFFECTEE PAR LES SUPPRESSIONS !
                            rt_avant = rt_avant_revision[0:len(rt_avant_revision)+(nb_char_avant_suppr-nb_suppr)]

                            # On trouve l'indice de début de la partie du running text qui suit la modification
                            index = rt_balise_ci_espaces_milieu[len(rt_avant_revision)+(nb_char_avant_suppr-nb_suppr)::].find(rt_apres_revision)

                            # On s'en sert pour reconstituer la modification balisée
                            rt_pendant = rt_balise_ci_espaces_milieu[len(rt_avant_revision)+(nb_char_avant_suppr-nb_suppr)::][:index] + rt_balise_ci_espaces_milieu[len(rt_avant_revision)+(nb_char_avant_suppr-nb_suppr)::][index + len(rt_apres_revision):]

                            # On identifie la partie du running text après la modification
                            rt_apres = rt_apres_revision

                            # On insère la modification balisée entre balises <IS> pour "Chaîne insérée" entre les parties du running text avant et après la modification
                            rt_balise_ci_espaces_milieu_final = rt_avant + "<IS>" + rt_pendant + "</IS>" + rt_apres

                            # On récupère toutes les balises avec leur contenu
                            pattern = re.compile(r'(<ID>)(.*?)(</ID>)')

                            # On ajoute les attributs "prod" et "char" aux balises <ID>
                            pattern = re.compile(r'(<ID>)(.*?)(</ID>)')  # Récupération de toutes les balises avec leur contenu
                            compteur = [0]  # Utilisation d'une liste pour permettre la mise à jour dans lambda
                            rt_balise_ci_espaces_milieu_final_attributs = re.sub(
                                pattern,
                                lambda match: remplacer_balise_si(match, compteur),
                                rt_balise_ci_espaces_milieu_final
                            )

                            # On trouve le nombre de caractères supprimés dans le running text par la production et on en déduit l'opération
                            if nb_suppr-nb_char_avant_suppr == len(prod[i].burst) :
                                op = 'substitution'
                            else :
                                op = 'deletion'

                            # On ajoute les attributs "char", "mots", "operation", et "suppr" à la balise <IS>
                            char = len(prod[i].burst)
                            mots = len(prod[i].burst.strip().split())
                            operation = op
                            suppr = nb_suppr-nb_char_avant_suppr
                            rt_balise_ci_espaces_milieu_final_attributs_ci = rt_balise_ci_espaces_milieu_final_attributs.replace("<IS>", f"<IS char={char} words={mots} operation='{op}' deletion={suppr}>")
                            prod[i].rt_balise = rt_balise_ci_espaces_milieu_final_attributs_ci

                            an = Annotation(ID = prod[i].ID, charge = prod[i].charge, outil = prod[i].outil, n_burst = prod[i].n_burst, debut_burst = prod[i].debut_burst, duree_burst = prod[i].duree_burst, duree_pause = prod[i].duree_pause, duree_cycle = prod[i].duree_cycle, pct_burst = prod[i].pct_burst, pct_pause = prod[i].pct_pause, longueur_burst = prod[i].longueur_burst, burst = prod[i].burst, startPos = prod[i].startPos, endPos = prod[i].endPos, docLength = prod[i].docLength, categ = prod[i].categ, charBurst = prod[i].charBurst, ratio = prod[i].ratio,
                            erreur = prod[i].erreur, cat_error = "ID", token_erronne = prod[i].token_erronne, lemme = prod[i].lemme, pos_suppose = prod[i].pos_suppose, pos_reel = prod[i].pos_reel, longueur = prod[i].longueur, contexte = prod[i].contexte, correction = prod[i].correction,
                            nb_char = char, nb_words = mots, type_operation = operation, nb_deletion = suppr, abs_position = None, rel_position = None, scope = 'preceding',
                            rt = prod[i].rt, rt_balise = prod[i].rt_balise)

                            annotations.append(an)

                # Sinon, on affiche un message d'erreur avec le numéro de burst de la production
                else :
                    print(f"Non-traité : {prod[i].n_burst}")

        # Supprimer les doublons éventuels
        annotations_sans_doublons = []
        for annotation in annotations :
            if annotation not in annotations_sans_doublons :
                annotations_sans_doublons.append(annotation)

        resultat[personne] = annotations_sans_doublons

    return resultat



def reconstruire_textes(dico: Dict) -> Dict :
    """Reconstruit les textes de chaque personne avec les erreurs annotées

    Parameters
    ----------
    dico : Dict
        dictionnaire où la clé est la personne et la valeur la liste des Productions produites par cette personne

    Returns
    -------
    Dict
        dictionnaire où la clé est la personne et la valeur le texte reconstruit avec les erreurs annotées
    """

    # Initialiser un dictionnaire pour stocker les textes reconstruits
    textes_reconstruits = {}
    
    data = ouvrir_csv("CLEAN_csv_planification.tsv")

    # Pour chaque personne :
    for personne, prod in tqdm(dico.items(), desc="Reconstruction des textes annotés") :
        
        # Extraire la première production
        for p in data : 
            if p.ID == personne and p.n_burst == 1 : 
                p.rt_balise = process_deletions(p.charBurst.replace("␣", " "))
                premiere_prod = p
        
        # Pour chaque production (à l'exception de la première)
        for i in range(0, len(prod)) :

            # Si la production ne contient pas d'erreur liée aux données d'origine :
            if prod[i].charBurst != "Err :501" :

                # Traiter les 2 premières productions sans erreurs
                if prod[i].n_burst == 2 :
                    
                    chaine_avant = premiere_prod.burst[0:prod[i].startPos]
                    chaine_apres = premiere_prod.burst[prod[i].startPos::]
                    modif = prod[i].charBurst.replace("␣", " ")
                                        
                    # Si la modification n'est pas ajoutée au début du texte : 
                    if chaine_avant != "" : 
                        # Aligner les parties précédant et suivant la modification avec les caractères spéciaux
                        chaine_avant_ajustee, chaine_apres_ajustee = extraire_sequence(premiere_prod.rt_balise, chaine_avant)
                    # Sinon : 
                    else : 
                        # La chaîne après ajustée correspond au running text balisé  et la chaîne avant ajustée est vide
                        chaine_avant_ajustee, chaine_apres_ajustee = chaine_avant, premiere_prod.rt_balise
                    
                    # Si la production est ajoutée à la suite du texte, la séparer du reste du texte par un pipe
                    if prod[i].startPos == premiere_prod.docLength :
                        modif = "|" + modif
                    
                    elif prod[i].startPos == premiere_prod.endPos : 
                        modif = "|" + modif
                        
                    # Sinon (si la production est insérée à l'intérieur du texte existant) :
                    else :
                                                
                        # Si la chaîne insérée est une lettre/espace/ponctuation ajoutée, l'annoter entre chevrons
                        if len(prod[i].burst.strip()) == 1 or prod[i].charBurst == "␣" :
                            
                            if len(chaine_apres.strip()) == 0 : 
                                modif = "|" + modif
                            else : 
                                modif = "<" + modif
                            
                        # Sinon (si la chaîne insérée est un mot ou une suite de mots), l'annoter entre accolades
                        else :
                            
                            if len(chaine_apres.strip()) == 0 : 
                                modif = "|" + modif
                            else : 
                                modif = "{" + modif + "}"                            

                    # Incrémenter le running text balisé de la production avec la modification
                    prod[i].rt_balise = chaine_avant_ajustee + modif + chaine_apres_ajustee

                # Pour les autres productions :
                else :

                    # Corriger la catégorie de production
                    if prod[i].startPos == prod[i-1].docLength :
                        prod[i].categ == "P"
                    elif prod[i-1].startPos <= prod[i].startPos <= prod[i-1].endPos :
                        prod[i].categ == "R"
                    else :
                        prod[i].categ == "RB"

                    # Corriger la position de départ lorsqu'elle est plus élevée que la longueur du texte de la production précédente
                    if prod[i].startPos > prod[i-1].docLength :
                        prod[i].startPos = prod[i-1].docLength

                    # Identifier la modification à ajouter ainsi que la partie précédente
                    chaine_avant = prod[i-1].rt[0:prod[i].startPos]
                    chaine_apres = prod[i-1].rt[prod[i].startPos::]
                    modif = prod[i].charBurst.replace("␣", " ")
                    
                    # Si la modification n'est pas ajoutée au début du texte : 
                    if chaine_avant != "" : 
                        # Aligner les parties précédant et suivant la modification avec les caractères spéciaux
                        chaine_avant_ajustee, chaine_apres_ajustee = extraire_sequence(prod[i-1].rt_balise, chaine_avant)
                    # Sinon : 
                    else : 
                        # La chaîne après ajustée correspond au running text balisé  et la chaîne avant ajustée est vide
                        chaine_avant_ajustee, chaine_apres_ajustee = chaine_avant, prod[i-1].rt_balise
                        
                    # Si la production est ajoutée à la suite du texte, la séparer du reste du texte par un pipe
                    if prod[i].startPos == prod[i-1].docLength :
                        modif = "|" + modif
                    
                    elif prod[i].startPos == prod[i-1].endPos : 
                        modif = "|" + modif
                        
                    # Sinon (si la production est insérée à l'intérieur du texte existant) :
                    else :
                                                
                        # Si la chaîne insérée est une lettre/espace/ponctuation ajoutée, l'annoter entre chevrons
                        if len(prod[i].burst.strip()) == 1 or prod[i].charBurst == "␣" :
                            
                            if len(chaine_apres.strip()) == 0 : 
                                modif = "|" + modif
                            else : 
                                modif = "<" + modif
                            
                        # Sinon (si la chaîne insérée est un mot ou une suite de mots), l'annoter entre accolades
                        else :
                            
                            if len(chaine_apres.strip()) == 0 : 
                                modif = "|" + modif
                            else : 
                                modif = "{" + modif + "}"                            

                    # Incrémenter le running text balisé de la production avec la modification
                    prod[i].rt_balise = chaine_avant_ajustee + modif + chaine_apres_ajustee

            # Enregistrer le dernier running text balisé de la personne dans une variable "texte"
            texte = prod[i].rt_balise
        
        # Effectuer les suppressions par backspaces
        texte_avec_char_suppr = process_deletions(texte)

        # Nettoyer et corriger les annotations
        texte_nettoye = nettoyer_texte(texte_avec_char_suppr)
        
        # Enregistrer le texte de chaque personne dans le dictionnaire
        textes_reconstruits[personne] = texte_nettoye

    return textes_reconstruits



def enregistrer_dictionnaire(dictionnaire: Dict) -> None :
    """Enregistre les textes reconstruits de chaque personne dans un fichier dont le nom est l'identifiant du participant

    Parameters
    ----------
    dictionnaire : Dict
        dictionnaire où la clé est la personne et la valeur le texte reconstruit qu'il a tapé

    Returns
    -------
    None
    """

    # Créer le dossier "Textes_reconstruits" s'il n'existe pas
    dossier = "Textes_reconstruits"
    if not os.path.exists(dossier) :
        os.makedirs(dossier)

    # Pour chaque clé dans le dictionnaire, créer un fichier texte
    for cle, valeur in dictionnaire.items() :
        # Construire le chemin complet du fichier
        chemin_fichier = os.path.join(dossier, f"{cle}.txt")

        # Écrire la valeur dans le fichier
        with open(chemin_fichier, 'w', encoding='utf-8') as fichier :
            fichier.write(str(valeur))
    print('Les textes reconstruits ont bien été enregistrés dans le dossier "Textes_reconstruits"')



def main() :

    # Demander à l'utilisateur les noms des fichiers de données non annotées et annotées
    data_file = input("Nom du fichier csv ou tsv contenant les données non annotées : ")
    errors_file = input("Nom du fichier csv contenant les données avec l'annotation des erreurs : ")

    # Charger les lignes du csv planification
    liste_lignes = ouvrir_csv(data_file)

    # Charger les lignes erronnées
    lignes_erronnees = csv_to_lines(errors_file)

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

    # Reconstruire les textes avec les erreurs
    dico_textes_avec_erreurs = reconstruire_textes(annotation_erreurs)

    # Enregistrer les textes de chaque personne dans un fichier différent
    enregistrer_dictionnaire(dico_textes_avec_erreurs)



if __name__ == "__main__":
    main()
