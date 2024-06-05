#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 10:02:35 2024

@author: amandine
"""

"""Ce script permet de baliser le texte obtenu pour chaque personne avec les types d'erreurs identifiés."""



from ch_enrichir_donnees import ouvrir_csv, csv_to_lines, combiner_lignes, enrichir_productions, get_persons, trier_nburst, recuperer_productions
from typing import Dict, List
from ch_datastructure import Diff, Production
from ch_outils_balisage import corriger_chaine, corriger_chaine_avec_balises, detecter_rb, difference_between, get_position_char_unique, remplacer_balise_si
from tqdm import tqdm
import re



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

    for personne, prod in tqdm(productions_par_personne.items(), desc="Balisage des erreurs") :

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
                        pattern = re.compile(r'(<SI>)(.*?)(</SI>)')

                        # On ajoute les attributs "prod" et "char" aux balises <SI>
                        pattern = re.compile(r'(<SI>)(.*?)(</SI>)')  # Récupération de toutes les balises avec leur contenu
                        compteur = [0]  # Utilisation d'une liste pour permettre la mise à jour dans lambda
                        rt_balise_normal_espaces_attributs = re.sub(
                            pattern,
                            lambda match: remplacer_balise_si(match, compteur),
                            rt_balise_normal_espaces
                        )

                        # On incrémente le running text balisé
                        prod[i].rt_balise = rt_balise_normal_espaces_attributs

                    # Sinon (si son charBurst ne commence par ⌫) :
                    else :

                        # Le running text balisé est égal au running text
                        prod[i].rt_balise = prod[i].rt


                # Si la production a pour erreur "Lettre unique ajoutée" :
                if prod[i].cat_error == "Lettre unique ajoutée" or prod[i].cat_error == "Espace unique ajouté" :

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
                        elif prod[i].burst.isalpha() :

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


                        # Sinon (s'il s'agit d'une ponctuation) :
                        else :

                            # On balise le burst <PA> pour "Ponctuation ajoutée"
                            burst_balise = f"<PA>{prod[i].charBurst}</PA>"

                            # On incrémente le running text balisé avec la ponctuation ajoutée balisée
                            rt_avant_ajout = prod[i].rt[0:prod[i].startPos]
                            lettre_ajoutee_balisee = burst_balise
                            rt_apres_ajout = prod[i].rt[prod[i].startPos+len(prod[i].charBurst)::]
                            rt_balise = rt_avant_ajout + lettre_ajoutee_balisee + rt_apres_ajout

                            # On ajoute les attributs "char", "mots", "operation", "suppr", et "position"
                            char = len(prod[i].burst)
                            mots = len(prod[i].burst.strip().split())
                            operation = 'ajout'
                            suppr = 0
                            position = get_position_char_unique(rt_balise, 'PA')
                            rt_balise = rt_balise.replace("<PA>", f"<PA char={char} mots={mots} operation='{operation}' suppr={suppr} position='{position}'>")
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


                            # Si le caractère ajouté est un espace :
                            if prod[i].burst == " " :

                                # S'il y a un seul backspace :
                                if n == 1 :

                                    # On balise l'espace ajouté <EA> pour "Espace ajouté"
                                    burst_balise = f"<EA>{prod[i].burst}</EA>"

                                    # On incrémente le running text balisé avec l'espace remplaçant balisé
                                    rt_avant_ajout = prod[i].rt[0:prod[i].startPos-n]
                                    lettre_remplacante_balisee = burst_balise
                                    rt_apres_ajout = prod[i-1].rt[prod[i].startPos::]
                                    rt_balise = rt_avant_ajout + lettre_remplacante_balisee + rt_apres_ajout

                                    # On ajoute les attributs "char", "mots", "operation", "suppr", et "position"
                                    char = len(prod[i].burst)
                                    mots = len(prod[i].burst.strip().split())
                                    operation = 'remplacement'
                                    suppr = n
                                    position = get_position_char_unique(rt_balise, 'EA')
                                    rt_balise = rt_balise.replace("<EA>", f"<EA char={char} mots={mots} operation='{operation}' suppr={suppr} position='{position}'>")
                                    prod[i].rt_balise = rt_balise

                                # Sinon (s'il y a plusieurs backspaces) :
                                else :

                                    # On balise l'espace ajouté <EA> pour "Espace ajouté"
                                    burst_balise = f"<EA>{prod[i].burst}</EA>"

                                    # On incrémente le running text balisé avec l'espace supprimant balisé
                                    rt_avant_ajout = prod[i].rt[0:prod[i].startPos-n]
                                    lettre_remplacante_balisee = burst_balise
                                    rt_apres_ajout = prod[i-1].rt[prod[i].startPos::]
                                    rt_balise = rt_avant_ajout + lettre_remplacante_balisee + rt_apres_ajout

                                    # On ajoute les attributs "char", "mots", "operation", "suppr", et "position"
                                    char = len(prod[i].burst)
                                    mots = len(prod[i].burst.strip().split())
                                    operation = 'suppression'
                                    suppr = n
                                    position = get_position_char_unique(rt_balise, 'EA')
                                    rt_balise = rt_balise.replace("<EA>", f"<EA char={char} mots={mots} operation='{operation}' suppr={suppr} position='{position}'>")
                                    prod[i].rt_balise = rt_balise


                            # S'il s'agit d'une lettre :
                            elif prod[i].burst.isalpha() :

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


                            # Sinon (si le caractère ajouté est une ponctuation) :
                            else :

                                # S'il y a un seul backspace :
                                if n == 1 :

                                    # On balise la ponctuation ajoutée <PA> pour "Ponctuation ajoutée"
                                    burst_balise = f"<PA>{prod[i].burst}</PA>"

                                    # On incrémente le running text balisé avec la ponctuation remplaçante balisée
                                    rt_avant_ajout = prod[i].rt[0:prod[i].startPos-n]
                                    lettre_remplacante_balisee = burst_balise
                                    rt_apres_ajout = prod[i-1].rt[prod[i].startPos::]
                                    rt_balise = rt_avant_ajout + lettre_remplacante_balisee + rt_apres_ajout

                                    # On ajoute les attributs "char", "mots", "operation", "suppr", et "position"
                                    char = len(prod[i].burst)
                                    mots = len(prod[i].burst.strip().split())
                                    operation = 'remplacement'
                                    suppr = n
                                    position = get_position_char_unique(rt_balise, 'PA')
                                    rt_balise = rt_balise.replace("<PA>", f"<PA char={char} mots={mots} operation='{operation}' suppr={suppr} position='{position}'>")
                                    prod[i].rt_balise = rt_balise

                                # Sinon (s'il y a plusieurs backspaces) :
                                else :

                                    # On balise la ponctuation ajoutée <PA> pour "Ponctuation ajoutée"
                                    burst_balise = f"<PA>{prod[i].burst}</PA>"

                                    # On incrémente le running text balisé avec la ponctuation supprimante balisée
                                    rt_avant_ajout = prod[i].rt[0:prod[i].startPos-n]
                                    lettre_remplacante_balisee = burst_balise
                                    rt_apres_ajout = prod[i-1].rt[prod[i].startPos::]
                                    rt_balise = rt_avant_ajout + lettre_remplacante_balisee + rt_apres_ajout

                                    # On ajoute les attributs "char", "mots", "operation", "suppr", et "position"
                                    char = len(prod[i].burst)
                                    mots = len(prod[i].burst.strip().split())
                                    operation = 'suppression'
                                    suppr = n
                                    position = get_position_char_unique(rt_balise, 'PA')
                                    rt_balise = rt_balise.replace("<PA>", f"<PA char={char} mots={mots} operation='{operation}' suppr={suppr} position='{position}'>")
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


                # Si la production a pour erreur "Suppression de caractères à l'intérieur d'un mot" :
                if prod[i].cat_error == "Suppression de caractères à l'intérieur d'un mot" :

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
                            pattern = re.compile(r'(<SI>)(.*?)(</SI>)')

                            # On ajoute les attributs "prod" et "char" aux balises <SI>
                            rt_balise_normal_espaces_attributs = re.sub(pattern, lambda match: f"<SI prod='interne' char={len(match.group(2))}>{match.group(2)}</SI>", rt_balise_normal_espaces)

                            # On incrémente le running text balisé
                            prod[i].rt_balise = rt_balise_normal_espaces_attributs

                        # Sinon (si les suppressions de la production affectent le running text) :
                        else :

                            # On insère le charburst de la production entre les parties du running text avant et après la modification
                            rt_normal = rt_avant_revision + prod[i].charBurst + rt_apres_revision

                            # On effectue le balisage des suppressions internes
                            rt_balise_normal = corriger_chaine_avec_balises(rt_normal)

                            # On remplace les espaces "␣" par des espaces simples
                            rt_balise_normal_espaces = rt_balise_normal.replace("␣", " ")

                            # On récupère toutes les balises avec leur contenu
                            pattern = re.compile(r'(<SI>)(.*?)(</SI>)')

                            # On ajoute les attributs "prod" et "char" aux balises <SI>
                            pattern = re.compile(r'(<SI>)(.*?)(</SI>)')  # Récupération de toutes les balises avec leur contenu
                            compteur = [0]  # Utilisation d'une liste pour permettre la mise à jour dans lambda
                            rt_balise_normal_espaces_attributs = re.sub(
                                pattern,
                                lambda match: remplacer_balise_si(match, compteur),
                                rt_balise_normal_espaces
                            )

                            # On incrémente le running text balisé
                            prod[i].rt_balise = rt_balise_normal_espaces_attributs


                    # Sinon (si la production n'est pas ajoutée à la suite du running text) :
                    else :

                        # Si les suppressions de la production n'affectent pas le running text :
                        if nb_char_avant_suppr >= nb_suppr :

                            # On insère le charburst de la production entre les parties du running text avant et après la modification entre balises <CI> pour "Chaîne insérée"
                            rt_ci_suite = rt_avant_revision + "<CI>" + prod[i].charBurst + "</CI>" + rt_apres_revision

                            # On effectue le balisage des suppressions internes
                            rt_balise_ci_suite = corriger_chaine_avec_balises(rt_ci_suite)

                            # On remplace les espaces "␣" par des espaces simples
                            rt_balise_ci_espaces_suite = rt_balise_ci_suite.replace("␣", " ")

                            # On récupère toutes les balises avec leur contenu
                            pattern = re.compile(r'(<SI>)(.*?)(</SI>)')

                            # On ajoute les attributs "prod" et "char" aux balises <SI>
                            rt_balise_ci_espaces_suite_attributs = re.sub(pattern, lambda match: f"<SI prod='interne' char={len(match.group(2))}>{match.group(2)}</SI>", rt_balise_ci_espaces_suite)

                            # On ajoute les attributs "char", "mots", "operation", et "suppr" à la balise <CI>
                            char = len(prod[i].burst)
                            mots = len(prod[i].burst.strip().split())
                            operation = 'ajout'
                            suppr = 0
                            rt_balise_ci_espaces_suite_attributs_ci = rt_balise_ci_espaces_suite_attributs.replace("<CI>", f"<CI char={char} mots={mots} operation='{op}' suppr={suppr}>")
                            prod[i].rt_balise = rt_balise_ci_espaces_suite_attributs_ci

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
                            #test_pendant = rt_balise_ci_espaces_milieu[len(rt_avant_revision)+(nb_char_avant_suppr-nb_suppr)::].replace(rt_apres_revision, "")
                            index = rt_balise_ci_espaces_milieu[len(rt_avant_revision)+(nb_char_avant_suppr-nb_suppr)::].find(rt_apres_revision)

                            # On s'en sert pour reconstituer la modification balisée
                            rt_pendant = rt_balise_ci_espaces_milieu[len(rt_avant_revision)+(nb_char_avant_suppr-nb_suppr)::][:index] + rt_balise_ci_espaces_milieu[len(rt_avant_revision)+(nb_char_avant_suppr-nb_suppr)::][index + len(rt_apres_revision):]

                            # On identifie la partie du running text après la modification
                            rt_apres = rt_apres_revision

                            # On insère la modification balisée entre balises <CI> pour "Chaîne insérée" entre les parties du running text avant et après la modification
                            rt_balise_ci_espaces_milieu_final = rt_avant + "<CI>" + rt_pendant + "</CI>" + rt_apres

                            # On récupère toutes les balises avec leur contenu
                            pattern = re.compile(r'(<SI>)(.*?)(</SI>)')

                            # On ajoute les attributs "prod" et "char" aux balises <SI>
                            pattern = re.compile(r'(<SI>)(.*?)(</SI>)')  # Récupération de toutes les balises avec leur contenu
                            compteur = [0]  # Utilisation d'une liste pour permettre la mise à jour dans lambda
                            rt_balise_ci_espaces_milieu_final_attributs = re.sub(
                                pattern,
                                lambda match: remplacer_balise_si(match, compteur),
                                rt_balise_ci_espaces_milieu_final
                            )

                            # On trouve le nombre de caractères supprimés dans le running text par la production et on en déduit l'opération
                            if nb_suppr-nb_char_avant_suppr == len(prod[i].burst) :
                                op = 'remplacement'
                            else :
                                op = 'suppression'

                            # On ajoute les attributs "char", "mots", "operation", et "suppr" à la balise <CI>
                            char = len(prod[i].burst)
                            mots = len(prod[i].burst.strip().split())
                            operation = op
                            suppr = nb_suppr-nb_char_avant_suppr
                            rt_balise_ci_espaces_milieu_final_attributs_ci = rt_balise_ci_espaces_milieu_final_attributs.replace("<CI>", f"<CI char={char} mots={mots} operation='{op}' suppr={suppr}>")
                            prod[i].rt_balise = rt_balise_ci_espaces_milieu_final_attributs_ci





                #if prod[i].ID == "P+S1" and prod[i].cat_error == "0" and prod[i].charBurst.startswith("⌫") :

                if prod[i].ID == "P+S1" and prod[i].cat_error == "Suppression de caractères à l'intérieur d'un mot" :

                #if prod[i].cat_error == "Lettre unique ajoutée" :


                    #print(f"{prod[i].ID}\t{prod[i].n_burst}\t{prod[i].burst}\t{prod[i].charBurst}\t{prod[i].rt_balise}")


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
                    #print(f"Production : {nb_char_avant_suppr >= nb_suppr}")
                    #print(f"Est ajouté à la suite du running text : {prod[i].rt.strip().endswith(prod[i].burst.strip())}")
                    #print()
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
