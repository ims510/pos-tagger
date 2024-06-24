'''Ce script permet de transformer des fichiers txt contenant des textes annotés en fichiers html avec des couleurs pour mieux visualiser les annotations.'''



import os



def surligner_texte(content: str) -> str :
    """Surligne le texte en ajoutant des balises HTML avec des styles CSS pour visualiser les annotations.

    Parameters
    ----------
    content : str
        contenu du fichier texte à surligner

    Returns
    -------
    str
        contenu avec les balises HTML ajoutées pour le surlignement
    """

    # Initialiser une variable pour stocker le texte surligné
    highlighted_content = ""

    # Initialiser un itérateur sur le texte
    i = 0

    # On itère sur chaque caractère du texte
    while i < len(content) :

        # Caractères déclanchant l'application d'un style :
        # 1. Accolade ouvrante
        # 2. Chevron ouvrant
        # 3. Pipe
        # 4. Tilde

        # 1. Si le caractère est une accolade ouvrante :
        if content[i] == '{' :
            start = i
            i += 1
            tilde_only = True
            temp_content = '{'

            # Tant qu'on ne rencontre pas d'accolade fermante, on continue d'itérer :
            while i < len(content) and content[i] != '}' :

                # On met les tildes en rouge et gras
                if content[i] == '~' :
                    temp_content += '<span style="color: red; font-weight: bold;">~</span>'

                # Si on rencontre un chevron ouvrant :
                elif content[i] == '<' :

                    # On surligne en vert
                    temp_content += '<span style="background-color: lightgreen;">&lt;'
                    i += 1

                    # Tant qu'on ne rencontre pas de chevron fermant :
                    while i < len(content) and content[i] != '>' :

                        # On met les tildes en rouge et gras
                        if content[i] == '~' :
                            temp_content += '<span style="color: red; font-weight: bold;">~</span>'

                        # On met les pipes en gras et on les surligne en jaune
                        elif content[i] == '|' :
                            temp_content += '<span style="font-weight: bold; color: black; background-color: yellow;">|</span>'

                        else:
                            temp_content += content[i]

                        i += 1

                    # Si on rencontre un chevron fermant, on l'ajoute au contenu et on ferme la balise
                    if i < len(content) and content[i] == '>' :
                        i += 1
                        temp_content += '&gt;'
                    temp_content += '</span>'

                # Si on rencontre un pipe :
                elif content[i] == '|' :

                    # On le met en gras et on le surligne en jaune
                    temp_content += '<span style="font-weight: bold; color: black; background-color: yellow;">|</span>'
                    tilde_only = False

                # Sinon on continue d'itérer
                else :
                    temp_content += content[i]
                    if content[i] not in {'~', '|', '<', '>'}:
                        tilde_only = False
                i += 1

            # Si on rencontre une accolade fermante, on l'ajoute au contenu
            if i < len(content) and content[i] == '}' :
                temp_content += '}'
                i += 1
            
            # Si la séquence entre accolades ne contient que des tildes :
            if tilde_only :

                # On la surligne en rouge
                highlighted_content += f'<span style="background-color: lightcoral;">{temp_content}</span>'

            # Sinon :
            else :

                # On la surligne en bleu
                highlighted_content += f'<span style="background-color: lightblue;">{temp_content}</span>'

        # 2. Sinon si le caractère est un chevron ouvrant :
        elif content[i] == '<' :

            # On surligne en vert
            highlighted_content += '<span style="background-color: lightgreen;">&lt;'
            i += 1

            # Tant qu'on ne rencontre pas de chevron fermant :
            while i < len(content) and content[i] != '>' :

                # Si on rencontre un tilde :
                if content[i] == '~' :

                    # On le met en gras et en rouge
                    highlighted_content += '<span style="color: red; font-weight: bold;">~</span>'

                # Sinon si le caractère est un pipe :
                elif content[i] == '|' :

                    # On le met en gras et on le surligne en jaune
                    highlighted_content += '<span style="font-weight: bold; color: black; background-color: yellow;">|</span>'

                # Sinon, on ne touche pas au style
                else :
                    highlighted_content += content[i]
                i += 1

            # Si on rencontre un chevron fermant, on ferme la balise
            if i < len(content) and content[i] == '>' :
                i += 1
                highlighted_content += '&gt;'
            highlighted_content += '</span>'

        # 3. Sinon si le caractère est un pipe :
        elif content[i] == '|' :

            # On le met en gras et on le surligne en jaune
            highlighted_content += '<span style="font-weight: bold; color: black; background-color: yellow;">|</span>'
            i += 1

        # 4. Sinon si le caractère est un tilde :
        elif content[i] == '~' :

            # On le met en gras et en rouge
            highlighted_content += '<span style="color: red; font-weight: bold;">~</span>'
            i += 1

        # Sinon (si le caractère est un caractère "normal"), on n'applique pas de style
        else :
            highlighted_content += content[i].replace('<', '&lt;').replace('>', '&gt;')
            i += 1

    return highlighted_content



def traiter_fichiers(dossier_source: str, dossier_sortie: str) -> None :
    """Traite tous les fichiers texte dans le dossier source, applique le surlignement et enregistre les résultats en tant que fichiers HTML dans le dossier de sortie.

    Parameters
    ----------
    dossier_source : str
        chemin du dossier contenant les fichiers texte à traiter
    dossier_sortie: str
        chemin du dossier où enregistrer les fichiers HTML surlignés

    Returns
    -------
    None
    """

    # Créer le dossier de sortie s'il n'existe pas
    if not os.path.exists(dossier_sortie):
        os.makedirs(dossier_sortie)

    # Parcourir tous les fichiers dans le dossier source
    for nom_fichier in os.listdir(dossier_source):
        chemin_complet = os.path.join(dossier_source, nom_fichier)
        if os.path.isfile(chemin_complet) and nom_fichier.endswith('.txt'):
            # Lire le contenu du fichier texte
            with open(chemin_complet, 'r', encoding='utf-8') as fichier:
                contenu = fichier.read()
            
            # Appliquer le surlignement
            contenu_surligne = surligner_texte(contenu)
            
            # Créer le contenu HTML final avec style
            contenu_html = f'''
                <html>
                <head>
                    <style>
                        body {{
                            font-family: sans-serif;
                        }}
                        span {{
                            font-family: sans-serif;
                        }}
                    </style>
                </head>
                <body>{contenu_surligne}</body>
                </html>
            '''
            
            # Définir le chemin de sortie
            chemin_sortie = os.path.join(dossier_sortie, nom_fichier.replace('.txt', '.html'))
            
            # Enregistrer le contenu dans un nouveau fichier HTML
            with open(chemin_sortie, 'w', encoding='utf-8') as fichier_sortie:
                fichier_sortie.write(contenu_html)

    print(f'Tous les fichiers ont été traités et enregistrés dans {dossier_sortie}.')



dossier_source = input('Nom du dossier contenant les textes reconstruits : ')
dossier_sortie = 'Textes_reconstruits_visualisation'
traiter_fichiers(dossier_source, dossier_sortie)
