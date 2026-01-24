# 📐 RDM Poutres - Bibliothèque Python pour l'Analyse des Structures

Une bibliothèque Python complète pour l'analyse des poutres isostatiques en Résistance des Matériaux (RDM). Calcul des efforts internes, réactions d'appuis et tracé des diagrammes.

## 🚀 Fonctionnalités

### 📊 Types de Poutres Supportés

- ✅ **Poutres sur 2 appuis simples** - Isostatiques classiques
- ✅ **Poutres encastrées** - Consoles (encastrement à gauche ou droite)
- ✅ **Poutres avec appui simple + rouleau** - Avec porte-à-faux

### ⚖️ Types de Charges

- ✅ **Charges concentrées** - Forces verticales (positives vers le bas)
- ✅ **Charges réparties** - Uniformes sur un intervalle
- ✅ **Moments concentrés** - Couples (positifs anti-horaire)

### 📈 Calculs RDM

- ✅ **Réactions aux appuis** - Calcul automatique
- ✅ **Effort tranchant V(x)** - Diagramme complet
- ✅ **Moment fléchissant M(x)** - Diagramme avec extrema
- ✅ **Effort normal N(x)** - Pour extensions futures

### 🎨 Visualisation

- ✅ **Diagrammes professionnels** - Avec matplotlib
- ✅ **Poutre et charges** - Représentation graphique
- ✅ **Points particuliers** - Zéros et extrema identifiés
- ✅ **Export d'images** - PNG, PDF, JPG

### Prérequis

- Python 3.7 ou supérieur
- pip (gestionnaire de packages Python)

### Installation des Dépendances

```bash
pip install numpy matplotlib
```
