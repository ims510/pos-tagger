# Analyse de données d'écriture en temps réel

## Introduction

Ce dépôt git a pour but de présenter 2 outils pour l'analyse automatique de données d'écriture en temps réel :

1. un POS-tagger
2. un chunker

L'objectif de ces deux outils est de pouvoir analyser les comportements des personnes qui tapent sur un clavier.


## POS-tagger

L'outil que nous avons développé pour réaliser la tâche d'annotation en parties du discours des erreurs est le script `pos_tagger.py`, et s'appuie sur deux modules d'annotation, à savoir Spacy et Treetagger.

Commande pour lancer l'outil :
```sh
python3 pos_tagger.py -i chemin/vers/le/fichier_csv_contenant_les_donnees -o chemin/vers/le/fichier_csv_de_resultats
```

Exemple de lancement :
```sh
python3 pos_tagger.py -i ../data/CLEAN_csv_planification.tsv -o ../data/annotation_erreurs_treetagger.csv
```

Le fichier de sortie est un csv contenant tous les tokens erronés avec leurs informations (type d'erreur, pos, lemme, longueuer de la modification...) ainsi que toutes les informations de la ligne dans laquelle ils ont été produits.
