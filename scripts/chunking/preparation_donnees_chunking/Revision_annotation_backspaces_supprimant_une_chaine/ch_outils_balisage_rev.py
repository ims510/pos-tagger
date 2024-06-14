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
                result.append('<ID>' + ''.join(suppr_char[::-1]) + '</ID>')
                suppr_char = []
            result.append(chaine[i])
        i += 1

    if suppr_char:
        result.append('<ID>' + ''.join(suppr_char[::-1]) + '</ID>')

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
            position_lettre = (position, nb_char)

            # Associer au tuple une valeur entre début, milieu, et fin
            if position == 1 :
                position_str = "start"
            if position == nb_char :
                position_str = "end"
            else :
                position_str = "middle"

            result = (position_str, position_lettre)
            
            return result



def remplacer_balise_si(match, compteur) :
    """
    Remplace une balise <ID> par une nouvelle balise <ID> avec les attributs prod et char ajoutés.

    Parameters
    ----------
    match: re.Match
        Objet correspondant à la balise <ID> et son contenu.
    compteur: list
        Liste contenant le compteur pour suivre le nombre de remplacements

    Returns
    -------
    str
        La nouvelle balise <ID> avec les attributs prod et char ajoutés
    """
    
    # Déterminer les attributs prod et char
    prod_value = "preceding" if compteur[0] == 0 else "local"
    contenu = match.group(2)
    longueur = len(contenu)
    
    # Incrémenter le compteur
    compteur[0] += 1
    
    # Retourner la nouvelle balise SI avec les attributs ajoutés
    return f'<ID scope="{prod_value}" char={longueur}>{contenu}</ID>'



def get_nb_char(chaine: str) -> str :
    """Renvoie le nombre de backspaces successifs dans une chaîne.

    Parameters
    ----------
    chaine : str
        chaîne contenant des backspaces

    Returns
    -------
    str
        chaîne où chaque séquence de backspaces est séparée par un pipe
    """
    suppression_counts = []
    count = 0
    for char in chaine :
        if char == '⌫' :
            count += 1
        else:
            if count > 0 :
                suppression_counts.append(str(count))
                count = 0
    if count > 0 :
        suppression_counts.append(str(count))
    return '|'.join(suppression_counts)



def find_difference(chaine1: str, chaine2: str):
    # Trouver la longueur minimale entre les deux cha√Ænes
    min_len = min(len(chaine1), len(chaine2))
    start_diff = None
    
    # Trouver le d√©but de la diff√©rence
    for i in range(min_len):
        if chaine1[i] != chaine2[i]:
            start_diff = i
            break
    
    # Si start_diff est toujours None, cela signifie que les d√©buts des deux cha√Ænes sont identiques
    if start_diff is None:
        # La diff√©rence commence apr√®s la fin de la cha√Æne la plus courte
        if len(chaine1) == len(chaine2):
            return "", -1, -1
        else:
            start_diff = min_len
    
    # Trouver la fin de la diff√©rence
    end_diff_chaine1 = len(chaine1)
    end_diff_chaine2 = len(chaine2)
    
    # Capturer les diff√©rences sp√©cifiques
    difference = chaine2[start_diff:end_diff_chaine2]
    
    return difference, start_diff, end_diff_chaine2



def extract_tags(html: str, tag: str) -> list:
    # Construire le pattern regex pour détecter les balises <tag> avec ou sans attributs
    pattern = re.compile(rf'<{tag}(\s[^>]*)?>.*?</{tag}>', re.IGNORECASE | re.DOTALL)
    
    # Rechercher toutes les occurrences du pattern dans la chaîne HTML
    matches = pattern.findall(html)
    
    # Utiliser re.findall sans les groupes capturés pour obtenir les balises complètes
    matches = re.findall(rf'<{tag}(?:\s[^>]*)?>.*?</{tag}>', html, re.IGNORECASE | re.DOTALL)
    
    return matches



def extract_deletion(tag):
    match = re.search(r"deletion=(\d+)", tag)
    if match:
        return int(match.group(1))
    return None



def extract_char(tag):
    match = re.search(r"char=(\d+)", tag)
    if match:
        return int(match.group(1))
    return None



def extract_content(tag):
    match = re.search(r">([^<]+)<", tag)
    if match:
        return match.group(1)
    return None



"""def supprimer_caracteres(chaine, n):
    caracteres_speciaux = {'|', '~'}
    caracteres_non_comptes = {'<', '>', '{', '}'}
    compteur = 0
    resultat = []

    for char in chaine:
        if char in caracteres_speciaux:
            resultat.append(char)
        elif char in caracteres_non_comptes:
            continue
        elif compteur < n:
            compteur += 1
        else:
            resultat.append(char)

    return ''.join(resultat)"""



