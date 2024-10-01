# pos-tagger
L'objectif principal du projet consiste à étudier les schémas et les comportements des individus lorsqu'ils tapent du texte sur un clavier. Il vise à répondre à des interrogations telles que : qu'est-ce qui entraîne une pause chez une personne pendant qu'elle tape ? Est-ce une partie spéci que du discours (verbe, nom, pronom), une position particulière dans une phrase (début de syntagme,  n de syntagme), ou des mots particuliers qui posent constamment problème ?

Dans cette perspective, une expérience a été menée sur plusieurs participants, qu'ils soient experts ou non dans un domaine. On leur a demandé de saisir un extrait de texte, et leurs frappes de clavier ont été enregistrées à l'aide d'un logiciel spécialisé conservant des informations comme la position du curseur, les retours en arrière, les corrections, le temps de pause entre deux saisies, etc.

Le résultat obtenu était un document XML contenant ces informations pour chaque touche pressée, qu'il s'agisse d'une lettre, d'une suppression, d'un espace, etc. Ces données ont ensuite été prétraitées a n d’obtenir des  chiers csv contenant ces informations, où chaque ligne correspond à la production entre deux intervalles de pauses. Notre rôle dans ce projet est de proposer un étiqueteur en parties du discours adapté à ces données de nature particulière.

