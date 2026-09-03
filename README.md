# Outil de Scraping de Prospects Médicaux (Google Maps)

Ce projet contient un outil de scraping en ligne de commande développé en Python. Il utilise `Playwright` pour extraire des prospects médicaux depuis Google Maps.

L'outil demande une spécialité médicale et une localisation, puis effectue une recherche, extrait les informations pour chaque cabinet (nom, note, nombre d'avis, numéro de téléphone, site web), et tente d'extraire une adresse e-mail depuis les sites web. Les résultats sont triés par note (de la meilleure à la pire) et exportés dans un fichier CSV.

## Prérequis

- Python 3.7+
- pip (gestionnaire de paquets Python)

## Installation

1. **Cloner ou télécharger le dépôt.**

2. **Installer les dépendances requises :**
   ```bash
   pip install -r requirements.txt
   ```

3. **Installer les navigateurs pour Playwright :**
   ```bash
   playwright install
   ```

## Utilisation

L'outil peut être exécuté en ligne de commande de deux manières :

### 1. Avec des arguments en ligne de commande
```bash
python scraper.py --specialty "ophtalmologue" --location "Marseille"
```

### 2. Mode interactif
Si vous exécutez le script sans arguments, il vous demandera de saisir la spécialité et la localisation :
```bash
python scraper.py
```
*(Vous serez invité à entrer la spécialité et la localisation.)*

## Résultat attendu

Le script va générer un fichier CSV dans le répertoire courant avec un nom tel que `leads_ophtalmologue_marseille.csv` contenant :
- Nom du médecin / cabinet
- Note moyenne
- Nombre d'avis
- Numéro de téléphone
- URL du site web
- Adresse e-mail (si trouvée)

## Avertissement
Assurez-vous de respecter les conditions d'utilisation de Google Maps et des sites web visités lors du scraping de ces données.