def supprimer_caracteres(chaine, n):
    caracteres_speciaux = {'|', '~'}
    caracteres_non_comptes = {'<', '>', '{', '}'}
    compteur = 0
    resultat = []
    
    liste = []
    for char in chaine : 
        if char in caracteres_speciaux : 
            liste.append((char, compteur))
        elif char in caracteres_non_comptes : 
            liste.append((char, compteur))
        else : 
            compteur += 1
            liste.append((char, compteur))
            
    for ele in liste : 
        if ele[1] <= n : 
            if ele[0] in caracteres_speciaux : 
                resultat.append(ele[0])
        else : 
            resultat.append(ele[0])
    
    return ''.join(resultat)



def extraire_sequence_v1(chaine_speciale, chaine_sans_speciale):
    resultat = []
    reste = []
    index_sans_speciale = 0
    longueur_sans_speciale = len(chaine_sans_speciale)
    ignorer = False
    sequence_complete = False

    for char in chaine_speciale:
        if char == '#':
            ignorer = not ignorer
            continue

        if ignorer:
            continue

        if not sequence_complete:
            if index_sans_speciale < longueur_sans_speciale and char == chaine_sans_speciale[index_sans_speciale]:
                resultat.append(char)
                index_sans_speciale += 1
                if index_sans_speciale == longueur_sans_speciale:
                    sequence_complete = True
            elif char in "|~<>{}":
                resultat.append(char)
            elif char not in chaine_sans_speciale[index_sans_speciale:]:
                break  # Sortir de la boucle si le caractère n'est pas dans la séquence sans caractères spéciaux
        else:
            reste.append(char)

    reste.extend(chaine_speciale[len(resultat)+len(reste):])

    return ''.join(resultat), ''.join(reste)



def extraire_sequence_v2(chaine_speciale, chaine_sans_speciale):
    resultat = []
    reste = []
    index_sans_speciale = 0
    longueur_sans_speciale = len(chaine_sans_speciale)
    ignorer = False
    sequence_complete = False

    for char in chaine_speciale:
        if char == '#':
            ignorer = not ignorer
            continue

        if ignorer:
            continue

        if not sequence_complete:
            if index_sans_speciale < longueur_sans_speciale and char == chaine_sans_speciale[index_sans_speciale]:
                resultat.append(char)
                index_sans_speciale += 1
                if index_sans_speciale == longueur_sans_speciale:
                    sequence_complete = True
            elif char in "|~<>{}":
                resultat.append(char)
            else:
                # Si on rencontre un caractère qui ne fait pas partie de la séquence sans caractères spéciaux,
                # on arrête d'ajouter des caractères à resultat et on passe à la partie reste.
                sequence_complete = True
        else:
            # On ajoute à reste les caractères restants de chaine_speciale sans inclure les caractères spéciaux.
            if char not in "|~<>{}":
                reste.append(char)

    return ''.join(resultat), ''.join(reste)



def extraire_sequence(chaine_speciale, chaine_sans_speciale):

    resultat = []
    reste = []
    index_sans_speciale = 0
    longueur_sans_speciale = len(chaine_sans_speciale)
    ignorer = False
    sequence_complete = False

    for char in chaine_speciale:
        """if char == '#':
            ignorer = not ignorer
            continue

        if ignorer:
            continue"""

        if not sequence_complete:
            if index_sans_speciale < longueur_sans_speciale and char == chaine_sans_speciale[index_sans_speciale]:
                resultat.append(char)
                index_sans_speciale += 1
                if index_sans_speciale == longueur_sans_speciale:
                    sequence_complete = True
            elif char in "|~<>{}#":
                resultat.append(char)
                # Si on ajoute un caractère spécial à resultat, on vérifie si la séquence est complète
                if index_sans_speciale < longueur_sans_speciale and char == chaine_sans_speciale[index_sans_speciale]:
                    index_sans_speciale += 1
                    if index_sans_speciale == longueur_sans_speciale:
                        sequence_complete = True
            else:
                # Si on rencontre un caractère qui ne fait pas partie de la séquence sans caractères spéciaux,
                # on ajoute ce caractère à resultat mais on ne change pas sequence_complete.
                resultat.append(char)
        else:
            # On ajoute à reste tous les caractères restants de chaine_speciale.
            reste.append(char)

    return ''.join(resultat), ''.join(reste)




