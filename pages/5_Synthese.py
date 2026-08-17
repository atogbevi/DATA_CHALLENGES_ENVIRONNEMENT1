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

from utils import bandeau_institutionnel, charger_parquet, styliser_figure

bandeau_institutionnel(
    "Synthèse et recommandations de priorisation",
    ":material/target:",
)

df_score = charger_parquet("page5_synthese/score_priorisation_canton.parquet")

st.warning(
    f"Ce score couvre **{len(df_score)} cantons** disposant simultanément des "
    f"3 signaux (maintenance, inondation, démographie) — **pas** un classement "
    f"des 388 cantons du pays. Il ne peut inclure aucun canton de Maritime : "
    f"le risque de maintenance vient uniquement de COSO (Nord-Togo), qui ne "
    f"couvre pas cette région.",
    icon=":material/info:",
    title="Périmètre du score",
)

st.markdown(
    """
    **Méthode** : chaque indicateur (taux sans plan d'entretien, FRI, habitants
    par ouvrage) est ramené entre 0 et 1, puis les 3 sont **moyennés simplement**
    — pas de pondération arbitraire à justifier devant un jury.
    """
)

st.markdown("## Cantons prioritaires")

nb_top = st.slider("Nombre de cantons à afficher", 5, len(df_score), 10)
df_top = df_score.sort_values("score_priorisation", ascending=False).head(nb_top)

fig_top = px.bar(
    df_top.sort_values("score_priorisation"),
    x="score_priorisation", y="canton", orientation="h",
    color="region",
    text_auto=".2f",
    labels={"score_priorisation": "Score de priorisation", "canton": ""},
    color_discrete_sequence=["#0B4D3A", "#006A4E", "#C9A227", "#4A6B5E", "#1C2321"],
    height=max(350, nb_top * 32),
)
styliser_figure(fig_top)
st.plotly_chart(fig_top, width="stretch", config={"displaylogo": False})

st.markdown("## Lecture du score, canton par canton")
st.caption("Les trois composantes sont affichées sous chaque canton du classement, pour expliquer le rang plutôt que de le laisser opaque.")

for rang, (_, row) in enumerate(
    df_top.sort_values("score_priorisation", ascending=False).iterrows(),
    start=1,
):
    st.markdown(
        f"""
        <div class="canton-entete">
          <span class="nom">{rang}. {row['canton']}</span>
          <span class="region">{row['region']}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c_score, c_plan, c_fri, c_hab = st.columns(4)
    c_score.metric("Score global", f"{row['score_priorisation']:.2f}", icon=":material/target:")
    c_plan.metric("Sans plan d'entretien", f"{row['taux_sans_plan_entretien']:.0%}", icon=":material/construction:")
    c_fri.metric("FRI", f"{row['FRI']:.3f}", icon=":material/flood:")
    c_hab.metric("Hab. / ouvrage", f"{row['habitants_par_ouvrage']:.0f}", icon=":material/groups:")
    st.markdown('<hr class="filet-canton">', unsafe_allow_html=True)

st.markdown("## Recommandations")

canton_top1 = df_top.sort_values("score_priorisation", ascending=False).iloc[0]

st.markdown(
    f"""
    <div class="reco">
      <p><strong>1. Prioriser l'entretien</strong> dans les cantons en tête de liste (ex. <strong>{canton_top1['canton']}</strong>,
      région {canton_top1['region']}) : taux sans plan d'entretien de
      {canton_top1['taux_sans_plan_entretien']:.0%}, FRI de {canton_top1['FRI']:.3f}.</p>
    </div>
    <div class="reco">
      <p><strong>2. Étendre la collecte de données</strong> en Maritime et Plateaux : ces régions sont
      structurellement absentes du score faute de champ de maintenance dans TdE
      et de couverture suffisante dans les sources disponibles.</p>
    </div>
    <div class="reco">
      <p><strong>3. Traiter Savanes en priorité pour les plans d'entretien</strong> : 86,5% des
      ouvrages n'ont aucun plan prévu, le taux le plus élevé du pays.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
