"""
utils.py - Fonctions partagees a toutes les pages du dashboard

Objectif : centraliser ici tout ce qui est répété d'une page à l'autre
(chemins de données, palettes de couleurs, mise en cache) évite de dupliquer 
la même logique plusieurs fois et garantit que "risque élevé" a toujours la même couleur, 
quelle que soit la page.
"""

from pathlib import Path
import json
import geopandas as gpd
import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Chemin vers les donnees, calcule depuis l'emplacement de CE fichier plutot
# qu'ecrit en dur -> l'app fonctionne peu importe d'ou elle est lancee.
# dashboard_data/ est copie A L'INTERIEUR de streamlit_app/ (voir etape
# d'export) pour que le dossier streamlit_app/ soit autonome : on peut le
# zipper seul et le lancer sur n'importe quel ordinateur sans dependance
# externe. D'ou un seul .parent (pas .parent.parent).
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).resolve().parent / "dashboard_data"

# ---------------------------------------------------------------------------
# Palettes de couleurs partagees. Definies une seule fois ici pour que la
# meme categorie ait toujours la meme couleur sur toutes les pages.
# ---------------------------------------------------------------------------
COULEURS_RISQUE_INONDATION = {
    "Faible": "#2ecc71",
    "Modéré": "#f1c40f",
    "Élevé": "#e67e22",
    "Très élevé": "#e74c3c",
}

COULEURS_SOURCE = {
    "COSO": "#2980b9",
    "TdE": "#8e44ad",
}

# ---------------------------------------------------------------------------
# Chargement des donnees, mis en cache pour que Streamlit ne relise pas les
# fichiers a chaque interaction utilisateur (clic, changement de filtre).
# ---------------------------------------------------------------------------


@st.cache_data
def charger_geojson(chemin_relatif: str) -> gpd.GeoDataFrame:
    return gpd.read_file(DATA_DIR / chemin_relatif)


@st.cache_data
def charger_parquet(chemin_relatif: str) -> pd.DataFrame:
    return pd.read_parquet(DATA_DIR / chemin_relatif)


@st.cache_data
def charger_geojson_brut(chemin_relatif: str) -> dict:
    """Pour les cas ou Plotly a besoin du GeoJSON brut (dict Python), pas d'un GeoDataFrame."""
    with open(DATA_DIR / chemin_relatif, encoding="utf-8") as f:
        return json.load(f)