def extraire_sequence_v_infinie(chaine_speciale, chaine_sans_speciale):
    resultat = []
    reste = []
    index_sans_speciale = 0
    longueur_sans_speciale = len(chaine_sans_speciale)
    ignorer = False
    sequence_complete = False

    for char in chaine_speciale:
        if char == '#':
            ignorer = not ignorer
            continue

        if ignorer:
            continue

        if not sequence_complete:
            if index_sans_speciale < longueur_sans_speciale and char == chaine_sans_speciale[index_sans_speciale]:
                resultat.append(char)
                index_sans_speciale += 1
                if index_sans_speciale == longueur_sans_speciale:
                    sequence_complete = True
            elif char in "|~<>{}":
                resultat.append(char)
                if index_sans_speciale < longueur_sans_speciale and char == chaine_sans_speciale[index_sans_speciale]:
                    index_sans_speciale += 1
                    if index_sans_speciale == longueur_sans_speciale:
                        sequence_complete = True
            else:
                # Si on rencontre un caractère qui ne fait pas partie de la séquence sans caractères spéciaux,
                # on ajoute ce caractère à la fois à resultat et à reste.
                resultat.append(char)
                reste.append(char)
        else:
            # On ajoute à reste les caractères restants de chaine_speciale sans inclure les caractères spéciaux.
            reste.append(char)

    return ''.join(resultat), ''.join(reste)


'''def calculate_insertion_position(chaine_sans_speciaux, chaine_avec_speciaux, position_insertion_sans_speciaux, chaine_a_inserer, balise, longueur_ajout):

    special_chars = "|<>~{}"
    real_position = 0
    adjusted_position = 0
    
    while adjusted_position < position_insertion_sans_speciaux and real_position < len(chaine_avec_speciaux):
        if chaine_avec_speciaux[real_position] not in special_chars:
            adjusted_position += 1
        real_position += 1
    
    if balise == "BD" : 
        result = chaine_avec_speciaux[0:real_position] + chaine_a_inserer + chaine_avec_speciaux[real_position+longueur_ajout::]
    else : 
        result = chaine_avec_speciaux[0:real_position] + chaine_a_inserer + chaine_avec_speciaux[real_position::]

    return result'''



