#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 28 09:42:42 2024

@author: amandine
"""

"""Ce script permet de baliser le texte obtenu pour chaque personne avec les types d'erreurs identifiés."""




from ch_identify_errors import ouverture_csv
from ch_datastructure import Ligne, Production, Diff, AnLine
from typing import List, Dict
from tqdm import tqdm
import csv
from ch_pos_tagger import get_persons, add_burst_to_text
import re



def ouvrir_csv(file) -> List[AnLine] :
    with open (file, 'r', encoding='utf-8') as f:

        if file.endswith('.csv') :
            delim = ','
        if file.endswith('.tsv') :
            delim = '\t'

        reader = csv.reader(f, delimiter=delim) ## le delimiter de notre csv c'est des tabs
        next(reader, None)
        liste_lignes = []
        for row in reader:

            #line = Ligne(charBurst=row[16], texte_simple = row[11], categorie=row[15], start_position=int(row[12]), end_position=int(row[13]), doc_length=int(row[14]), id=row[0], n_burst=int(row[3]))

            line = AnLine(
                ID=row[0],
                charge=row[1],
                outil=row[2],
                n_burst=int(row[3]),
                debut_burst=float(row[4].replace(',', '.')) if row[4] else None,
                duree_burst=float(row[5].replace(',', '.')) if row[5] else None,
                duree_pause=float(row[6].replace(',', '.')) if row[6] else None,
                duree_cycle=float(row[7].replace(',', '.')) if row[7] else None,
                pct_burst=float(row[8].replace(',', '.')) if row[8] else None,
                pct_pause=float(row[9].replace(',', '.')) if row[9] else None,
                longueur_burst=int(row[10]),
                burst=row[11],
                startPos=int(row[12]),
                endPos=int(row[13]),
                docLength=int(row[14]),
                categ=row[15],
                charBurst=row[16],
                ratio=float(row[17].replace(',', '.')) if row[17] else None,

                erreur='False',
                cat_error='0',
                token_erronne='0',
                lemme='0',
                pos_suppose='0',
                pos_reel='0',
                longueur='0',
                contexte='0',
                correction='0',

                )

            liste_lignes.append(line)

        return liste_lignes



def csv_to_lines(file) -> List[AnLine] :
    with open (file, 'r', encoding='utf-8') as f:

        if file.endswith('.csv') :
            delim = ','
        if file.endswith('.tsv') :
            delim = '\t'

        reader = csv.reader(f, delimiter=delim) ## le delimiter de notre csv c'est des tabs
        next(reader, None)
        liste_lignes = []
        for row in reader:

            #line = Ligne(charBurst=row[16], texte_simple = row[11], categorie=row[15], start_position=int(row[12]), end_position=int(row[13]), doc_length=int(row[14]), id=row[0], n_burst=int(row[3]))

            line = AnLine(
                ID=row[0],
                charge=row[10],
                outil=row[11],
                n_burst=int(row[12]),
                debut_burst=float(row[13].replace(',', '.')) if row[13] else None,
                duree_burst=float(row[14].replace(',', '.')) if row[14] else None,
                duree_pause=float(row[15].replace(',', '.')) if row[15] else None,
                duree_cycle=float(row[16].replace(',', '.')) if row[16] else None,
                pct_burst=float(row[17].replace(',', '.')) if row[17] else None,
                pct_pause=float(row[18].replace(',', '.')) if row[18] else None,
                longueur_burst=int(row[19]),
                burst=row[20],
                startPos=int(row[21]),
                endPos=int(row[22]),
                docLength=int(row[23]),
                categ=row[24],
                charBurst=row[25],
                ratio=float(row[26].replace(',', '.')) if row[26] else None,

                erreur=row[5],
                cat_error=row[6],
                token_erronne=row[1],
                lemme=row[4],
                pos_suppose=row[3],
                pos_reel=row[2],
                longueur=row[7],
                contexte=row[8],
                correction=row[9]

                )

            liste_lignes.append(line)

        return liste_lignes



