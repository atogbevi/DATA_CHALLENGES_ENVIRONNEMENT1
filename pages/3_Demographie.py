"""
Page 3 - Demographie
========================
Objectif pedagogique : deux echelles de population bien distinguees (region =
officielle 2010, canton = modelisee fri_cantons), jamais melangees dans le
meme graphique. Et les zones a faible couverture de donnees sont grisees /
signalees, jamais presentees comme un vrai indicateur de penurie.
"""
import plotly.express as px
import streamlit as st

from utils import charger_parquet

st.set_page_config(page_title="Démographie", page_icon="👥", layout="wide")
st.title("👥 Pression démographique")

st.markdown(
    """
    **Pression démographique** = nombre d'habitants qui dépendent, en moyenne,
    d'un seul point d'eau dans une zone. Plus ce chiffre est élevé, plus la
    zone est potentiellement sous-équipée.
    """
)

df_demo_region = charger_parquet("page3_demographie/demographie_pression_region.parquet")
df_demo_canton = charger_parquet("page3_demographie/demographie_pression_canton.parquet")

# ---------------------------------------------------------------------------
# 1. Echelle region (population officielle 2010) — le chiffre fiable a mettre
#    en avant.
# ---------------------------------------------------------------------------
st.subheader("1. Par région (population officielle, recensement 2010)")

df_demo_region_fiable = df_demo_region[df_demo_region["couverture_donnees_suffisante"]]
df_demo_region_non_fiable = df_demo_region[~df_demo_region["couverture_donnees_suffisante"]]

if len(df_demo_region_non_fiable) > 0:
    zones_exclues = ", ".join(df_demo_region_non_fiable["region_norm"].tolist())
    st.info(
        f"ℹ️ **{zones_exclues}** exclue(s) du graphique ci-dessous : trop peu "
        f"d'ouvrages recensés dans COSO/TdE pour que le ratio reflète une vraie "
        f"pénurie plutôt qu'un simple trou de données (hors périmètre des sources "
        f"disponibles, pas forcément hors périmètre de la réalité).",
        icon="ℹ️",
    )

fig_demo_region = px.bar(
    df_demo_region_fiable.sort_values("habitants_par_ouvrage", ascending=True),
    x="habitants_par_ouvrage", y="region_norm", orientation="h",
    text_auto=".2s",
    labels={"habitants_par_ouvrage": "Habitants par ouvrage", "region_norm": ""},
    color="habitants_par_ouvrage", color_continuous_scale="Blues",
)
fig_demo_region.update_layout(height=280, coloraxis_showscale=False)
fig_demo_region.update_traces(textposition="outside")
st.plotly_chart(fig_demo_region, width="stretch")

st.divider()

# ---------------------------------------------------------------------------
# 2. Echelle canton (population modelisee fri_cantons) — plus de granularite,
#    mais autre source, jamais comparee chiffre a chiffre avec la region.
# ---------------------------------------------------------------------------
st.subheader("2. Par canton (population modélisée — autre source que ci-dessus)")
st.caption(
    "⚠️ Cette population vient de `fri_cantons.gpkg` (modélisée), pas du "
    "recensement officiel utilisé au niveau région. Les deux échelles ne sont "
    "pas directement comparables chiffre à chiffre."
)

seuil_min_canton = st.slider(
    "Nombre minimum d'ouvrages pour afficher un canton", min_value=1, max_value=10, value=3,
)
df_canton_filtre = df_demo_canton[df_demo_canton["nb_ouvrages"] >= seuil_min_canton]

st.dataframe(
    df_canton_filtre[[
        "region_nom", "canton_nom", "total_pop", "nb_ouvrages", "habitants_par_ouvrage"
    ]].sort_values("habitants_par_ouvrage", ascending=False),
    column_config={
        "total_pop": st.column_config.NumberColumn("Population", format="%.0f"),
        "habitants_par_ouvrage": st.column_config.NumberColumn("Hab. / ouvrage", format="%.0f"),
    },
    hide_index=True, width="stretch", height=400,
)
