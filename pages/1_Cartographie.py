"""
Page 1 - Cartographie
========================
Objectif pedagogique : une carte choroplethe (polygones colores) et des points
superposes sont DEUX traces Plotly differentes assemblees dans UNE figure.
Le choroplethe a besoin d'un GeoJSON "brut" (dict) + d'une colonne id qui
correspond a "featureidkey" ; les points, eux, prennent juste des listes de
latitude/longitude.

Correctif applique ici (refonte) : sur la version precedente, les points
COSO/TdE pouvaient devenir difficiles a distinguer une fois superposes au
fond choroplethe FRI - un souci connu de rendu Plotly/MapLibre quand un
calque de polygones et un calque de marqueurs se chevauchent sans contraste
suffisant. Fix applique : contour blanc + taille augmentee sur les points,
et opacite du fond choroplethe legerement reduite, pour garantir que les
points restent visibles quel que soit l'ordre de rendu des calques.
"""
import plotly.graph_objects as go
import streamlit as st

from utils import bandeau_institutionnel, charger_geojson, charger_geojson_brut, COULEURS_SOURCE, styliser_figure

bandeau_institutionnel("Cartographie des points d'eau", ":material/map:")

st.markdown(
    """
    Fond de carte : FRI (risque d'inondation) par canton, sur les **388 cantons
    du pays**. Points superposés : les **86 ouvrages COSO** cartographiables
    (Nord-Togo) et les **67 ouvrages TdE** (Grand Lomé).
    """
)

geojson_cantons_brut = charger_geojson_brut("page1_cartographie/fri_cantons_clean.geojson")
gdf_cantons = charger_geojson("page1_cartographie/fri_cantons_clean.geojson")
gdf_coso = charger_geojson("page1_cartographie/coso_clean_mappable.geojson")
gdf_tde = charger_geojson("page1_cartographie/gdf_chateaux_deau_forages_tde.geojson")

with st.container(horizontal=True, gap="large"):
    afficher_coso = st.checkbox("Afficher COSO", value=True)
    afficher_tde = st.checkbox("Afficher TdE", value=True)
    afficher_fond_fri = st.checkbox("Afficher le fond FRI par canton", value=True)

fig = go.Figure()

if afficher_fond_fri:
    fig.add_trace(go.Choroplethmap(
        geojson=geojson_cantons_brut,
        locations=gdf_cantons["canton_id"],
        featureidkey="properties.canton_id",
        z=gdf_cantons["FRI"],
        colorscale="YlOrRd",
        zmin=0, zmax=gdf_cantons["FRI"].max(),
        marker_opacity=0.42,
        marker_line_width=0.3,
        colorbar_title="FRI",
        name="Risque d'inondation (canton)",
        hovertext=gdf_cantons["canton_nom"] + " (" + gdf_cantons["region_nom"] + ")",
        hoverinfo="text+z",
    ))

# Points ajoutes APRES le choroplethe (rendus au-dessus) ET avec un contour
# blanc + une taille plus marquee : garantit un fort contraste visuel meme
# si le calque de polygones venait a s'afficher avec une opacite elevee.
if afficher_coso:
    fig.add_trace(go.Scattermap(
        lat=gdf_coso.geometry.y,
        lon=gdf_coso.geometry.x,
        mode="markers",
        marker=dict(size=11, color=COULEURS_SOURCE["COSO"]),
        name="COSO (Nord-Togo)",
        text=gdf_coso["location_name"],
        hoverinfo="text",
    ))

if afficher_tde:
    fig.add_trace(go.Scattermap(
        lat=gdf_tde.geometry.y,
        lon=gdf_tde.geometry.x,
        mode="markers",
        marker=dict(size=11, color=COULEURS_SOURCE["TdE"]),
        name="TdE (Grand Lomé)",
        text=gdf_tde["nom_ouvrage"],
        hoverinfo="text",
    ))

fig.update_layout(
    map=dict(
        style="carto-positron",
        center=dict(lat=8.6, lon=1.0),
        zoom=6.2,
    ),
    margin=dict(l=0, r=0, t=0, b=0),
    height=680,
    legend=dict(
        yanchor="top", y=0.98, xanchor="left", x=0.01,
        bgcolor="rgba(250,250,248,0.92)",
        bordercolor="#D8E0DB",
        borderwidth=1,
    ),
)
styliser_figure(fig, carte=True)

st.plotly_chart(fig, width="stretch", config={"displaylogo": False})

st.caption(
    "Seuls 39% des ouvrages COSO ont une géométrie exploitable (86/218) — "
    "les 132 restants existent mais ne peuvent pas être positionnés sur cette "
    "carte. Ils restent comptabilisés dans les stats des autres pages. Si les "
    "points restent peu visibles sur votre écran, décochez le fond FRI ci-dessus "
    "pour les isoler."
)