def combiner_lignes(liste: List[AnLine]) -> List[AnLine]:
    # Dictionnaire pour regrouper les lignes par (ID, n_burst)
    lignes_regroupees = {}

    # Parcourir la liste pour regrouper les lignes ayant les mêmes clés ID et n_burst
    for ligne in liste:
        cle = (ligne.ID,
               ligne.n_burst,
               ligne.charge,
               ligne.outil,
               ligne.debut_burst,
               ligne.duree_burst,
               ligne.duree_pause,
               ligne.duree_cycle,
               ligne.pct_burst,
               ligne.pct_pause,
               ligne.longueur_burst,
               ligne.burst,
               ligne.startPos,
               ligne.endPos,
               ligne.docLength,
               ligne.categ,
               ligne.charBurst,
               ligne.ratio,
               ligne.erreur,
               ligne.cat_error)

        if cle in lignes_regroupees:
            # Si la clé existe, ajouter les valeurs texte et lemme à la ligne correspondante
            lignes_regroupees[cle]['token_erronne'].append(ligne.token_erronne)
            lignes_regroupees[cle]['lemme'].append(ligne.lemme)
            lignes_regroupees[cle]['pos_suppose'].append(ligne.pos_suppose)
            lignes_regroupees[cle]['pos_reel'].append(ligne.pos_reel)
            lignes_regroupees[cle]['longueur'].append(ligne.longueur)
            lignes_regroupees[cle]['contexte'].append(ligne.contexte)
            lignes_regroupees[cle]['correction'].append(ligne.correction)

        else:
            # Si la clé n'existe pas, créer une nouvelle entrée dans le dictionnaire
            lignes_regroupees[cle] = {
                                      'token_erronne': [ligne.token_erronne],
                                      'lemme': [ligne.lemme],
                                      'pos_suppose': [ligne.pos_suppose],
                                      'pos_reel': [ligne.pos_reel],
                                      'longueur': [ligne.longueur],
                                      'contexte': [ligne.contexte],
                                      'correction': [ligne.correction]}


    # Créer une nouvelle liste de AnLine en combinant les valeurs texte et lemme pour chaque groupe
    lignes_combinees = []
    for cle, valeurs in lignes_regroupees.items():

        token_erronne_combine = '|'.join(valeurs['token_erronne'])
        lemme_combine = '|'.join(valeurs['lemme'])
        pos_suppose_combine = '|'.join(valeurs['pos_suppose'])
        pos_reel_combine = '|'.join(valeurs['pos_reel'])
        longueur_combine = '|'.join(valeurs['longueur'])
        contexte_combine = '|'.join(valeurs['contexte'])
        correction_combine = '|'.join(valeurs['correction'])


        lignes_combinees.append(AnLine(
            ID=cle[0],
            n_burst=cle[1],
            charge=cle[2],
            outil=cle[3],
            debut_burst=cle[4],
            duree_burst=cle[5],
            duree_pause=cle[6],
            duree_cycle=cle[7],
            pct_burst=cle[8],
            pct_pause=cle[9],
            longueur_burst=cle[10],
            burst=cle[11],
            startPos=cle[12],
            endPos=cle[13],
            docLength=cle[14],
            categ=cle[15],
            charBurst=cle[16],
            ratio=cle[17],
            erreur=cle[18],
            cat_error=cle[19],

            token_erronne=token_erronne_combine,
            lemme=lemme_combine,
            pos_suppose=pos_suppose_combine,
            pos_reel=pos_reel_combine,
            longueur=longueur_combine,
            contexte=contexte_combine,
            correction=correction_combine
            ))

    return lignes_combinees



