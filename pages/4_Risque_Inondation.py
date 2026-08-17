"""
Page 4 - Risque d'inondation
================================
Objectif pedagogique : montrer le FRI EXACT de chaque point (extrait de la
grille 1km, etape 4 du pipeline), pas le FRI du canton entier — rappel de la
decouverte methodologique : le FRI d'un canton peut etre tire vers le haut par
ses zones les plus exposees, alors qu'un point precis peut etre ailleurs.
"""
import plotly.express as px
import streamlit as st

from utils import charger_geojson, COULEURS_RISQUE_INONDATION

st.set_page_config(page_title="Risque d'inondation", page_icon="🌊", layout="wide")
st.title("🌊 Exposition des ouvrages au risque d'inondation")

st.markdown(
    """
    Le **FRI (Flood Risk Index)** affiché ici est extrait précisément pour
    chaque point (grille 1km), pas la moyenne de son canton — un point peut
    être dans une zone moins exposée que le reste de son canton.
    """
)

gdf_points_fri = charger_geojson("page4_risque_inondation/points_eau_avec_fri.geojson")

# ---------------------------------------------------------------------------
# 1. Carte des points colores par niveau de risque.
# ---------------------------------------------------------------------------
niveaux_ordonnes = ["Faible", "Modéré", "Élevé", "Très élevé"]

fig_carte = px.scatter_map(
    gdf_points_fri.dropna(subset=["FRI"]),
    lat=gdf_points_fri.dropna(subset=["FRI"]).geometry.y,
    lon=gdf_points_fri.dropna(subset=["FRI"]).geometry.x,
    color="niveau_risque_inondation",
    category_orders={"niveau_risque_inondation": niveaux_ordonnes},
    color_discrete_map=COULEURS_RISQUE_INONDATION,
    hover_name="nom_ouvrage",
    hover_data={"region": True, "type_source": True, "FRI": ":.3f"},
    zoom=6.2, center=dict(lat=8.6, lon=1.0),
    height=600,
)
fig_carte.update_layout(
    map_style="carto-positron",
    margin=dict(l=0, r=0, t=0, b=0),
    legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.8)"),
)
st.plotly_chart(fig_carte, width="stretch")

points_sans_fri = gdf_points_fri["FRI"].isna().sum()
if points_sans_fri > 0:
    st.caption(
        f"ℹ️ {points_sans_fri} point(s) non affiché(s) : hors couverture de la "
        f"grille FRI (cas de bordure frontalière, voir étape 4 du pipeline)."
    )

st.divider()

# ---------------------------------------------------------------------------
# 2. Repartition par niveau de risque, avec seuils rappeles.
# ---------------------------------------------------------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Répartition des ouvrages par niveau de risque")
    df_repartition = (
        gdf_points_fri["niveau_risque_inondation"].value_counts()
        .reindex(niveaux_ordonnes).reset_index()
    )
    df_repartition.columns = ["niveau", "nb_ouvrages"]
    fig_repartition = px.bar(
        df_repartition, x="niveau", y="nb_ouvrages",
        color="niveau", color_discrete_map=COULEURS_RISQUE_INONDATION,
        text_auto=True,
        labels={"nb_ouvrages": "Nombre d'ouvrages", "niveau": ""},
    )
    fig_repartition.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig_repartition, width="stretch")

with col2:
    st.subheader("Seuils utilisés")
    st.caption("Calculés sur les quartiles des 388 cantons (population complète), pas sur l'échantillon de points.")
    st.markdown(
        """
        | Niveau | FRI |
        |---|---|
        | Faible | 0 – 0,079 |
        | Modéré | 0,079 – 0,110 |
        | Élevé | 0,110 – 0,198 |
        | Très élevé | > 0,198 |
        """
    )
