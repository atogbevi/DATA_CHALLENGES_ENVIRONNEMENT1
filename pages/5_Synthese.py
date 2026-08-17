"""
Page 5 - Synthese et recommandations
========================================
Objectif pedagogique : le score de priorisation est une MOYENNE SIMPLE de 3
indicateurs normalises (pas de poids arbitraires a defendre devant un jury).
On rappelle explicitement sa limite : il ne couvre que les cantons deja
representes dans COSO/TdE, pas les 388 cantons du pays.
"""
import plotly.express as px
import streamlit as st

from utils import charger_parquet

st.set_page_config(page_title="Synthèse", page_icon="🎯", layout="wide")
st.title("🎯 Synthèse & recommandations de priorisation")

df_score = charger_parquet("page5_synthese/score_priorisation_canton.parquet")

st.warning(
    f"Ce score couvre **{len(df_score)} cantons** disposant simultanément des "
    f"3 signaux (maintenance, inondation, démographie) — **pas** un classement "
    f"des 388 cantons du pays. Il ne peut inclure aucun canton de Maritime : "
    f"le risque de maintenance vient uniquement de COSO (Nord-Togo), qui ne "
    f"couvre pas cette région.",
    icon="⚠️",
)

st.markdown(
    """
    **Méthode** : chaque indicateur (taux sans plan d'entretien, FRI, habitants
    par ouvrage) est ramené entre 0 et 1, puis les 3 sont **moyennés simplement**
    — pas de pondération arbitraire à justifier devant un jury.
    """
)

# ---------------------------------------------------------------------------
# 1. Top cantons prioritaires.
# ---------------------------------------------------------------------------
st.subheader("Cantons prioritaires (score le plus élevé)")

nb_top = st.slider("Nombre de cantons à afficher", 5, len(df_score), 10)
df_top = df_score.sort_values("score_priorisation", ascending=False).head(nb_top)

fig_top = px.bar(
    df_top.sort_values("score_priorisation"),
    x="score_priorisation", y="canton", orientation="h",
    color="region",
    text_auto=".2f",
    labels={"score_priorisation": "Score de priorisation", "canton": ""},
    height=max(350, nb_top * 32),
)
st.plotly_chart(fig_top, width="stretch")

st.divider()

# ---------------------------------------------------------------------------
# 2. Detail des 3 composantes du score, pour comprendre POURQUOI un canton
#    est prioritaire (pas juste un chiffre final opaque).
# ---------------------------------------------------------------------------
st.subheader("Détail des 3 composantes par canton")

st.dataframe(
    df_top[[
        "region", "canton", "taux_sans_plan_entretien", "FRI",
        "habitants_par_ouvrage", "score_priorisation"
    ]].sort_values("score_priorisation", ascending=False),
    column_config={
        "taux_sans_plan_entretien": st.column_config.ProgressColumn(
            "Sans plan d'entretien", min_value=0, max_value=1, format="%.0f%%"
        ),
        "FRI": st.column_config.NumberColumn("FRI", format="%.3f"),
        "habitants_par_ouvrage": st.column_config.NumberColumn("Hab./ouvrage", format="%.0f"),
        "score_priorisation": st.column_config.ProgressColumn(
            "Score global", min_value=0, max_value=1, format="%.2f"
        ),
    },
    hide_index=True, width="stretch",
)

st.divider()

# ---------------------------------------------------------------------------
# 3. Recommandations textuelles, ancrees sur les chiffres ci-dessus.
# ---------------------------------------------------------------------------
st.subheader("Recommandations")

canton_top1 = df_top.sort_values("score_priorisation", ascending=False).iloc[0]

st.markdown(
    f"""
    1. **Prioriser l'entretien** dans les cantons en tête de liste (ex. **{canton_top1['canton']}**,
       région {canton_top1['region']}) : taux sans plan d'entretien de
       {canton_top1['taux_sans_plan_entretien']:.0%}, FRI de {canton_top1['FRI']:.3f}.
    2. **Étendre la collecte de données** en Maritime et Plateaux : ces régions sont
       structurellement absentes du score faute de champ de maintenance dans TdE
       et de couverture suffisante dans les sources disponibles.
    3. **Traiter Savanes en priorité pour les plans d'entretien** : 86,5% des
       ouvrages n'ont aucun plan prévu, le taux le plus élevé du pays.
    """
)
