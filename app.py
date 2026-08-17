"""
app.py - Page d'accueil du dashboard
=======================================
Objectif pedagogique : cette page ne fait AUCUN calcul, elle affiche
uniquement des chiffres deja produits par le pipeline (etapes 1 a 7). C'est
la regle qu'on s'est fixee des le depart : la logique metier vit dans les
scripts Python, pas dans l'app.
"""
import streamlit as st

from utils import charger_geojson, charger_parquet

st.set_page_config(
    page_title="Accès à l'eau potable au Togo",
    page_icon="💧",
    layout="wide",
)

st.title("Diagnostic de l'accès à l'eau potable au Togo")
st.caption("Togo AI Lab — Défi Data Environnement — COSO + TdE + FRI/FSI")
st.caption("Réalisé par Angelica TOGBEVI - Analyste de données et Développeuse Web")


st.markdown(
    """
    Ce dashboard croise les infrastructures hydrauliques (COSO, Nord-Togo et
    TdE, Grand Lomé), la démographie et le risque d'inondation pour proposer
    un diagnostic et des recommandations de priorisation.

    **Utilisez le menu à gauche** pour naviguer entre les 5 pages d'analyse.
    """
)

st.divider()

# ---------------------------------------------------------------------------
# Chiffres cles : chaque metrique vient d'un fichier deja calcule, avec sa
# source clairement identifiee au survol (aucun recalcul ici).
# ---------------------------------------------------------------------------
gdf_coso = charger_geojson("page1_cartographie/coso_clean_mappable.geojson")
gdf_tde = charger_geojson("page1_cartographie/gdf_chateaux_deau_forages_tde.geojson")
df_maintenance_region = charger_parquet("page2_maintenance/maintenance_risk_par_region.parquet")
df_score = charger_parquet("page5_synthese/score_priorisation_canton.parquet")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Ouvrages recensés",
    "285",
    help="218 microprojets COSO (Nord-Togo) + 67 châteaux/forages TdE (Grand Lomé)",
)
col2.metric(
    "Points cartographiés",
    f"{len(gdf_coso) + len(gdf_tde)}",
    help="Sous-ensemble avec géométrie exploitable : 86/218 COSO + 67/67 TdE",
)
col3.metric(
    "Taux moyen sans plan d'entretien",
    f"{df_maintenance_region['taux_sans_plan_entretien'].mean():.0%}",
    help="COSO uniquement — TdE n'a pas ce champ dans les données disponibles",
)
col4.metric(
    "Cantons priorisables",
    f"{len(df_score)}",
    help="Cantons disposant des 3 signaux (maintenance, inondation, démographie) simultanément",
)

st.divider()

st.markdown(
    """
    ### ⚠️ Limites méthodologiques à garder en tête

    - **Aucune donnée de panne/abandon réelle** n'existe dans les sources : la page
      "Maintenance" utilise un **proxy** (existence d'un plan d'entretien), jamais
      un vrai taux de fonctionnalité.
    - **COSO couvre le Nord-Togo, TdE couvre surtout Grand Lomé** : le score de
      priorisation (page Synthèse) ne peut donc classer que les zones déjà
      représentées dans ces deux sources, pas les 388 cantons du pays.
    - La démographie combine **deux échelles différentes** (population officielle
      2010 au niveau région, population modélisée au niveau canton) — jamais
      confondues dans les mêmes graphiques.
    """
)