def calculate_insertion_position_v2(chaine_sans_speciaux, chaine_avec_speciaux, position_insertion_sans_speciaux, chaine_a_inserer, balise, longueur_ajout, fin_insertion):

    chaine_avant = chaine_avec_speciaux[0:position_insertion_sans_speciaux]


    pauses = re.findall(r'\|', chaine_avant)
    somme_pauses=0
    for pause in pauses : 
        somme_pauses += 1

    si = re.findall('~', chaine_avant)
    somme_si=0
    for s in si : 
        somme_si += 1

    sequences_supprimees = re.findall(r'(#[^#]*#)', chaine_avant)
    longueurs_suppr = []
    for seq in sequences_supprimees : 
        longueurs_suppr.append(len(seq))
    somme_suppr=0
    for nb in longueurs_suppr : 
        somme_suppr += nb

    lettres_ajoutees_apres = re.findall(r'[<>]', chaine_avant)
    longueurs_lettres_ajout = []
    for seq in lettres_ajoutees_apres : 
        longueurs_lettres_ajout.append(len(seq))
    somme_lettres_ajout=0
    for nb in longueurs_lettres_ajout : 
        somme_lettres_ajout += nb

    sequences_ajoutees_apres = re.findall(r'[{}]', chaine_avant)
    longueurs_ajout = []
    for seq in sequences_ajoutees_apres : 
        longueurs_ajout.append(len(seq))
    somme_ajout=0
    for nb in longueurs_ajout : 
        somme_ajout += nb

    somme_modifs = somme_pauses + somme_si + somme_suppr + somme_ajout + somme_lettres_ajout
    chaine_avant_ajustee = chaine_avec_speciaux[0:position_insertion_sans_speciaux+somme_modifs]



    pauses = re.findall(r'\|', chaine_avant_ajustee)
    somme_pauses=0
    for pause in pauses : 
        somme_pauses += 1
    
    si = re.findall('~', chaine_avant_ajustee)
    somme_si=0
    for s in si : 
        somme_si += 1

    sequences_supprimees = re.findall(r'(#[^#]*#)', chaine_avant_ajustee)
    longueurs_suppr = []
    for seq in sequences_supprimees : 
        longueurs_suppr.append(len(seq))
    somme_suppr=0
    for nb in longueurs_suppr : 
        somme_suppr += nb

    lettres_ajoutees_apres = re.findall(r'[<>]', chaine_avant_ajustee)
    longueurs_lettres_ajout = []
    for seq in lettres_ajoutees_apres : 
        longueurs_lettres_ajout.append(len(seq))
    somme_lettres_ajout=0
    for nb in longueurs_lettres_ajout : 
        somme_lettres_ajout += nb

    sequences_ajoutees_apres = re.findall(r'[{}]', chaine_avant_ajustee)
    longueurs_ajout = []
    for seq in sequences_ajoutees_apres : 
        longueurs_ajout.append(len(seq))
    somme_ajout=0
    for nb in longueurs_ajout : 
        somme_ajout += nb

    somme_modifs = somme_pauses + somme_si + somme_suppr + somme_ajout + somme_lettres_ajout
    #chaine_avant_ajustee_bis = chaine_avec_speciaux[0:position_insertion_sans_speciaux+somme_modifs]
    chaine_avant_ajustee_bis = chaine_avec_speciaux[0:len(chaine_sans_speciaux[0:position_insertion_sans_speciaux])+somme_modifs]




    
    print("chaine_sans_speciaux : ")
    print(chaine_sans_speciaux[0:position_insertion_sans_speciaux])
    
    print(f"somme_modifs : {somme_modifs}")
    print(f"somme_pauses : {somme_pauses}")
    print(f"somme_si : {somme_si}")
    print(f"somme_suppr : {somme_suppr}")
    print(f"somme_ajout : {somme_ajout}")
    print(f"somme_lettres_ajout : {somme_lettres_ajout}")
    
    
    #print("chaine_avec_speciaux : ")
    #print(chaine_avec_speciaux)
    
    print("chaine_avant_ajustee_bis : ")
    print(chaine_avant_ajustee_bis)
    
    chaine_apres = chaine_avec_speciaux[len(chaine_avant_ajustee_bis)::]
    print("chaine_apres : ")
    print(chaine_apres)
    
    
    nb_suppr = 0
    
    if chaine_apres.startswith("}") : 
        chaine_a_inserer = "}" + chaine_a_inserer
    #elif chaine_a_inserer.startswith("<") : 
        #chaine_a_inserer = chaine_a_inserer.replace("<", "")
    #else : 
        #chaine_a_inserer = chaine_a_inserer
    
    for char in chaine_a_inserer.replace("{", "") : 
        if char == "~" : 
            nb_suppr += 1
        else : 
            break
    
    #print("nb_suppr : ")
    #print(nb_suppr)
    
    
    chaine_apres_ajustee = supprimer_caracteres(chaine_apres, nb_suppr)
    
    if chaine_apres_ajustee.startswith("}") : 
        chaine_a_inserer = "}" + chaine_a_inserer
        chaine_apres_ajustee = chaine_apres_ajustee[:-1]
    
    if chaine_apres_ajustee.startswith("<") : 
        chaine_a_inserer = "<" + chaine_a_inserer
    
    print("chaine_a_inserer : ")
    print(chaine_a_inserer)
    
    print("chaine_apres_ajustee : ")
    print(chaine_apres_ajustee)

    
    
    
    
    
    
    
    
    # Ecrire une fonction qui, étant donné une chaîne de caractères et un nombre n,
    # supprime les n premiers caractères de la chaîne lorsqu'ils ne sont pas des caractères spéciaux.
    # Quand on rencontre un caractère spécial, on passe au caractère suivant jusqu'à supprimer n caractères.
    
    # Exemple : 
    # chaine = "|,<␣> certain~s remède<s> sont enc~ore utilisés |à nos jours|."
    # n = 2
    # resultat_souhaite == "| certain~s remède<s> sont enc~ore utilisés |à nos jours|."
    
    
    # Remarque : les caractères spéciaux sont les "|" et les "~".
    
    # Par contre, si le caractère rencontré est un chevron (ouvrant ou fermant) ou une accolade (ouvrante ou fermante), 
    # on supprime le caractère mais sans ajouter cette suppression au compte de suppressions de caractères.
    
    # Voici le processus plus en détails pour notre exemple : 
        
        # | --> caractère spécial donc on passe au suivant --> n=0
        # , --> caractère normal donc on supprime le caractère et on ajoute 1 au compteur de suppressions --> compteur=1 (<=n)
        # < --> chevron donc on supprime le caractère sans ajouter 1 au compteur de suppressions --> compteur=1 (<=n)
        # ␣ --> caractère normal donc on supprime le caractère et on ajoute 1 au compteur de suppressions --> compteur=2 (<=n)
        # > --> chevron donc on supprime le caractère sans ajouter 1 au compteur de suppressions --> compteur=2 (<=n)
        #   --> caractère normal donc on devrait le supprimer mais si on le supprimer, le compteur de suppressions dépasse n donc on ne le supprime pas et on arrête. --> compteur=2 (<=n)

    
    
    
    if balise == "BD" or balise == "AL" or balise == "AP" or balise == "AS" : 
        result = chaine_avant_ajustee_bis + chaine_a_inserer + chaine_avec_speciaux[position_insertion_sans_speciaux+somme_modifs+longueur_ajout::]
    elif balise == "IS" or balise == "IW" : 
        result = chaine_avant_ajustee_bis + chaine_a_inserer + chaine_apres_ajustee
    else : 
        result = chaine_avant_ajustee_bis + chaine_a_inserer + chaine_avec_speciaux[position_insertion_sans_speciaux+somme_modifs::]

    return result




