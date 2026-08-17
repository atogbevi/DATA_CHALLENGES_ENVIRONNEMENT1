"""
Page 1 - Cartographie
========================
Objectif pedagogique : une carte choroplethe (polygones colores) et des points
superposes sont DEUX traces Plotly differentes assemblees dans UNE figure.
Le choroplethe a besoin d'un GeoJSON "brut" (dict) + d'une colonne id qui
correspond a "featureidkey" ; les points, eux, prennent juste des listes de
latitude/longitude.
"""
import plotly.graph_objects as go
import streamlit as st

from utils import DATA_DIR, charger_geojson, charger_geojson_brut, COULEURS_SOURCE

st.set_page_config(page_title="Cartographie", page_icon="🗺️", layout="wide")
st.title("🗺️ Cartographie des points d'eau")

st.markdown(
    """
    Fond de carte : FRI (risque d'inondation) par canton, sur les **388 cantons
    du pays**. Points superposés : les **86 ouvrages COSO** cartographiables
    (Nord-Togo) et les **67 ouvrages TdE** (Grand Lomé).
    """
)

# ---------------------------------------------------------------------------
# Chargement des donnees (mis en cache par utils.py, donc rapide meme si
# l'utilisateur change de filtre plusieurs fois).
# ---------------------------------------------------------------------------
geojson_cantons_brut = charger_geojson_brut("page1_cartographie/fri_cantons_clean.geojson")
gdf_cantons = charger_geojson("page1_cartographie/fri_cantons_clean.geojson")
gdf_coso = charger_geojson("page1_cartographie/coso_clean_mappable.geojson")
gdf_tde = charger_geojson("page1_cartographie/gdf_chateaux_deau_forages_tde.geojson")

# ---------------------------------------------------------------------------
# Filtres simples dans la barre laterale : quelle(s) source(s) afficher.
# ---------------------------------------------------------------------------
with st.sidebar:
    st.subheader("Filtres")
    afficher_coso = st.checkbox("Afficher COSO", value=True)
    afficher_tde = st.checkbox("Afficher TdE", value=True)
    afficher_fond_fri = st.checkbox("Afficher le fond FRI par canton", value=True)

# ---------------------------------------------------------------------------
# Construction de la figure : on assemble les traces une par une dans un
# meme objet go.Figure, qui partage un seul systeme de coordonnees (mapbox).
# ---------------------------------------------------------------------------
fig = go.Figure()

if afficher_fond_fri:
    fig.add_trace(go.Choroplethmap(
        geojson=geojson_cantons_brut,
        locations=gdf_cantons["canton_id"],
        featureidkey="properties.canton_id",
        z=gdf_cantons["FRI"],
        colorscale="YlOrRd",
        zmin=0, zmax=gdf_cantons["FRI"].max(),
        marker_opacity=0.55,
        marker_line_width=0.3,
        colorbar_title="FRI",
        name="Risque d'inondation (canton)",
        hovertext=gdf_cantons["canton_nom"] + " (" + gdf_cantons["region_nom"] + ")",
        hoverinfo="text+z",
    ))

if afficher_coso:
    fig.add_trace(go.Scattermap(
        lat=gdf_coso.geometry.y,
        lon=gdf_coso.geometry.x,
        mode="markers",
        marker=dict(size=8, color=COULEURS_SOURCE["COSO"]),
        name="COSO (Nord-Togo)",
        text=gdf_coso["location_name"],
        hoverinfo="text",
    ))

if afficher_tde:
    fig.add_trace(go.Scattermap(
        lat=gdf_tde.geometry.y,
        lon=gdf_tde.geometry.x,
        mode="markers",
        marker=dict(size=8, color=COULEURS_SOURCE["TdE"]),
        name="TdE (Grand Lomé)",
        text=gdf_tde["nom_ouvrage"],
        hoverinfo="text",
    ))

fig.update_layout(
    map=dict(
        style="carto-positron",  # fond de carte gratuit, pas de token requis
        center=dict(lat=8.6, lon=1.0),  # centre approximatif du Togo
        zoom=6.2,
    ),
    margin=dict(l=0, r=0, t=0, b=0),
    height=650,
    legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.8)"),
)

st.plotly_chart(fig, width="stretch")

st.info(
    "💡 Remarque de lecture : seuls 39% des ouvrages COSO ont une géométrie "
    "exploitable (86/218) — les 132 restants existent mais ne peuvent pas être "
    "positionnés sur cette carte. Ils restent comptabilisés dans les stats des "
    "autres pages.",
    icon="ℹ️",
)
