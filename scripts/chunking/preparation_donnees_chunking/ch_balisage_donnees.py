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
    for char in chaine:
        if char == "⌫":
            if result:
                result.pop()  # Supprime le dernier caractère ajouté
        else:
            result.append(char)  # Ajoute le caractère au résultat
    return ''.join(result)



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

                        toto = prod[i-1].rt.replace(" ", "␣") + prod[i].burst.replace(" ", "␣")

                        prod[i].rt_balise = prod[i].rt


                # Si la production a pour erreur "Lettre unique ajoutée" :
                if prod[i].cat_error == "Lettre unique ajoutée" :

                    # S'il s'agit simplement d'un caractère :
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

                                # On balise la lettre ajoutée <LR> pour "Lettre remplaçant une autre"
                                burst_balise = f"<LR>{prod[i].burst}</LR>"

                                # On incrémente le running text balisé avec la lettre remplaçante balisée
                                rt_avant_ajout = prod[i].rt[0:prod[i].startPos-n]
                                lettre_remplacante_balisee = burst_balise
                                rt_apres_ajout = prod[i-1].rt[prod[i].startPos::]
                                rt_balise = rt_avant_ajout + lettre_remplacante_balisee + rt_apres_ajout
                                prod[i].rt_balise = rt_balise

                            # Sinon (s'il y a plusieurs backspaces) :
                            else :

                                # On balise la lettre ajoutée <LS> pour "Lettre supprimant une chaîne"
                                burst_balise = f"<LS>{prod[i].burst}</LS>"

                                # On incrémente le running text balisé avec la lettre supprimante balisée
                                rt_avant_ajout = prod[i].rt[0:prod[i].startPos-n]
                                lettre_remplacante_balisee = burst_balise
                                rt_apres_ajout = prod[i-1].rt[prod[i].startPos::]
                                rt_balise = rt_avant_ajout + lettre_remplacante_balisee + rt_apres_ajout
                                prod[i].rt_balise = rt_balise


                # Si la production a pour erreur "Mot inséré entre deux mots" :
                if prod[i].cat_error == "Mot inséré entre deux mots" :

                    # On balise le burst <MI> pour "Mot inséré"
                    burst_balise = f"<MI>{prod[i].burst}</MI>"

                    # On incrémente le running text balisé avec le mot inséré balisé
                    rt_avant_insertion = prod[i-1].rt[0:prod[i].startPos]
                    rt_apres_insertion = prod[i-1].rt[prod[i].startPos::]
                    rt_balise = rt_avant_insertion + burst_balise + rt_apres_insertion
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

                        # On balise le burst <CS> pour "Chaîne supprimant une chaîne"
                        burst_balise = f"<CS>{prod[i].burst}</CS>"

                        # On incrémente le running text balisé avec la chaîne insérée balisée
                        rt_avant_ajout = prod[i].rt[0:prod[i].startPos-n]
                        lettre_remplacante_balisee = burst_balise
                        rt_apres_ajout = prod[i-1].rt[prod[i].startPos::]
                        rt_balise = rt_avant_ajout + lettre_remplacante_balisee + rt_apres_ajout
                        prod[i].rt_balise = rt_balise

                    # Sinon (si le charburst ne commence pas par un backspace) :
                    else :

                        # On balise le burst <CI> pour "Chaîne insérée"
                        burst_balise = f"<CI>{prod[i].burst}</CI>"

                        # On incrémente le running text balisé avec la chaîne insérée balisée
                        rt_avant_insertion = prod[i-1].rt[0:prod[i].startPos]
                        rt_apres_insertion = prod[i-1].rt[prod[i].startPos::]
                        rt_balise = rt_avant_insertion + burst_balise + rt_apres_insertion
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
                    prod[i].rt_balise = rt_balise


                # Si la production a pour erreur "Suppression de caractères à l'intérieur d'un mot" :
                if prod[i].cat_error == "Suppression de caractères à l'intérieur d'un mot" :

                    # S'il y a une seule suppression interne :
                    if len(prod[i].token_erronne.split('|')) == 1 :

                        # On ajoute le charburst au running texte qui se situe avant la position de départ du curseur
                        rt_avec_charburst = prod[i].rt[0:prod[i].startPos] + prod[i].charBurst

                        # On corrige la chaine en effectuant les supprressions indiquées dans le burst
                        chaine_corrigee = corriger_chaine(rt_avec_charburst)

                        # On balise la suppression interne <SI> pour "Suppression interne"
                        suppr_interne = chaine_corrigee[len(chaine_corrigee)-len(prod[i].burst):len(chaine_corrigee)+len(prod[i].burst)].replace("␣", " ")
                        suppr_interne_balisee = f"<SI>{suppr_interne}</SI>"

                        # On identifie la position de début de la chaîne contenant des suppressions internes
                        rt_avant_suppr_interne = chaine_corrigee[0:len(chaine_corrigee)-len(prod[i].burst)]

                        # On trouve la différence entre le running text et le runnung text avant la chaîne contenant les suppressions internes auquel on a ajouté cette chaîne
                        modif = difference_between(prod[i].rt, rt_avant_suppr_interne+suppr_interne)

                        # On retrouve à partir de cette différence la partie du running text qui suit la chaîne cintenant les suppressions internes
                        rt_apres_suppr_interne = modif.difference

                        # S'il n'y a pas de différence :
                        if rt_apres_suppr_interne == None :

                            # On concatène le running text avant la suppression interne avec la suppression interne balisée
                            rt_balise = rt_avant_suppr_interne + suppr_interne_balisee

                        # Sinon :
                        else :

                            # On concatène le running text avant la suppression interne avec la suppression interne balisée et le running text après la suppression interne
                            rt_balise = rt_avant_suppr_interne + suppr_interne_balisee + rt_apres_suppr_interne

                        # On incrémente le running text
                        prod[i].rt_balise = corriger_chaine(rt_balise)


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



                if prod[i].ID == "P+S1" :
                    print(prod[i].n_burst)
                    print()
                    print(prod[i].cat_error)
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