def enrichir_productions(liste1: List[AnLine], liste2: List[AnLine]) -> List[AnLine]:
    # Nouvelle liste pour stocker les lignes mises à jour
    lignes_combinees = []

    # Créer un dictionnaire pour un accès rapide aux lignes de liste2 par (ID, n_burst)
    dict_liste2 = {(ligne.ID, ligne.n_burst): ligne for ligne in liste2}

    # Mettre à jour les lignes de liste1 avec les attributs correspondants de liste2
    for ligne1 in liste1:
        cle = (ligne1.ID, ligne1.n_burst)
        if cle in dict_liste2:
            ligne2 = dict_liste2[cle]
            # Créer une nouvelle ligne mise à jour et l'ajouter à la liste
            ligne_mise_a_jour = AnLine(
                ID=ligne1.ID,
                n_burst=ligne1.n_burst,
                charge=ligne2.charge,
                outil=ligne2.outil,
                debut_burst=ligne2.debut_burst,
                duree_burst=ligne2.duree_burst,
                duree_pause=ligne2.duree_pause,
                duree_cycle=ligne2.duree_cycle,
                pct_burst=ligne2.pct_burst,
                pct_pause=ligne2.pct_pause,
                longueur_burst=ligne2.longueur_burst,
                burst=ligne2.burst,
                startPos=ligne2.startPos,
                endPos=ligne2.endPos,
                docLength=ligne2.docLength,
                categ=ligne2.categ,
                charBurst=ligne2.charBurst,
                ratio=ligne2.ratio,
                erreur=ligne2.erreur,
                cat_error=ligne2.cat_error,
                token_erronne=ligne2.token_erronne,
                lemme=ligne2.lemme,
                pos_suppose=ligne2.pos_suppose,
                pos_reel=ligne2.pos_reel,
                longueur=ligne2.longueur,
                contexte=ligne2.contexte,
                correction=ligne2.correction
            )
            lignes_combinees.append(ligne_mise_a_jour)

    # Ajouter les lignes de liste1 qui n'ont pas de correspondance dans liste2
    for ligne1 in liste1:
        cle = (ligne1.ID, ligne1.n_burst)
        if cle not in dict_liste2:
            lignes_combinees.append(ligne1)

    # Trier les lignes selon leur burst
    liste_triee = sorted(lignes_combinees, key=lambda x: (x.ID, x.n_burst))

    return liste_triee



def recuperer_productions(list_lines: List[AnLine], personnes: Dict[str, List[AnLine]]) -> Dict[str, List] :
    """Renvoie un dictionnaire où on a pour chaque personne la liste de ses productions."""

    textes_produits_par_personne = {}

    for list_lines in tqdm(personnes.values(), desc='Identification des erreurs') :

        n=1
        running_text = list_lines[0].burst
        texte_produit_par_etapes = []

        for i in range(1,len(list_lines)):

            # Add this line to the document text so far
            running_text_after = add_burst_to_text(running_text, list_lines[i].charBurst, list_lines[i].startPos)

            # Update text for next iteration
            participant = list_lines[i].ID
            n += 1
            running_text = running_text_after
            #prod = Production(n, list_lines[i].burst, running_text, "balises")

            prod = Production(
                ID=list_lines[i].ID,
                charge=list_lines[i].charge,
                outil=list_lines[i].outil,
                n_burst=list_lines[i].n_burst,
                debut_burst=list_lines[i].debut_burst,
                duree_burst=list_lines[i].duree_burst,
                duree_pause=list_lines[i].duree_pause,
                duree_cycle=list_lines[i].duree_cycle,
                pct_burst=list_lines[i].pct_burst,
                pct_pause=list_lines[i].pct_pause,
                longueur_burst=list_lines[i].longueur_burst,
                burst=list_lines[i].burst,
                startPos	=list_lines[i].startPos,
                endPos=list_lines[i].endPos,
                docLength=list_lines[i].docLength,
                categ=list_lines[i].categ,
                charBurst=list_lines[i].charBurst,
                ratio=list_lines[i].ratio,

                erreur=list_lines[i].erreur,
                cat_error=list_lines[i].cat_error,
                token_erronne=list_lines[i].token_erronne,
                lemme=list_lines[i].lemme,
                pos_suppose=list_lines[i].pos_suppose,
                pos_reel=list_lines[i].pos_reel,
                longueur=list_lines[i].longueur,
                contexte=list_lines[i].contexte,
                correction=list_lines[i].correction,

                rt=running_text,
                rt_balise=running_text)

            texte_produit_par_etapes.append(prod)

        textes_produits_par_personne[participant] = texte_produit_par_etapes

    return textes_produits_par_personne



