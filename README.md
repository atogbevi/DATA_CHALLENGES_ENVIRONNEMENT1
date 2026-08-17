# Diagnostic de l'accès à l'eau potable au Togo

Dashboard Streamlit réalisé dans le cadre du **Data Challenges · Défi Environnement1**.

Il croise les infrastructures hydrauliques, la démographie et le risque d'inondation pour produire un diagnostic territorial et des pistes de priorisation.

Réalisé par **Angelica TOGBEVI**.

## Objectif

Aider à lire, sur un même support :

- où se trouvent les ouvrages d'eau potable cartographiables ;
- quels sites n'ont pas de plan d'entretien ;
- où la pression démographique sur les points d'eau est la plus forte ;
- quels ouvrages sont exposés au risque d'inondation (FRI) ;
- quels cantons ressortent en priorité lorsque ces trois signaux sont combinés.

L'application **n'effectue aucun calcul métier**. Elle affiche des fichiers déjà produits par un pipeline de traitement en amont (`dashboard_data/`).

## Sources

| Source | Périmètre | Contenu |
| --- | --- | --- |
| **COSO** | Nord-Togo | 218 microprojets ; 86 ont une géométrie exploitable |
| **TdE** | Grand Lomé | 67 châteaux d'eau / forages, tous cartographiables |

Les indicateurs d'inondation s'appuient sur le **FRI** (Flood Risk Index), disponible à deux échelles : canton (388 cantons) et grille 1 km extraite au point de chaque ouvrage.

## Pages

1. **Accueil** — chiffres clés et limites méthodologiques.
2. **Cartographie** — fond FRI par canton + points COSO / TdE.
3. **Maintenance** — taux de sites sans plan d'entretien (COSO uniquement) et avancement des travaux.
4. **Démographie** — pression (habitants par ouvrage), avec deux échelles distinctes : recensement 2010 (région) et population modélisée (canton).
5. **Risque d'inondation** — FRI exact de chaque point (grille 1 km), pas la moyenne du canton.
6. **Synthèse** — score de priorisation = moyenne simple de trois indicateurs normalisés (maintenance, FRI, habitants par ouvrage).

## Limites

- Aucune donnée de panne ou d'abandon réel : le « risque de maintenance » est un **proxy** (existence d'un plan d'entretien), pas un taux de fonctionnalité.
- Couverture géographique partielle : COSO au Nord, TdE surtout au Grand Lomé. Le score de synthèse ne classe que les cantons déjà présents dans ces sources, **pas** les 388 cantons du pays.
- Les deux échelles démographiques ne sont jamais mélangées dans un même graphique.


## Structure

```
streamlit_app/
├── app.py              → page d'accueil (chiffres clés + limites méthodologiques)
├── utils.py             → chargement des données, mis en cache, palettes de couleurs
├── dashboard_data/       → données déjà traitées par le pipeline
└── pages/
    ├── 1_Cartographie.py
    ├── 2_Maintenance.py
    ├── 3_Demographie.py
    ├── 4_Risque_Inondation.py
    └── 5_Synthese.py
```

## Installation et lancement

```bash
pip install streamlit plotly pydeck geopandas pyarrow
streamlit run app.py
```

L'app s'ouvre automatiquement dans le navigateur (http://localhost:8501).

Python 3.10+ recommandé. L'app se lance depuis la racine du dépôt, quel que soit le répertoire de travail : les chemins de données sont calculés à partir de `utils.py`.
