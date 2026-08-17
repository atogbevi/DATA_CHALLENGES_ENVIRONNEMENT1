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

from utils import bandeau_institutionnel, charger_geojson, COULEURS_RISQUE_INONDATION, styliser_figure

bandeau_institutionnel(
    "Exposition des ouvrages au risque d'inondation",
    ":material/flood:",
)

st.markdown(
    """
    Le **FRI (Flood Risk Index)** affiché ici est extrait précisément pour
    chaque point (grille 1 km), pas la moyenne de son canton car un point peut
    être dans une zone moins exposée que le reste de son canton.
    """
)

gdf_points_fri = charger_geojson("page4_risque_inondation/points_eau_avec_fri.geojson")
gdf_points_fri = gdf_points_fri.to_crs("EPSG:4326")

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
    height=620,
)
# Correctif (refonte) : px.scatter_map n'applique aucune taille de marqueur
# par defaut -> sur le fond clair "carto-positron", les points (surtout le
# jaune "Modere") pouvaient devenir quasi invisibles a l'echelle nationale.
# On force une taille plus grande, comme sur la carte Cartographie (page 1).
# NB : contrairement aux marqueurs scatter "classiques", scattermap.Marker
# ne supporte pas de contour (pas d'attribut "line") - la taille est le
# seul levier de contraste disponible ici.
fig_carte.update_traces(marker=dict(size=11))
fig_carte.update_layout(
    map_style="carto-positron",
    margin=dict(l=0, r=0, t=0, b=0),
    legend=dict(
        yanchor="top", y=0.98, xanchor="left", x=0.01,
        bgcolor="rgba(250,250,248,0.92)",
        bordercolor="#D8E0DB",
        borderwidth=1,
    ),
)
styliser_figure(fig_carte, carte=True)
st.plotly_chart(fig_carte, width="stretch", config={"displaylogo": False})

points_sans_fri = gdf_points_fri["FRI"].isna().sum()
if points_sans_fri > 0:
    st.caption(
        f"{points_sans_fri} point(s) non affiché(s) : hors couverture de la "
        f"grille FRI (cas de bordure frontalière)."
    )

st.markdown(
    f"""
    <div class="legende-fri">
      <div class="legende-fri-item"><span class="swatch" style="background:{COULEURS_RISQUE_INONDATION['Faible']}"></span> Faible <span class="val">0 – 0,079</span></div>
      <div class="legende-fri-item"><span class="swatch" style="background:{COULEURS_RISQUE_INONDATION['Modéré']}"></span> Modéré <span class="val">0,079 – 0,110</span></div>
      <div class="legende-fri-item"><span class="swatch" style="background:{COULEURS_RISQUE_INONDATION['Élevé']}"></span> Élevé <span class="val">0,110 – 0,198</span></div>
      <div class="legende-fri-item"><span class="swatch" style="background:{COULEURS_RISQUE_INONDATION['Très élevé']}"></span> Très élevé <span class="val">&gt; 0,198</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption(
    "Seuils calculés sur les quartiles des 388 cantons (population complète), "
    "pas sur l'échantillon de points."
)

st.markdown("### Répartition des ouvrages par niveau de risque")

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
fig_repartition.update_layout(height=360, showlegend=False)
styliser_figure(fig_repartition)
st.plotly_chart(fig_repartition, width="stretch", config={"displaylogo": False})