def calculate_insertion_position(chaine_sans_speciaux, chaine_avec_speciaux, position_insertion_sans_speciaux, chaine_a_inserer, balise, longueur_ajout, fin_insertion):
    
    print("chaine_avec_speciaux : ")
    print(chaine_avec_speciaux)
    print()
    print("chaine_sans_speciaux[0:position_insertion_sans_speciaux] : ")
    print(chaine_sans_speciaux[0:position_insertion_sans_speciaux])
    chaine_avant_ajustee, chaine_apres_ajustee = extraire_sequence(chaine_avec_speciaux, chaine_sans_speciaux[0:position_insertion_sans_speciaux])

    print()
    print("chaine_avant_ajustee : ")
    print(chaine_avant_ajustee)
    print("chaine_apres_ajustee : ")
    print(chaine_apres_ajustee)
    
    
    '''if chaine_apres_ajustee.startswith("<") : 
        print("KUJUJ")
        chaine_a_inserer = chaine_a_inserer + "<"'''


    
    
    nb_suppr = 0
    
    if chaine_apres_ajustee.startswith("}") : 
        chaine_a_inserer = "}" + chaine_a_inserer
    
    for char in chaine_a_inserer.replace("{", "").replace("<", "") : 
        if char == "~" : 
            nb_suppr += 1
        else : 
            break

    
    chaine_apres_ajustee = supprimer_caracteres(chaine_apres_ajustee, nb_suppr)
    print("ICI : ")
    print(chaine_apres_ajustee)
    
    if chaine_apres_ajustee.startswith("}") : 
        chaine_a_inserer = "}" + chaine_a_inserer
        chaine_apres_ajustee = chaine_apres_ajustee[:-1]
    
    
    
    
    print("chaine_a_inserer : ")
    print(chaine_a_inserer)
    
    print("chaine_apres_ajustee apres traitement : ")
    print(chaine_apres_ajustee)
    
    if balise != "BD" : 
        
        liste = []
        for char in chaine_apres_ajustee : 
            if char != ">" : 
                liste.append(char)
            else : 
                liste.append(char)
                break

        if liste != [] and liste[-1] == ">" and "<" not in liste : 
            chaine_apres_ajustee = "<" + chaine_apres_ajustee
        
        '''liste = []
        for char in chaine_apres_ajustee : 
            if char == ">" : 
                break
            liste.append(char)
        if "<" not in liste : 
            chaine_apres_ajustee =  "<" + chaine_apres_ajustee'''
    
    print("Correction chaine_apres_ajustee : ")
    print(chaine_apres_ajustee)

    
    
    
    
    
    if balise == "AL" or balise == "AP" or balise == "AS" : 
        result = chaine_avant_ajustee + chaine_a_inserer + chaine_apres_ajustee
    elif balise == "BD" : 
        result = chaine_avant_ajustee + chaine_a_inserer + chaine_apres_ajustee[longueur_ajout::]
    elif balise == "IS" or balise == "IW" : 
        #result = chaine_avant_ajustee + chaine_a_inserer + chaine_apres_ajustee[0:len(chaine_apres_ajustee)-longueur_ajout]
        result = chaine_avant_ajustee + chaine_a_inserer + chaine_apres_ajustee
    else : 
        result = chaine_avant_ajustee + chaine_a_inserer + chaine_apres_ajustee

    return result








def process_deletions(text):
    result = list(text)
    i = 0

    while i < len(result):
        if result[i] == '⌫':
            # Si le caractère de suppression est trouvé, rechercher le caractère précédent
            j = i - 1
            while j >= 0 and result[j] == '~':
                j -= 1
            if j >= 0 and result[j] != '~':
                # Supprimer le caractère précédent s'il n'est pas un tilde
                result.pop(j)
                i -= 1  # Ajuster l'index après suppression
            # Remplacer le caractère de suppression par un tilde
            result[i] = '~'
        i += 1

    # Joindre la liste en une chaîne de caractères
    return ''.join(result)
