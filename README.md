# Instant-Giveaway
Bot Instant Gaming

Tisma : [![wakatime](https://wakatime.com/badge/user/a16f794f-b91d-4818-8dfc-d768ce605ece/project/c7ba3a6d-1d1d-42c2-ab13-09c6b41c0649.svg)](https://wakatime.com/badge/user/a16f794f-b91d-4818-8dfc-d768ce605ece/project/c7ba3a6d-1d1d-42c2-ab13-09c6b41c0649)

# Instant-Giveaway
## Instant Gaming Giveaway Utilimate Tool
Une application desktop pour automatiser la participation et la vérification des giveaways sur Instant Gaming.
 

## Fonctionnalités

- Participation automatique aux giveaways Instant Gaming
- Vérification des giveaways gagnés 
- Gestion des liens de giveaway avec vérification de leur état (actif, mort, etc.)
- Interface utilisateur intuitive avec onglets dédiés aux différentes fonctions
- Mode invisible permettant d'exécuter Chrome en arrière-plan
- Détection automatique du nom d'utilisateur ou configuration manuelle

## Installation

### Prérequis

- Python 3.8 ou supérieur
- Un navigateur Chrome installé
- Un compte Instant Gaming

### Installation des dépendances

pip install -r requirements.txt

Les dépendances principales sont :
- PyQt6
- selenium
- psutil
- requests
- beautifulsoup4

## Utilisation

1. Lancez l'application avec :
   python main.py

2. Configurez vos paramètres dans l'onglet "Paramètres"
3. Ajoutez des liens de giveaway dans l'onglet "Gestion des liens"
4. Participez aux giveaways avec l'onglet "Participation"
5. Vérifiez vos gains avec l'onglet "Vérification"

### Gestion des liens

Vous pouvez ajouter des liens manuellement ou importer/exporter une liste de liens au format JSON. Le format standard est :
https://www.instant-gaming.com/XX/giveaway/INFLUENCER

## Configuration

Dans l'onglet "Paramètres", vous pouvez configurer :

- Le chemin vers Chrome
- Le délai d'attente entre les actions
- Le téléchargement automatique du driver Chrome
- La fermeture automatique des onglets
- Le nombre de tentatives en cas d'échec
- Le mode invisible (headless)
- La détection automatique du nom d'utilisateur

## Fonctionnement

L'application utilise Selenium pour automatiser les interactions avec le navigateur Chrome. Elle s'appuie sur votre profil Chrome existant pour éviter d'avoir à vous authentifier à chaque utilisation.

Pour les giveaways, l'application :
1. Visite chaque lien de giveaway
2. Vérifie s'il est possible de participer
3. Clique sur le bouton de participation
4. Collecte les points bonus si disponibles

Pour la vérification des gains, l'application :
1. Visite chaque lien de giveaway
2. Vérifie si le giveaway est terminé avec un gagnant
3. Compare le nom du gagnant avec votre nom d'utilisateur
4. Affiche les giveaways que vous avez gagnés

## Structure du projet

Instant-Giveaway/
│
├── main.py                 # Point d'entrée de l'application
├── requirements.txt        # Dépendances Python
│
├── src/                    # Code source
│   ├── controllers/        # Contrôleurs pour la logique métier
│   ├── models/             # Modèles de données
│   ├── utils/              # Utilitaires divers
│   └── views/              # Interfaces utilisateur
│
└── resources/              # Ressources de l'application
    ├── config/             # Fichiers de configuration
    ├── data/               # Données (liens, etc.)
    └── img/                # Images et icônes

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à proposer une pull request.

## Licence

Ce projet est sous licence open source.

## Remarques

Cette application est développée à des fins éducatives. L'utilisation abusive pourrait enfreindre les conditions d'utilisation d'Instant Gaming.