def difference_between(chaine_1, chaine_2) :

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




    # Suppression
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


        # Trouver la chaÃ®ne correspondant Ã  la diffÃ©rence
        diff = Diff(start_diff_index, end_diff_index, chaine_1[start_diff_index:end_diff_index])

        return diff




def trier_nburst(dico_personnes) :

    for personne in dico_personnes:
        dico_personnes[personne].sort(key=lambda x: x.n_burst)
    return dico_personnes



def baliser_erreurs(dico_prod) :

    for personne, prod in dico_prod.items() :

        # Pour chaque production de chaque personne :
        for i in range(1, len(prod)) :

            # 1. Si la production contient une erreur du type "Suppression de caractères à l'intérieur d'un mot" :
            if prod[i].cat_error == "Suppression de caractères à l'intérieur d'un mot" :

                # S'il y a une seule suppression interne :
                if len(prod[i].token_erronne.split('|')) == 1 :

                    # on balise le burst en remplaçant le token erroné par sa correction entre balises
                    burst_balise = prod[i].charBurst.replace(prod[i].token_erronne, f"<SI>{prod[i].correction}</SI>")

                    # on remplace les espaces "␣" du burst balisé par des espaces classiques
                    burst_balise_espaces = burst_balise.replace("␣", " ")

                    # on remplace le burst par le burst balisé dans le running texte
                    rt_balise = prod[i].rt.replace(prod[i].burst, burst_balise_espaces)
                    prod[i].rt_balise = rt_balise


                    #print(rt_balise)
                    #print("--------------------------------------------------------------------------------------")

                # S'il y a plusieurs suppressions internes :
                if len(prod[i].token_erronne.split('|')) > 1 :

                    # on recrée les couples (token erroné, correction)
                    err = prod[i].token_erronne.split('|')
                    corr = prod[i].correction.split('|')
                    couples = list(zip(err, corr))

                    charburst_balise = prod[i].charBurst

                    '''# pour chaque couple :
                    for couple in couples :

                        print(couple)
                        #burst_balise = prod[i].charBurst.replace(couple[0], f"<SI>{couple[1]}</SI>")
                        charburst_balise = charburst_balise.replace(couple[0], f"<SI>{couple[1]}</SI>")


                    print(charburst_balise)
                    print("--------------------------------------------------------------------------------------")'''






                    '''# Intégrer les balises au running text balisé
                    burst_sans_balises = charburst_balise_espaces.replace("<SI>", "")
                    burst_sans_balises = burst_sans_balises.replace("</SI>", "")
                    prod[i].rt_balise = prod[i].rt_balise.replace(burst_sans_balises, charburst_balise_espaces)

                    print(prod[i].charBurst)
                    print(prod[i].burst)
                    print(prod[i].token_erronne)
                    print(prod[i].correction)
                    print(prod[i].rt_balise)
                    print("-----------------------------------------")'''







