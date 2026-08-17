"""
app.py - Page d'accueil du dashboard
=======================================
Objectif pedagogique : cette page ne fait AUCUN calcul, elle affiche
uniquement des chiffres deja produits par le pipeline (etapes 1 a 7). C'est
la regle qu'on s'est fixee des le depart : la logique metier vit dans les
scripts Python, pas dans l'app.
"""
import streamlit as st

from utils import (
    bandeau_institutionnel,
    charger_geojson,
    charger_parquet,
    injecter_styles,
    marque_sidebar,
)

st.set_page_config(
    page_title="Accès à l'eau potable au Togo",
    page_icon=":material/water_drop:",
    layout="wide",
    initial_sidebar_state="expanded",
)

injecter_styles()

with st.sidebar:
    marque_sidebar()


def page_accueil() -> None:
    bandeau_institutionnel(
        "Diagnostic de l'accès à l'eau potable au Togo",
        ":material/water_drop:",
    )
    # Motif geometrique : UNE SEULE occurrence dans tout le site, ici.
    st.markdown('<div class="motif-signature" aria-hidden="true"></div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="signature-auteur">Réalisé par Angelica TOGBEVI — Analyste de données et développeuse web</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="intro-accueil">
        Ce dashboard croise les infrastructures hydrauliques (COSO, Nord-Togo et
        TdE, Grand Lomé), la démographie et le risque d'inondation pour proposer
        un diagnostic et des recommandations de priorisation.
        Utilisez le menu à gauche pour naviguer entre les cinq pages d'analyse.
        </div>
        """,
        unsafe_allow_html=True,
    )

    gdf_coso = charger_geojson("page1_cartographie/coso_clean_mappable.geojson")
    gdf_tde = charger_geojson("page1_cartographie/gdf_chateaux_deau_forages_tde.geojson")
    df_maintenance_region = charger_parquet("page2_maintenance/maintenance_risk_par_region.parquet")
    df_score = charger_parquet("page5_synthese/score_priorisation_canton.parquet")

    col1, col2, col3, col4 = st.columns([1.15, 1, 1.2, 1])
    col1.metric(
        "Ouvrages recensés",
        "285",
        help="218 microprojets COSO (Nord-Togo) + 67 châteaux/forages TdE (Grand Lomé)",
        icon=":material/water_drop:",
    )
    col2.metric(
        "Points cartographiés",
        f"{len(gdf_coso) + len(gdf_tde)}",
        help="Sous-ensemble avec géométrie exploitable : 86/218 COSO + 67/67 TdE",
        icon=":material/map:",
    )
    col3.metric(
        "Taux moyen sans plan d'entretien",
        f"{df_maintenance_region['taux_sans_plan_entretien'].mean():.0%}",
        help="COSO uniquement — TdE n'a pas ce champ dans les données disponibles",
        icon=":material/construction:",
    )
    col4.metric(
        "Cantons priorisables",
        f"{len(df_score)}",
        help="Cantons disposant des 3 signaux (maintenance, inondation, démographie) simultanément",
        icon=":material/target:",
    )

    st.markdown("## Limites méthodologiques à garder en tête")
    st.markdown(
        """
        <div class="bloc-limites">
          <div class="note-limite">
            <strong>Pas de taux de panne mesuré</strong>
            <p>Aucune donnée de panne ou d'abandon réelle n'existe dans les sources : la page Maintenance utilise un proxy (existence d'un plan d'entretien), jamais un vrai taux de fonctionnalité.</p>
          </div>
          <div class="note-limite">
            <strong>Couverture géographique partielle</strong>
            <p>COSO couvre le Nord-Togo, TdE couvre surtout Grand Lomé : le score de priorisation (page Synthèse) ne peut classer que les zones déjà représentées dans ces deux sources, pas les 388 cantons du pays.</p>
          </div>
          <div class="note-limite">
            <strong>Deux échelles démographiques</strong>
            <p>La démographie combine deux échelles différentes (population officielle 2010 au niveau région, population modélisée au niveau canton) — jamais confondues dans les mêmes graphiques.</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


pg = st.navigation(
    [
        st.Page(
            page_accueil,
            title="Accueil",
            icon=":material/water_drop:",
            default=True,
            url_path="accueil",
        ),
        st.Page("pages/1_Cartographie.py", title="Cartographie", icon=":material/map:"),
        st.Page("pages/2_Maintenance.py", title="Maintenance", icon=":material/construction:"),
        st.Page("pages/3_Demographie.py", title="Démographie", icon=":material/groups:"),
        st.Page("pages/4_Risque_Inondation.py", title="Risque d'inondation", icon=":material/flood:"),
        st.Page("pages/5_Synthese.py", title="Synthèse", icon=":material/target:"),
    ],
    position="sidebar",
    expanded=True,
)
pg.run()
