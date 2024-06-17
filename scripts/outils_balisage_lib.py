"""Ce script contient les fonctions qui sont utilisées dans le balisage des données."""



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
    while i < len(chaine) :
        if chaine[i] == '⌫' :
            if result :
                suppr_char.append(result.pop())
        else :
            if suppr_char:
                result.append('<ID>' + ''.join(suppr_char[::-1]) + '</ID>')
                suppr_char = []
            result.append(chaine[i])
        i += 1

    if suppr_char :
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



def extraire_sequence(chaine_speciale: str, chaine_sans_speciale: str) -> tuple[str, str] :
    """Aligne un texte contenant des caractères spéciaux avec une chaîne sans caractères spéciaux contenue dans ce texte

    Parameters
    ----------
    chaine_speciale : str
        chaîne contenant des caractères spéciaux
    chaine_sans_speciale : str
        chaine ne contenant pas de caractères spéciaux contenant chaine_speciale sans caractères spéciaux

    Returns
    -------
    tuple
        chaine avec caractères spéciaux avant et chaine avec caractères spéciaux après alignées
    """

    resultat = []
    reste = []
    index_sans_speciale = 0
    longueur_sans_speciale = len(chaine_sans_speciale)
    ignorer = False
    sequence_complete = False

    for char in chaine_speciale :
        if not sequence_complete :
            if index_sans_speciale < longueur_sans_speciale and char == chaine_sans_speciale[index_sans_speciale] :
                resultat.append(char)
                index_sans_speciale += 1
                if index_sans_speciale == longueur_sans_speciale :
                    sequence_complete = True
            elif char in "|~<>{}#⌫" :
                resultat.append(char)
                # Si on ajoute un caractère spécial à resultat, on vérifie si la séquence est complète
                if index_sans_speciale < longueur_sans_speciale and char == chaine_sans_speciale[index_sans_speciale] :
                    index_sans_speciale += 1
                    if index_sans_speciale == longueur_sans_speciale :
                        sequence_complete = True
            else :
                # Si on rencontre un caractère qui ne fait pas partie de la séquence sans caractères spéciaux,
                # on ajoute ce caractère à resultat mais on ne change pas sequence_complete.
                resultat.append(char)
        else :
            # On ajoute à reste tous les caractères restants de chaine_speciale.
            reste.append(char)

    return ''.join(resultat), ''.join(reste)



def process_deletions(text: str) -> str :
    """Reproduit le processus de supprissons en remplaçant les caractères supprimés par des tildes

    Parameters
    ----------
    text : str
        chaîne contenant des caractères de suppression et des caractères spéciaux

    Returns
    -------
    str
        chaine sans les caractères de suppression et avec caractères supprimés remplacés par des tildes
    """
    
    special_chars = {'|', '<', '>', '{', '}'}
    result = list(text)
    i = 0

    while i < len(result) :
        if result[i] == '⌫' :
            # Si le caractère de suppression est trouvé, rechercher le caractère précédent
            j = i - 1
            while j >= 0 and result[j] == '~' :
                j -= 1
            if j >= 0 and result[j] != '~' :
                if result[j] in special_chars and j > 0 :
                    # Si le caractère précédent est un caractère spécial, supprimer le caractère avant le spécial
                    result.pop(j - 1)
                    i -= 1  # Ajuster l'index après suppression
                else:
                    # Supprimer le caractère précédent s'il n'est pas un tilde ou un caractère spécial
                    result.pop(j)
                    i -= 1  # Ajuster l'index après suppression
            # Remplacer le caractère de suppression par un tilde
            result[i] = '~'
        i += 1

    # Joindre la liste en une chaîne de caractères
    return ''.join(result)



def nettoyer_texte(texte: str) -> str : 
    """Referme les balises des lettres uniques ajoutées

    Parameters
    ----------
    texte : str
        texte final avec unqiuement des chevrons ouvrants ("<")

    Returns
    -------
    str
        texte final où les lettres ajoutées sont suivies d'un chevrons fermant (">")
    """
    import re
    pattern = r"<~*."
    def replacer(match):
        return match.group() + ">"
    texte_modifie = re.sub(pattern, replacer, texte)
    texte_corrige = re.sub(r"<{>", "{", texte_modifie)
    return texte_corrige
