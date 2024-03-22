## 19/03/2024

Pour pouvoir etiquetter des mots incomplets, il nous faut d'abord voir dans auel contexte on trouve ces mots et si on peut se baser sur le pos du mot suivant ou precedant. IL nous faut donc identifier ce contexte en faisant un parsing des donnees du fichier csv planifications.

On cherche d'abord un etiquetteur qui ait l'etiquette "unknown" qu'il peut utiliser pour les mots incomplets

Les différents problemes :

- Stanza essaye de deviner les mots qu'ils comprend pas  exemple : "l'ois ch" pour l'oiseau chante était analysé l'oiseau cheval. Il donnait aussi le pos de nom s'il reconnait pas les mots

- Spacy se omporte comme Stanza,dans le sens qu'il devine le pos mais contrairement à Stanza il garde la lemme pareil que le mot qu'il ne reussit pas à identifier correctement.Par exemple "l'ois ch" est garde comme l'ois ch dans les lemmes, avec les pos nom.

- Seul TreeTigger semble mettre une étiquette unknown quand il ne reconnait pas un mot, mais cela n'arrive pas pour chaque mot inconnu. Donc on doit changer de strategie.

- NLTK ?

On s'est rendu compte donc du fait que tous les taggers utilisent des informations syntaxiques pour etiquetter les tokens. On a donc changé de strategie: on va utiliser le fichier final en format texte pour faire un lexique et si un mot n'est pas reconnu dans le lexique par exemple "p" l'ajouter dans une liste de mots non reconnu, cela permettra d'identifier nos différentes erreurs.

- En fonction des erreurs qu'on aura identifié il faudra faire une liste de regles et entrainer un modele pour garder nos erreurs et qu'il ne prédisent pas


## 22/03/2024

Notre objectif lors de cette séance est de créer un lexique à partir des fichiers finaux.

Les fichiers que nous avons obtenus auprès de Georgeta étaient au format docx. Nous avons donc cû convertir ces fichiers au format txt pour pouvoir ensuite récupérer leurs contenus textuels. Nous avons utilisé la librairie python pypandoc et itéré sur tous les fichiers du dossier Planification. Nous avons réussi à obtenir des fichiers txt correspondant.

L'étape suivante était d'écrire un second script dans lequel nous itérons sur chaque fichier txt obtenu précédemment, récupérons les mots contenus dans ces fichiers, et les stockons dans une variable de type set (afin d'éviter les doublons).
