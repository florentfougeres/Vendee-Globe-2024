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
python dernier_pointage.py --output-dir ./data_output/
```

## Télécharger l'historique de tous les pointages

```bash
python trajectoires_pointages.py --output-dir ./data_output/
```


## Pour aller encore plus loin

Ce projet est actuellement un proof of concept (PoC). À l'avenir, on pourrait envisager : 

- De diffuser les pointages via une API
- Pouvoir charger directement les pointages depuis un plugin QGIS