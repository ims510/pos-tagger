'''Ce script permet de transformer des fichiers txt contenant des textes annotés en fichiers html avec des couleurs pour mieux visualiser les annotations.'''



import os

def surligner_texte(content):
    highlighted_content = ""
    i = 0
    while i < len(content):
        if content[i] == '{':
            start = i
            i += 1
            tilde_only = True
            temp_content = '{'
            while i < len(content) and content[i] != '}':
                if content[i] == '~':
                    temp_content += '<span style="color: red; font-weight: bold;">~</span>'
                elif content[i] == '<':
                    temp_content += '<span style="background-color: lightgreen;">&lt;'
                    i += 1
                    while i < len(content) and content[i] != '>':
                        if content[i] == '~':
                            temp_content += '<span style="color: red; font-weight: bold;">~</span>'
                        elif content[i] == '|':
                            temp_content += '<span style="font-weight: bold; color: black; background-color: yellow;">|</span>'
                        else:
                            temp_content += content[i]
                        i += 1
                    if i < len(content) and content[i] == '>':
                        i += 1
                        temp_content += '&gt;'
                    temp_content += '</span>'
                elif content[i] == '|':
                    temp_content += '<span style="font-weight: bold; color: black; background-color: yellow;">|</span>'
                    tilde_only = False
                else:
                    temp_content += content[i]
                    if content[i] not in {'~', '|', '<', '>'}:
                        tilde_only = False
                i += 1
            if i < len(content) and content[i] == '}':
                temp_content += '}'
                i += 1
            
            if tilde_only:
                highlighted_content += f'<span style="background-color: lightcoral;">{temp_content}</span>'
            else:
                highlighted_content += f'<span style="background-color: lightblue;">{temp_content}</span>'
        elif content[i] == '<':
            highlighted_content += '<span style="background-color: lightgreen;">&lt;'
            i += 1
            while i < len(content) and content[i] != '>':
                if content[i] == '~':
                    highlighted_content += '<span style="color: red; font-weight: bold;">~</span>'
                elif content[i] == '|':
                    highlighted_content += '<span style="font-weight: bold; color: black; background-color: yellow;">|</span>'
                else:
                    highlighted_content += content[i]
                i += 1
            if i < len(content) and content[i] == '>':
                i += 1
                highlighted_content += '&gt;'
            highlighted_content += '</span>'
        elif content[i] == '|':
            highlighted_content += '<span style="font-weight: bold; color: black; background-color: yellow;">|</span>'
            i += 1
        elif content[i] == '~':
            highlighted_content += '<span style="color: red; font-weight: bold;">~</span>'
            i += 1
        else:
            highlighted_content += content[i].replace('<', '&lt;').replace('>', '&gt;')
            i += 1
    return highlighted_content

def traiter_fichiers(dossier_source, dossier_sortie):
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
