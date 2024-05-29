#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 28 09:42:42 2024

@author: amandine
"""

"""Ce script permet de baliser le texte obtenu pour chaque personne avec les types d'erreurs identifiés."""




from identify_errors import ouverture_csv
from datastructure import Ligne, Production, Diff, AnLine
from typing import List, Dict
from tqdm import tqdm
import csv
from pos_tagger import get_persons, add_burst_to_text



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
            
            #lignes_regroupees[cle]['erreur'].append(ligne.erreur)
            #lignes_regroupees[cle]['cat_error'].append(ligne.cat_error)
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
                                        #'erreur': [ligne.erreur], 
                                        #'cat_error': [ligne.cat_error], 
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
        
        #erreur_combine = '|'.join(valeurs['erreur'])
        #cat_error_combine = '|'.join(valeurs['cat_error'])
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
            
            #erreur=erreur_combine, 
            #cat_error=cat_error_combine,
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

    return lignes_combinees



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
                    end_diff_index = len(chaine_1)+1 - index
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
                end_diff_index = len(chaine_1)+1 - index
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



def baliser_suppressions_internes(dico_prod) : 
    
    for personne, productions in dico_prod.items() : 
        
        # Pour chaque production de chaque personne : 
        for prod in productions : 
            
            # Si la production contient une erreur du type "Suppression de caractères à l'intérieur d'un mot" : 
            if prod.cat_error == "Suppression de caractères à l'intérieur d'un mot" : 
                
                # S'il y a une seule suppression interne : 
                if len(prod.token_erronne.split('|')) == 1 : 
                    
                    # On balise le charburst
                    charburst_balise = prod.charBurst.replace(prod.token_erronne, f"<SI>{prod.correction}</SI>")
                    prod.charBurst = charburst_balise.replace("␣", " ")
                    
                    # Intégrer les balises au running text balisé
                    burst_sans_balises = prod.charBurst.replace("<SI>", "")
                    burst_sans_balises = burst_sans_balises.replace("</SI>", "")
                    prod.rt_balise = prod.rt_balise.replace(burst_sans_balises, prod.charBurst)
                    
                                    
                # S'il y a plusieurs suppressions internes : 
                if len(prod.token_erronne.split('|')) > 1 : 
                    
                    # On recrée les couples (token_errone, correction)
                    err = prod.token_erronne.split('|')
                    corr = prod.correction.split('|')
                    couples = list(zip(err, corr))

                    # On initialise le charburst qu'on va baliser
                    charburst_balise = prod.charBurst
                    
                    # Pour chaque couple, on balise le charburst balisé
                    for couple in couples : 
                        charburst_balise = charburst_balise.replace(couple[0], f"<SI>{couple[1]}</SI>")
                    prod.charBurst = charburst_balise.replace("␣", " ")
                    
                    # Intégrer les balises au running text balisé
                    burst_sans_balises = prod.charBurst.replace("<SI>", "")
                    burst_sans_balises = burst_sans_balises.replace("</SI>", "")
                    prod.rt_balise = prod.rt_balise.replace(burst_sans_balises, prod.charBurst)
            
            
            # Si la production ne contient pas d'erreur de suppressions internes : 
            else : 
                
                # le charBurst reste tel quel
                prod.charBurst == prod.charBurst
                
    
    
    # Conserver toutes les annotations marquées par les balises à chaque production...   
    
    # Pour chaque production de chaque personne : 
        
        # Si le charburst contient des balises <SI> : 
            
            # On remplace le le burst par le charBurst dans le running text balisé
            
            # Le running text balisé de la production i+1 est égal au running text balisé de la production i + le 
    
    '''for pers, prod in dico_prod.items() : 
        #print("------------")
        #print(prod.rt_balise)
        
        for i in range(1, len(prod)) : 
            
            #print(prod[i].rt_balise)
            
            test = prod[i].rt_balise.replace(burst_sans_balises, prod[i-1].)'''
        
    
    for prod in dico_prod["P+S1"] : 
        print(f"{prod.ID}\t{prod.n_burst}\t{prod.rt_balise}")
        
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
SI = baliser_suppressions_internes(productions_par_personne)








'''for prod in productions_par_personne["P+S1"] : 
    print(prod.ID)
    print(prod.n_burst)
    print(prod.erreur)
    print(prod.cat_error)
    print(prod.rt)
    print("------------")
'''



'''for participant, productions in productions_par_personne.items() :

    # Itérer sur chaque production
    for i in range(1, len(productions)) :

        # Trouver la différence entre la production et celle d'avant
        modif = difference_between(productions[i].rt, productions[i-1].rt)
        
        
        # S'il n'y a pas de modification, le texte_balise correspond au running text
        if modif.start == None or modif.end == None or modif.difference == None :
            productions[i].rt_balise = productions[i].rt
            
        # S'il y a une modification :
        else :
            
            # Si la production est plus courte que la précédente : cas d'une suppression
            if len(productions[i].rt) < len(productions[i-1].rt) :

                prod_debut = productions[i-1].rt[0:modif.start]
                differ = modif.difference
                prod_fin = productions[i-1].rt[modif.end::]
                texte_balise = prod_debut + "<S>" + differ + "</S>" + prod_fin
                productions[i].rt_balise = texte_balise
                
            # Si la production est plus longue que la précédente : cas d'un ajout
            #if len(productions[i].rt) > len(productions[i-1].rt) :

            # Si un seul caractère est ajouté :
            if len(modif.difference.strip()) == 1 :

                # Si le caractère est un espace :
                if modif.difference.strip() == ' ' :

                    prod_debut = productions[i].rt[0:modif.start]
                    differ = modif.difference
                    prod_fin = productions[i].rt[modif.end::]
                    texte_balise = prod_debut + "<EA>" + differ + "</EA>" + prod_fin
                    productions[i].rt_balise = texte_balise

                # Si le caractère est une lettre
                else :

                    prod_debut = productions[i].rt[0:modif.start]
                    differ = modif.difference
                    prod_fin = productions[i].rt[modif.end::]
                    texte_balise = prod_debut + "<LA>" + differ + "</LA>" + prod_fin
                    productions[i].rt_balise = texte_balise
                    
            # Si plusieurs caractères sont ajoutés :
            else :

                # Si les caractères ajoutés correspondent à un mot :
                if len(modif.difference.split()) == 1 :

                    prod_debut = productions[i].rt[0:modif.start]
                    differ = modif.difference
                    prod_fin = productions[i].rt[modif.end::]
                    texte_balise = prod_debut + "<MI>" + differ + "</MI>" + prod_fin
                    productions[i].rt_balise = texte_balise

                # Si les caractères ajoutés correspondent à une chaîne de mots :
                else :

                    prod_debut = productions[i].rt[0:modif.start]
                    differ = modif.difference
                    prod_fin = productions[i].rt[modif.end::]
                    texte_balise = prod_debut + "<CI>" + differ + "</CI>" + prod_fin
                    productions[i].rt_balise = texte_balise'''


'''for participant, productions in productions_par_personne.items() : 
    if participant == "P+S1" : 
        for prod in productions : 
            print("------------")
            print(prod.n_burst)
            print()
            print(prod.rt_balise)
            print("------------")'''


