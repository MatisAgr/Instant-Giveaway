# Instant-Giveaway
Tisma : [![wakatime](https://wakatime.com/badge/user/a16f794f-b91d-4818-8dfc-d768ce605ece/project/c7ba3a6d-1d1d-42c2-ab13-09c6b41c0649.svg)](https://wakatime.com/badge/user/a16f794f-b91d-4818-8dfc-d768ce605ece/project/c7ba3a6d-1d1d-42c2-ab13-09c6b41c0649)

Une application desktop pour automatiser la participation et la vérification des giveaways sur Instant Gaming, vous permettant d'économiser du temps et de maximiser vos chances de gagner.

> [!CAUTION]
> **Cette application peut violer les [conditions d'utilisation d'Instant Gaming](https://www.instant-gaming.com/en/terms-of-use/).**
> **Je ne suis PAS responsable si votre compte Instant Gaming est suspendu ou banni suite à l'utilisation de cet outil.**
> **L'utilisation d'outils d'automatisation peut être considérée comme un abus et entraîner des sanctions sur votre compte.**

<h3> Aperçu : </h3>

![image](https://github.com/user-attachments/assets/preview-image)

---

## Table des matières
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Fonctionnalités](#fonctionnalités)
- [Structure du projet](#structure-du-projet)
- [Dépendances](#dépendances)
- [Technologies utilisées](#technologies-utilisées)

## Prérequis

Avant de commencer, assurez-vous d'avoir installé :
- [Python 3.8](https://www.python.org/downloads/) ou supérieur
- [Google Chrome](https://www.google.com/chrome/) (dernière version recommandée)
- Un compte Instant Gaming valide

## Installation

1. Clonez le dépôt :
```sh
git clone https://github.com/MatisAgr/Instant-Giveaway.git
```

2. Accédez au dossier du projet :
```sh
cd Instant-Giveaway
```

3. Installez les dépendances :
```sh
pip install -r requirements.txt
```


## Configuration

Dans l'onglet "Paramètres" de l'application, vous pouvez configurer :

- **Navigateur** : Chemin vers l'exécutable Chrome
- **Délais** : Temps d'attente entre les actions (coming soon)
- **Mode invisible** : Exécution de Chrome en arrière-plan
- **Détection du nom d'utilisateur** : Automatique ou manuel
- **Options avancées** :
  - Téléchargement automatique du driver Chrome
  - Fermeture automatique des onglets
  - Nombre de tentatives en cas d'échec

## Utilisation

1. Lancez l'application (soyez connecté au préalable sur votre navigateur):
```sh
python main.py
```

2. **Gestion des liens** :
- Ajoutez manuellement des liens de giveaway
- Importez une liste de liens au format JSON
- Vérifiez l'état des liens (actifs/morts)

3. **Participation aux giveaways** :
- Sélectionnez l'onglet "Participation"
- Cliquez sur "Démarrer" pour participer automatiquement à tous les giveaways
- L'application parcourt chaque lien et participe si possible

4. **Vérification des gains** :
- Dans l'onglet "Vérification"
- Lancez la vérification pour voir si vous avez gagné des giveaways
- Les résultats s'affichent dans l'interface

## Fonctionnalités

- **Participation automatique** : Visite chaque lien et participe aux giveaways
- **Vérification des gains** : Vérifie si vous avez gagné des giveaways terminés
- **Gestion des liens** : Interface pour ajouter, modifier, supprimer et vérifier les liens
- **Mode invisible** : Exécution en arrière-plan sans afficher le navigateur
- **Collecte de points bonus** : Récupération automatique des points bonus disponibles
- **Interface intuitive** : Organisation en onglets pour une expérience utilisateur fluide

## Dépendances

Ce projet utilise les bibliothèques suivantes :
- `PyQt6` : Pour l'interface graphique
- `selenium` : Pour l'automatisation du navigateur
- `psutil` : Pour la gestion des processus
- `requests` : Pour les requêtes HTTP
- `beautifulsoup4` : Pour l'analyse HTML


#### Remarque

Une version console plus ancienne du projet est disponible dans le dossier `OLD`. 
Cette version a été développée par [Mothix](https://github.com/MothixExe) ❤️ et contient les fonctionnalités de base pour la participation et la vérification des giveaways via une interface en ligne de commande.

Les scripts originaux comprennent :
- `participer.py` : Pour participer aux giveaways
- `verif.py` : Pour vérifier les giveaways gagnés
- `versionjs.py` : Alternative utilisant l'injection JavaScript

Cette version peut être utile pour les utilisateurs préférant une interface en ligne de commande ou souhaitant comprendre le fonctionnement de base du programme. (Cette version étant ancienne ne dispose pas des patchs de bug et des nouvelles fonctionnalités)