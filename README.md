# Vendée Globe 2024

Ce projet propose des scripts Python permettant de construire des données géographiques à partir des pointages du Vendée Globe 2024, fournis toutes les 4 heures sur le [site officiel](https://www.vendeeglobe.org/classement) de la compétition.

Cela vous permet, par exemple, de visualiser les dernières positions dans votre SIG préféré : [QGIS](https://qgis.org/).

![qgis](img/qgis.png)

## Environnement virtuel

Il est vivement conseillé d'installer les dépendances dans un environnement virtuel (venv).

```bash
python -m venv .venv 
source .venv/bin/activate
pip install -r requirements.txt
```

## Obtenir le dernier pointage en date au format GPKG

```bash
python get_last_ranking.py --output-dir <chemin_du_répertoire>
```

### Arguments

- `--output-dir` : (optionnel) Spécifie le répertoire dans lequel le fichier GPKG sera sauvegardé. Si cet argument est omis, le fichier sera exporté dans le répertoire courant (`./`).

### Exemple 

```bash
python get_last_ranking.py --output-dir ./data_output/
```

## Télécharger l'historique de tous les pointages

WIP (Work In Progress) : cette fonctionnalité est en cours de développement. Plus d'informations seront fournies une fois terminée.

## Pour aller encore plus loin

Ce projet est actuellement un proof of concept (PoC). À l'avenir, on pourrait envisager : 

- De diffuser les pointages via une API
- Pouvoir charger directement les pointages depuis un plugin QGIS