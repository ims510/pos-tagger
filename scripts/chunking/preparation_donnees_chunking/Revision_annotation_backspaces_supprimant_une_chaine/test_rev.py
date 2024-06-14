#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 15:39:37 2024

@author: amandine
"""


chaine_1 = "p>ose des problèmes"
chaine_2 = "pose des problèmes"
chaine_3 = "po<s>e des problèmes"


liste_1 = []
for char in chaine_1 : 
    if char != ">" : 
        liste_1.append(char)
    else : 
        liste_1.append(char)
        break

if liste_1[-1] == ">" and "<" not in liste_1 : 
    chaine_1 = "<" + chaine_1

liste_2 = []
for char in chaine_2 : 
    if char != ">" : 
        liste_2.append(char)
    else : 
        liste_2.append(char)
        break

if liste_2[-1] == ">" and "<" not in liste_2 : 
    chaine_2 = "<" + chaine_2

liste_3 = []
for char in chaine_3 : 
    if char != ">" : 
        liste_3.append(char)
    else : 
        liste_3.append(char)
        break

if liste_3[-1] == ">" and "<" not in liste_3 : 
    chaine_3 = "<" + chaine_3














chaine_avec_spe = "Dans le cadre de la médecine traditionnelle, |nous voici face à un dillemme. |Beaucoup critiqué cette dernière s'avère parfois en~ effet fort efficace sur certain<~~s> points~~. |En effet si l'ont y réfléchie plus longuement beaucoup de nos méthodes actuelles se sont basé sur les fond<s> de cette méd|~ecine alternative{~~ du aux croyance et autre connaissances antètieures~~ et même si elle est dépassé sur certains cas de maladie à l'heure actu}{elle}| certain~s remède<s> sont enc~ore utilisés |à nos jours|. | |~~~De plus nous pouvons ~~~souligner le fait que la médecine alternative |n'utilise~~~ pas que les croyances{ au final}|, |les remèdes naturel##s sont en effe|~~~~~~~~~~t éno~rmément mi<~t> en avant contrairement à la médecine actuelle qui mêm~e si elle s'avère efficace ut~~~~~~~~~~ilise pour la plupart du~ temps des médicament~s plus ou moins chimi~~~~~~que pouvant parfois être plus nocif que la maladie en elle-même{ et pouvant créer }{d'autre problème~s mé~di~~~caux{ plus ou moins grave} chez le plus patient}. |Cependant, si nous devons faire une comparaison entre ces |deux méthodes médicales, il s'avère être vrai que la médecine alternative{ peut}{ malgré tout} pos<~é> beaucoup de problème |s{ et erreurs médi}{cal}< > |à nos jours|, en ~effet une partie de cette médecine <~s>e basant {~~~sur les} ancienne<s> croyances, les erreurs médicale<s> de diag|~nostic <~s>e font ~beaucoup plus |qu'en médecine moderne{ du }{a un manque de connaissance}{ pour les ~'nouvelles' maladie}<s>|~ et malheureusement dans certains cas des erreurs ~~~~~~~comme cell~~~~~~~~es-ci peuvent parfois être fatale{ pour~ le patient}. |La médecine alternative pose aussi problème dans le sens où elle ne progresse pas contrairement à la medecine moderne, cette dernière dispose des dernières technologi~~e|~~~~, connaissance et |recherches afin de découvrir de nouvelles maladie~s pathogène mais aussi afin de trouver un antidote co~~~~~ntre ces derniers. |M~~alheureuseme~nt en médecine, il est important |de bien conna~ître la mal~~~~adie afin de la soignée| et ce n'est pas toujours le cas de la médecine alternative même si cette~~ dernière dispose |aussi de remède pouvant être plus ~~~~efficace qu'en médecine moderne.| "
chaine_sans_spe = "Dans le cadre de la médecine traditionnelle, nous voici face à un dillemme. Beaucoup critiqué cette dernière s'avère parfois en effet fort efficace sur certains points. En effet si l'ont y réfléchie plus longuement beaucoup de nos méthodes actuelles se sont basé sur les fonds de cette médecine alternative du aux croyance et autre connaissances antètieures et même si elle est dépassé sur certains cas de maladie à l'heure actuelle certains remèdes sont encore utilisés à nos jours.  De plus nous pouvons souligner le fait que la médecine alternative n'utilise pas que les croyances au final, les remèdes naturels sont en effet énormément mit en avant contrairement à la médecine actuelle qui même si elle s'avère efficace utilise pour la plupart du temps des médicaments plus ou moins chimique pouvant parfois être plus nocif que la maladie en elle-même et pouvant créer d'autre problèmes médicaux plus ou moins grave chez le plus patient. Cependant, si nous devons faire une comparaison entre ces deux méthodes médicales, il s'avère être vrai que la médecine alternative peut malgré tout posé beaucoup de problèmes et erreurs médical  à nos jours, en effet une partie de cette médecine se basant sur les anciennes croyances, les erreurs médicales de diagnostic se font beaucoup plus qu'en médecine moderne du a un manque de connaissance pour les 'nouvelles' maladies et malheureusement dans certains cas des erreurs comme celles-ci peuvent parfois être fatale pour le patient. La médecine alternative pose aussi problème dans le sens où elle ne progresse pas contrairement à la medecine moderne, cette dernière dispose des dernières technologie, connaissance et recherches afin de découvrir de nouvelles maladies pathogène mais aussi afin de trouver un antidote contre ces derniers. Malheureusement en médecine, il est important de bien connaître la maladie afin de la soignée et ce n'est pas toujours le cas de la médecine alternative même si cette dernière dispose aussi de remède pouvant être plus efficace qu'en médecine moderne.  "

chaine_avec_spe_nettoyee = chaine_avec_spe.replace("|", "").replace("~", "").replace("<", "").replace(">", "").replace("{", "").replace("}", "").replace("#", "")


'''print(chaine_sans_spe)
print()
print(chaine_avec_spe_nettoyee)'''



def comparer_chaines(chaine1, chaine2):
    longueur_min = min(len(chaine1), len(chaine2))
    
    # Parcourir les deux chaînes jusqu'à la longueur de la plus courte
    for i in range(longueur_min):
        if chaine1[i] != chaine2[i]:
            chaine1_diff = chaine1[:i+1]
            chaine2_diff = chaine2[:i+1]
            return (f"Différence trouvée à la position {i}: '{chaine1[i]}' != '{chaine2[i]}'",
                    chaine1_diff, chaine2_diff)
    
    # Vérifier si les chaînes sont de longueurs différentes
    if len(chaine1) != len(chaine2):
        chaine1_diff = chaine1[:longueur_min+1] if longueur_min < len(chaine1) else chaine1
        chaine2_diff = chaine2[:longueur_min+1] if longueur_min < len(chaine2) else chaine2
        return (f"Les chaînes ont des longueurs différentes. La différence commence à la position {longueur_min}",
                chaine1_diff, chaine2_diff)
    
    return ("Les chaînes sont identiques", chaine1, chaine2)


#print(comparer_chaines(chaine_sans_spe, chaine_avec_spe_nettoyee))






texte = "Dans le cadre de la médecine traditionnelle, |nous voici face à un dillemme. |Beaucoup critiqué cette dernière s'avère parfois ene⌫ effet fort efficace sur certaines<⌫⌫s> points, ⌫⌫. |En effet si l'ont y réfléchie plus longuement beaucoup de nos méthodes actuelles se sont basé sur les fond<s> de cette médi|⌫ecine alternative|,< >{⌫⌫ du aux croyance et autre connaissances antètieures, ⌫⌫ et même si elle est dépassé sur certains cas de maladie à l'heure actu}{elle} certaine⌫s remède<s> sont encà⌫ore utilisés |à nos jours|.< > |L'u⌫⌫⌫De plus nous pouvons com⌫⌫⌫souligner le fait que la médecine alternative |n'utilisepas⌫⌫⌫ pas que les croyances{ au final}|, |les remèdes naturelle⌫⌫s sont en effet| beaucoup⌫⌫⌫⌫⌫⌫⌫⌫⌫⌫t énom⌫rmément mis<⌫t> en avant contrairement à la médecine actuelle qui mêms⌫e"


def process_deletions(text):
    special_chars = {'|', '<', '>', '{', '}'}
    result = list(text)
    i = 0

    while i < len(result):
        if result[i] == '⌫':
            # Si le caractère de suppression est trouvé, rechercher le caractère précédent
            j = i - 1
            while j >= 0 and result[j] == '~':
                j -= 1
            if j >= 0 and result[j] != '~':
                if result[j] in special_chars and j > 0:
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



texte_nettoye = process_deletions(texte)
print(texte_nettoye)