def baliser_suppressions_internes(dico_prod) :

    for personne, prod in dico_prod.items() :

        # Pour chaque production de chaque personne :
        for i in range(1, len(prod)) :

            # 1. Si la production contient une erreur du type "Suppression de caractères à l'intérieur d'un mot" :
            if prod[i].cat_error == "Suppression de caractères à l'intérieur d'un mot" :

                # S'il y a une seule suppression interne :
                if len(prod[i].token_erronne.split('|')) == 1 :

                    # On balise le charburst dans une variable
                    charburst_balise = prod[i].charBurst.replace(prod[i].token_erronne, f"<SI>{prod[i].correction}</SI>")
                    charburst_balise_espaces = charburst_balise.replace("␣", " ")

                    # Intégrer les balises au running text balisé
                    burst_sans_balises = charburst_balise_espaces.replace("<SI>", "")
                    burst_sans_balises = burst_sans_balises.replace("</SI>", "")
                    prod[i].rt_balise = prod[i].rt_balise.replace(burst_sans_balises, charburst_balise_espaces)

                '''# S'il y a plusieurs suppressions internes :
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

                    # Intégrer les balises au running text balisé
                    burst_sans_balises = prod[i].charBurst.replace("<SI>", "")
                    burst_sans_balises = burst_sans_balises.replace("</SI>", "")
                    prod[i].rt_balise = prod[i].rt_balise.replace(burst_sans_balises, prod[i].charBurst)

                    print(f"{prod[i].charBurst}")'''

                # S'il y a plusieurs suppressions internes :
                if len(prod[i].token_erronne.split('|')) > 1 :

                    # On recrée les couples (token_errone, correction)
                    err = prod[i].token_erronne.split('|')
                    corr = prod[i].correction.split('|')
                    couples = list(zip(err, corr))

                    # On initialise le charburst qu'on va baliser
                    charburst_balise = prod[i].charBurst

                    # Pour chaque couple, on balise le charburst
                    for couple in couples :
                        charburst_balise = charburst_balise.replace(couple[0], f"<SI>{couple[1]}</SI>")
                        #prod[i].charBurst = charburst_balise.replace("␣", " ")
                        charburst_balise_espaces = charburst_balise.replace("␣", " ")
                        #charburst_balise_espaces = charburst_balise_espaces.replace("⌫", "")

                    #print(charburst_balise_espaces)

                    # Intégrer les balises au running text balisé
                    burst_sans_balises = charburst_balise_espaces.replace("<SI>", "")

                    burst_sans_balises = burst_sans_balises.replace("</SI>", "")

                    #toto = prod[i].rt_balise.replace(burst_sans_balises, charburst_balise_espaces)
                    #toto = prod[i].rt_balise.replace(prod[i].burst, charburst_balise_espaces)
                    toto = prod[i].rt.replace(prod[i].burst, charburst_balise_espaces)
                    prod[i].rt_balise = toto.replace("⌫", "")



                    '''print(prod[i].rt_balise)
                    #print(burst_sans_balises)
                    print(prod[i].burst)
                    print(charburst_balise_espaces)
                    print("**********")
                    print(toto)
                    print("**********")
                    print("-----------------------------------------------")'''

                    #prod[i].rt_balise = prod[i].rt_balise.replace(burst_sans_balises, charburst_balise_espaces)

                    #print(f"{prod[i].rt_balise}")

                print(prod[i].rt_balise)


            # 2. Si la production contient une erreur du type "Lettre unique ajoutée" :
            if prod[i].cat_error == "Lettre unique ajoutée" :

                modif = difference_between(prod[i-1].rt, prod[i].rt)

                # Si len(prod[i-1].rt) < len(prod[i].rt)  --> cas basique où une lettre est ajoutée (ex : remède -> remèdes) :
                if len(prod[i-1].rt) < len(prod[i].rt) :

                    # on balise le token erronné aux positions de la modif dans la production i
                    if modif.start != None and modif.end != None :
                        ch_avant_balises = prod[i].rt[0:modif.start]
                        ch_balisee = f"<LA>{prod[i].token_erronne}</LA>"
                        ch_apres_balises = prod[i].rt[modif.end-1:len(prod[i].rt)]
                        prod[i].rt_balise = ch_avant_balises + ch_balisee + ch_apres_balises

                # Sinon  --> cas où la lettre ajoutée remplace une autre lettre ou chaîne (ex : madecine -> médecine ; nous -> non) :
                else :

                    # on balise le token erronné aux positions de la modif dans la production i
                    if modif.start != None and modif.end != None :
                        ch_avant_balises = prod[i].rt[0:modif.start]
                        ch_balisee = f"<LR>{prod[i].token_erronne}</LR>"
                        ch_apres_balises = prod[i].rt[modif.end:len(prod[i].rt)]
                        prod[i].rt_balise = ch_avant_balises + ch_balisee + ch_apres_balises


            # 3. Si la production contient une erreur du type "Espace ajouté" :
            if prod[i].cat_error == "Espace ajouté" :

                modif = difference_between(prod[i-1].rt, prod[i].rt)

                # Si len(prod[i-1].rt) < len(prod[i].rt)  --> cas basique où un espace est ajouté (ex : eneffet -> en effet) :
                if len(prod[i-1].rt) < len(prod[i].rt) :

                    # on balise le token erronné aux positions de la modif dans la production i
                    if modif.start != None and modif.end != None :
                        ch_avant_balises = prod[i].rt[0:modif.start]
                        ch_balisee = f"<EA>{prod[i].token_erronne}</EA>"
                        ch_apres_balises = prod[i].rt[modif.end-1:len(prod[i].rt)]
                        prod[i].rt_balise = ch_avant_balises + ch_balisee + ch_apres_balises


                # Sinon  --> cas où l'espace ajouté remplace une lettre ou une chaîne (ex : enxeffet -> en effet ; enneeffet -> en effet) :
                else :

                    # on balise le token erronné aux positions de la modif dans la production i
                    if modif.start != None and modif.end != None :
                        ch_avant_balises = prod[i].rt[0:modif.start]
                        ch_balisee = f"<ER>{prod[i].token_erronne}</ER>"
                        ch_apres_balises = prod[i].rt[modif.end:len(prod[i].rt)]
                        prod[i].rt_balise = ch_avant_balises + ch_balisee + ch_apres_balises





            # 4. Si la production contient une erreur du type "Mot inséré entre deux mots" :
            if prod[i].cat_error == "Mot inséré entre deux mots" :

                modif = difference_between(prod[i-1].rt, prod[i].rt)

                if modif.start != None and modif.end != None :

                    # Si la différence et le token erroné sont identiques :
                    if modif.difference.strip() == prod[i].token_erronne.strip() :

                        # on balise le token erroné
                        ch_avant_balises = prod[i].rt[0:modif.start]
                        ch_balisee = f"<MI>{prod[i].token_erronne}</MI>"
                        ch_apres_balises = prod[i].rt[modif.end-1:len(prod[i].rt)]
                        prod[i].rt_balise = ch_avant_balises + ch_balisee + ch_apres_balises

                    # Sinon :
                    else :

                        # on trouve le nombre de caractères différents à gauche


                        # on trouve le nombre de caractères différents à droite



                        ch_avant_balises = prod[i].rt[0:modif.start]
                        ch_balisee = f"<MI>{prod[i].token_erronne}</MI>"
                        ch_apres_balises = prod[i].rt[modif.end-1:len(prod[i].rt)]
                        texte_balise = ch_avant_balises + ch_balisee + ch_apres_balises


                        #for mot in range(1, len(texte_balise.split())) :

                            #print(texte_balise[mot])

                            #if texte_balise[mot].endswith("<MI>") :
                                #print(texte_balise[mot])



                        '''print("----------------")
                        print(prod[i-1].n_burst)
                        print(prod[i-1].rt)
                        print()
                        print(prod[i].n_burst)
                        print(prod[i].rt)
                        print("***")
                        print(prod[i].token_erronne)
                        print(modif.difference)
                        print(texte_balise)
                        #print(prod[i].rt_balise)

                        print("----------------")'''



            if prod[i].cat_error == "Partie d'une chaîne insérée entre deux mots" :
                toto = "toto"

            if prod[i].cat_error == "Backspaces supprimant une chaîne" :
                toto = "toto"

            if prod[i].cat_error == "Deletes supprimant une chaîne" :
                toto = "toto"

            if prod[i].cat_error == "0" :
                toto = "toto"

            else :
                toto = "fini"

    return dico_prod






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

