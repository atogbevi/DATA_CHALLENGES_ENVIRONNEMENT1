"""
utils.py - Fonctions partagees a toutes les pages du dashboard

Objectif : centraliser ici tout ce qui est repete d'une page a l'autre
(chemins de donnees, palettes de couleurs, mise en cache) - evite de
dupliquer la meme logique plusieurs fois et garantit que "risque eleve" a
toujours la meme couleur, quelle que soit la page.
"""

from pathlib import Path
import json
import geopandas as gpd
import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Chemin vers les donnees, calcule depuis l'emplacement de CE fichier plutot
# qu'ecrit en dur -> l'app fonctionne peu importe d'ou elle est lancee.
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).resolve().parent / "dashboard_data"

# ---------------------------------------------------------------------------
# Palettes de couleurs partagees. Definies une seule fois ici pour que la
# meme categorie ait toujours la meme couleur sur toutes les pages.
# Ces couleurs de SIGNALISATION (risque, source) sont independantes de la
# palette institutionnelle (verte/or) utilisee pour l'habillage general —
# jamais reutilisees comme couleur de "chrome" pour ne pas diluer leur sens.
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


# ---------------------------------------------------------------------------
# Couche visuelle uniquement (aucune logique de donnees).
# ---------------------------------------------------------------------------
_CSS_PATH = Path(__file__).resolve().parent / "static" / "style.css"


def injecter_styles() -> None:
    """Charge le CSS institutionnel. Appele depuis app.py et chaque page."""
    css = _CSS_PATH.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def bandeau_institutionnel(titre: str, icone: str) -> None:
    """En-tete de page : petite capitale (eyebrow) + titre serif.

    Remplace volontairement l'ancien filet vert sous le titre : une ligne
    d'accent sous un titre est un des signes les plus reconnaissables d'une
    interface generee par IA. La hierarchie visuelle vient ici de
    l'espacement et du contraste de police (Fraunces vs IBM Plex Mono), pas
    d'un trait.
    """
    injecter_styles()
    st.markdown(
        '<p class="eyebrow-page"><span class="puce"></span>'
        "Togo AI Lab · Défi Environnement · Accès à l'eau potable</p>",
        unsafe_allow_html=True,
    )
    st.markdown(f'<h1 class="titre-page">{titre}</h1>', unsafe_allow_html=True)


def marque_sidebar() -> None:
    """En-tete de la barre laterale, visible sur toutes les pages."""
    st.markdown(
        """
        <div class="sidebar-marque">
          <span class="nom">Diagnostic eau potable</span>
          <span class="sous">Togo AI Lab · Environnement</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def styliser_figure(fig, *, carte: bool = False):
    """Applique la typographie institutionnelle sans modifier les traces de donnees."""
    fig.update_layout(
        font=dict(family="IBM Plex Sans, sans-serif", color="#1C2321", size=13),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    if not carte:
        fig.update_xaxes(gridcolor="#E4EBE7", zeroline=False, linecolor="#D8E0DB")
        fig.update_yaxes(gridcolor="#E4EBE7", zeroline=False, linecolor="#D8E0DB")
    return fig
