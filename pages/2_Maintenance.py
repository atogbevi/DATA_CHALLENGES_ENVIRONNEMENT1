"""
Page 2 - Maintenance
=======================
Objectif pedagogique : deux graphiques cote a cote, JAMAIS fusionnes, pour ne
pas laisser penser qu'ils mesurent la meme chose :
1. Le risque de maintenance (proxy : absence de plan d'entretien)
2. L'avancement des travaux (status / current_status_of_the_site)
Le premier est un risque futur, le second est un etat de chantier passe.
"""
import plotly.express as px
import streamlit as st

from utils import bandeau_institutionnel, charger_parquet, styliser_figure

bandeau_institutionnel(
    "Risque de maintenance et avancement des travaux",
    ":material/construction:",
)

st.warning(
    "Aucune donnée de panne ou d'abandon réelle n'existe dans les sources "
    "disponibles. Le « risque de maintenance » ci-dessous est un **proxy** basé sur "
    "l'existence (ou non) d'un plan d'entretien prévu — pas un taux de panne "
    "mesuré. Ces indicateurs concernent **uniquement COSO** (218 ouvrages) : "
    "TdE n'a pas de champ équivalent dans les données disponibles.",
    icon=":material/info:",
    title="Limite des données",
)

df_maintenance_region = charger_parquet("page2_maintenance/maintenance_risk_par_region.parquet")
df_maintenance_canton = charger_parquet("page2_maintenance/maintenance_risk_par_canton.parquet")
df_avancement = charger_parquet("page2_maintenance/avancement_travaux_par_region.parquet")

col_risque, col_chantier = st.columns((1.05, 1), gap="large")

with col_risque:
    st.markdown("## Taux de sites sans plan d'entretien")
    st.caption("Par région — proxy d'un risque de maintenance futur.")

    fig_maintenance_region = px.bar(
        df_maintenance_region.sort_values("taux_sans_plan_entretien", ascending=True),
        x="taux_sans_plan_entretien", y="region", orientation="h",
        text_auto=".0%",
        labels={"taux_sans_plan_entretien": "% sans plan d'entretien", "region": ""},
        color="taux_sans_plan_entretien", color_continuous_scale="Reds",
    )
    fig_maintenance_region.update_layout(height=320, coloraxis_showscale=False)
    fig_maintenance_region.update_traces(textposition="outside")
    styliser_figure(fig_maintenance_region)
    st.plotly_chart(fig_maintenance_region, width="stretch", config={"displaylogo": False})

with col_chantier:
    st.markdown("## Avancement des travaux")
    st.caption("Indépendant du risque de maintenance — état de chantier passé.")

    champ_choisi = st.radio(
        "Champ source", options=["current_status_of_the_site", "status"],
        horizontal=True,
        help="Deux champs bruts du jeu COSO, avec un decoupage legerement different des memes chantiers.",
    )

    df_avancement_filtre = df_avancement[df_avancement["champ_source"] == champ_choisi]

    fig_avancement = px.bar(
        df_avancement_filtre, x="region", y="nb_ouvrages", color="libelle_statut",
        labels={"nb_ouvrages": "Nombre d'ouvrages", "region": "", "libelle_statut": "Statut"},
        barmode="stack",
        color_discrete_sequence=["#0B4D3A", "#006A4E", "#C9A227", "#4A6B5E", "#1C2321", "#7A8F85"],
    )
    fig_avancement.update_layout(height=320)
    styliser_figure(fig_avancement)
    st.plotly_chart(fig_avancement, width="stretch", config={"displaylogo": False})

with st.expander("Détail par canton", icon=":material/table_rows:"):
    seuil_min = st.slider(
        "Nombre minimum d'ouvrages pour afficher un canton (fiabilité)",
        min_value=1, max_value=10, value=3,
        help="En dessous de ce seuil, le taux repose sur trop peu d'ouvrages pour être fiable.",
    )
    df_canton_filtre = df_maintenance_canton[df_maintenance_canton["nb_ouvrages"] >= seuil_min]
    st.caption(
        f"{len(df_canton_filtre)} / {len(df_maintenance_canton)} cantons affichés "
        f"(seuil : {seuil_min} ouvrages minimum)"
    )
    st.dataframe(
        df_canton_filtre.sort_values("taux_sans_plan_entretien", ascending=False),
        column_config={
            "taux_sans_plan_entretien": st.column_config.ProgressColumn(
                "Taux sans plan", min_value=0, max_value=1, format="%.0f%%"
            ),
        },
        hide_index=True, width="stretch",
    )