# Recuperer la liste des productions de chaque participant
productions_par_personne = recuperer_productions(lignes_enrichies, participants_ordre_nburst)



# Baliser le texte de chaque personne en fonction des types d'erreurs

# Baliser les suppressions internes (texte balisé stocké dans le charBurst)
#SI = baliser_suppressions_internes(productions_par_personne)

annotation_erreurs = baliser_erreurs(productions_par_personne)


'''for personne, prod in productions_par_personne.items() :

    # Pour chaque production de chaque personne :
    for i in range(0, len(prod)) :

        if prod[i].ID == "P+S19" :

            print(prod[i].n_burst)
            print(prod[i].rt)
            print()
            print(f"{prod[i].token_erronne} ; {prod[i].contexte} ; {prod[i].correction} ; {prod[i].startPos} ; {prod[i].endPos} ; {prod[i].cat_error}")
            print(prod[i].charBurst)
            print(prod[i].burst)
            print(prod[i-1].rt[0:prod[i].startPos])
            print(prod[i-1].rt[prod[i].startPos:prod[i].endPos])
            print(prod[i].rt[prod[i].startPos:prod[i].endPos])
            print("-"*100)'''


def corriger_chaine(chaine):
    result = []
    for char in chaine:
        if char == "⌫":
            if result:
                result.pop()  # Supprime le dernier caractère ajouté
        else:
            result.append(char)  # Ajoute le caractère au résultat
    return ''.join(result)


