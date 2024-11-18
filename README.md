
# 🌍 Vendée Globe 2024 ⛵

Ce projet propose des **scripts Python** permettant de construire des données géographiques à partir des pointages du **Vendée Globe 2024**, fournis toutes les 4 heures sur le [site officiel](https://www.vendeeglobe.org/classement) de la compétition. 

Grâce à ce projet, vous pouvez visualiser les **dernières positions des skippers** dans votre SIG préféré comme [QGIS](https://qgis.org/). 🗺️

![qgis](img/qgis.png)

## 🛠️ Environnement Virtuel

Pour installer les dépendances dans un environnement virtuel (venv), voici la procédure recommandée :

```bash
python -m venv .venv
source .venv/bin/activate   # Sur Windows, utilisez `.venv\Scriptsctivate`
pip install -r requirements.txt
```

Cela vous permettra de garder votre environnement propre et de gérer facilement les bibliothèques nécessaires au projet. 🌱

## 📡 Obtenir le Dernier Pointage en Date au Format GPKG

Pour récupérer le **dernier pointage** et le sauvegarder en **GPKG**, utilisez la commande suivante :

```bash
python dernier_pointage.py --output-dir ./data_output/
```

Cela vous permettra d'avoir le dernier pointage mis à jour dans votre répertoire de sortie. 📍

## 📜 Télécharger l'Historique Complet des Pointages

Si vous souhaitez télécharger **tous les pointages historiques**, exécutez :

```bash
python trajectoires_pointages.py --output-dir ./data_output/
```

Cela vous fournira un fichier contenant l'ensemble des trajets et positions des skippers. 🛳️

## 📅 Release Journalière

Chaque jour à **7h30**, un processus **CI/CD** exécute le script `trajectoires_pointages.py` et met à jour le fichier **Geopackage** dans la section des [Latest Daily Release](https://github.com/florentfgrs/Vendee-Globe-2024/releases/tag/latest).

Vous pouvez toujours télécharger la dernière version du fichier en cliquant sur le lien suivant : [Derniers Données du Jour](https://github.com/florentfgrs/Vendee-Globe-2024/releases/download/latest/latest_data.gpkg) 🚀

## 🔮 Pour Aller Plus Loin

Ce projet est actuellement un **proof of concept (PoC)**. À l'avenir, plusieurs améliorations sont envisagées :

- 🚀 **Diffusion des pointages via une API**
- 🧭 **Chargement direct des pointages depuis un plugin QGIS**

**N'hésitez pas à contribuer ou à proposer des améliorations !** 🤝