for personne, prod in productions_par_personne.items() :

    # Pour chaque production de chaque personne :
    for i in range(0, len(prod)) :

        if prod[i].ID == "P+S1" :

            # Si la production n'a pas d'erreur :
            if prod[i].cat_error == "0" :

                # Si son charBurst commence par ⌫ :
                if prod[i].charBurst.startswith("⌫") :

                    # On compte le nombre de ⌫ à la suite
                    n=0
                    for char in prod[i].charBurst :
                        if char =="⌫" :
                            n+=1
                        else :
                            break

                    couple = (prod[i-1].rt, n)


                    partie_a_supprimer = prod[i].rt[prod[i].startPos:prod[i].endPos]

                    #print(couple)
                    #print(prod[i].n_burst)

                    # On supprime les n derniers caractères du running text de la production précédente

                    #print(prod[i-1].rt.replace(" ", "␣"))

                    rt_avec_suppressions = prod[i-1].rt[:-n]
                    #print(rt_avec_suppressions)

                else :



                    #print(prod[i-1].rt.replace(" ", "␣"))

                    toto = prod[i-1].rt.replace(" ", "␣") + prod[i].burst.replace(" ", "␣")
                    #print(toto)
                    #print(prod[i].rt.replace(" ", "␣"))
                    #print("-"*150)

            if prod[i].cat_error == "Lettre unique ajoutée" :

                if len(prod[i].charBurst) == 1 :

                    if prod[i].charBurst == "␣" :

                        burst_balise = f"<EA>{prod[i].charBurst}</EA>"
                        rt_avant_ajout = prod[i].rt[0:prod[i].startPos]
                        lettre_ajoutee_balisee = burst_balise
                        rt_apres_ajout = prod[i].rt[prod[i].startPos+len(prod[i].charBurst)::]
                        rt_balise = rt_avant_ajout + lettre_ajoutee_balisee + rt_apres_ajout
                        prod[i].rt_balise = rt_balise

                    else :

                        burst_balise = f"<LA>{prod[i].charBurst}</LA>"
                        rt_avant_ajout = prod[i].rt[0:prod[i].startPos]
                        lettre_ajoutee_balisee = burst_balise
                        rt_apres_ajout = prod[i].rt[prod[i].startPos+len(prod[i].charBurst)::]
                        rt_balise = rt_avant_ajout + lettre_ajoutee_balisee + rt_apres_ajout
                        prod[i].rt_balise = rt_balise

                else :

                    if prod[i].charBurst.startswith("⌫") :

                        n=0
                        for char in prod[i].charBurst :
                            if char == "⌫" :
                                n+= 1
                            else :
                                break

                        if n == 1 :

                            burst_balise = f"<LR>{prod[i].burst}</LR>"
                            rt_avant_ajout = prod[i].rt[0:prod[i].startPos-n]
                            lettre_remplacante_balisee = burst_balise
                            rt_apres_ajout = prod[i-1].rt[prod[i].startPos::]
                            rt_balise = rt_avant_ajout + lettre_remplacante_balisee + rt_apres_ajout
                            prod[i].rt_balise = rt_balise

                        else :

                            burst_balise = f"<LS>{prod[i].burst}</LS>"
                            rt_avant_ajout = prod[i].rt[0:prod[i].startPos-n]
                            lettre_remplacante_balisee = burst_balise
                            rt_apres_ajout = prod[i-1].rt[prod[i].startPos::]
                            rt_balise = rt_avant_ajout + lettre_remplacante_balisee + rt_apres_ajout
                            prod[i].rt_balise = rt_balise


            if prod[i].cat_error == "Mot inséré entre deux mots" :

                burst_balise = f"<MI>{prod[i].burst}</MI>"
                rt_avant_insertion = prod[i-1].rt[0:prod[i].startPos]
                rt_apres_insertion = prod[i-1].rt[prod[i].startPos::]
                rt_balise = rt_avant_insertion + burst_balise + rt_apres_insertion
                prod[i].rt_balise = rt_balise


            if prod[i].cat_error == "Partie d'une chaîne insérée entre deux mots" :

                if prod[i].charBurst.startswith("⌫") :

                    n=0
                    for char in prod[i].charBurst :
                        if char == "⌫" :
                            n+= 1
                        else :
                            break

                    burst_balise = f"<CS>{prod[i].burst}</CS>"
                    rt_avant_ajout = prod[i].rt[0:prod[i].startPos-n]
                    lettre_remplacante_balisee = burst_balise
                    rt_apres_ajout = prod[i-1].rt[prod[i].startPos::]
                    rt_balise = rt_avant_ajout + lettre_remplacante_balisee + rt_apres_ajout
                    prod[i].rt_balise = rt_balise

                else :

                    burst_balise = f"<CI>{prod[i].burst}</CI>"
                    rt_avant_insertion = prod[i-1].rt[0:prod[i].startPos]
                    rt_apres_insertion = prod[i-1].rt[prod[i].startPos::]
                    rt_balise = rt_avant_insertion + burst_balise + rt_apres_insertion
                    prod[i].rt_balise = rt_balise


            if prod[i].cat_error == "Backspaces supprimant une chaîne" :

                n=0
                for char in prod[i].charBurst :
                    if char == "⌫" :
                        n+= 1

                chaine_supprimee_balisee = f"<SB>{prod[i].contexte}</SB>"
                rt_avant_suppression = prod[i-1].rt[0:prod[i].startPos-n]
                rt_apres_suppression = prod[i-1].rt[prod[i].startPos::]
                rt_balise = rt_avant_suppression + chaine_supprimee_balisee + rt_apres_suppression
                prod[i].rt_balise = rt_balise


            if prod[i].cat_error == "Deletes supprimant une chaîne" :

                n=0
                for char in prod[i].charBurst :
                    if char == "⌦" :
                        n+= 1

                chaine_supprimee_balisee = f"<SD>{prod[i].contexte}</SD>"
                rt_avant_suppression = prod[i-1].rt[0:prod[i].startPos]
                rt_apres_suppression = prod[i-1].rt[prod[i].startPos+n::]
                rt_balise = rt_avant_suppression + chaine_supprimee_balisee + rt_apres_suppression
                prod[i].rt_balise = rt_balise


            if prod[i].cat_error == "Suppression de caractères à l'intérieur d'un mot" :

                # S'il y a une seule suppression interne :
                if len(prod[i].token_erronne.split('|')) == 1 :

                    rt_avec_charburst = prod[i].rt[0:prod[i].startPos] + prod[i].charBurst
                    chaine_corrigee = corriger_chaine(rt_avec_charburst)

                    rt_avant_suppr_interne = chaine_corrigee[0:len(chaine_corrigee)-len(prod[i].burst)]
                    suppr_interne = chaine_corrigee[len(chaine_corrigee)-len(prod[i].burst):len(chaine_corrigee)+len(prod[i].burst)].replace("␣", " ")
                    suppr_interne_balisee = f"<SI>{suppr_interne}</SI>"

                    modif = difference_between(prod[i].rt, rt_avant_suppr_interne+suppr_interne)
                    rt_apres_suppr_interne = modif.difference

                    rt_balise = rt_avant_suppr_interne + suppr_interne_balisee + rt_apres_suppr_interne
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

                    # Intégrer les balises au running text balisé
                    burst_sans_balises = prod[i].charBurst.replace("<SI>", "")
                    burst_sans_balises = burst_sans_balises.replace("</SI>", "")
                    prod[i].rt_balise = prod[i].rt_balise.replace(burst_sans_balises, prod[i].charBurst)

                    print(f"{prod[i].charBurst}")

                    print(prod[i].rt)




                    print("-"*120)


























