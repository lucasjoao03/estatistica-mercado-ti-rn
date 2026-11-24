"""
Etapa 5 - Análise exploratória e estatística do painel UF x ano.

Perguntas:
  P1. Estados que formam mais profissionais de TI (por habitante) têm mais
      emprego formal em TI (por habitante)?
  P2. Formação está associada a salários de TI maiores ou menores?
  P3. A formação de um ano antecipa o emprego do ano seguinte (defasagem)?
  P4. A participação feminina na formação acompanha a do mercado?
  P5. Onde o RN se posiciona em relação ao esperado pelo modelo?

Entrada:  dados/processados/painel_uf_ano.csv
Saídas:   resultados/ (tabelas .csv, gráficos .png, modelos .txt, relatorio.md)
"""
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.diagnostic import het_breuschpagan

import config

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message="covariance of constraints")

OUT = config.RESULTADOS
FOCO = config.UF_FOCO
NORDESTE = ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"]

# Cores (paleta categórica validada; o restante fica em cinza)
COR_FOCO = "#2a78d6"     # RN
COR_NE = "#eb6834"       # Nordeste
COR_BR = "#1baf7a"       # Brasil
COR_OUTRAS = "#b4b2a9"
TINTA = "#3d3d3a"
TINTA_SEC = "#73726c"

plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 200, "savefig.bbox": "tight",
    "font.size": 10, "axes.titlesize": 12, "axes.titleweight": "bold",
    "axes.edgecolor": "#d3d1c7", "axes.labelcolor": TINTA_SEC,
    "xtick.color": TINTA_SEC, "ytick.color": TINTA_SEC,
    "axes.grid": True, "grid.color": "#ebeae4", "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False,
})

# Pares (x, y) analisados nas correlações
PARES = [
    ("concluintes_ti_100k", "vinculos_ti_100k", "P1 Formação x emprego"),
    ("concluintes_ti_100k", "salario_medio_ti", "P2 Formação x salário médio TI"),
    ("concluintes_ti_100k", "salario_relativo_ti", "P2 Formação x salário relativo TI"),
    ("concluintes_ti_100k_lag1", "vinculos_ti_100k", "P3 Formação (t-1) x emprego (t)"),
    ("cresc_concluintes_ti_pct", "cresc_vinculos_ti_pct", "P3 Crescimento formação x crescimento emprego"),
    ("pct_fem_concluintes_ti", "pct_fem_vinculos_ti", "P4 % mulheres formação x mercado"),
]

ROTULOS = {
    "concluintes_ti_100k": "Concluintes de TI por 100 mil hab.",
    "concluintes_ti_100k_lag1": "Concluintes de TI por 100 mil hab. (ano anterior)",
    "vinculos_ti_100k": "Empregos formais de TI por 100 mil hab.",
    "salario_medio_ti": "Salário médio em TI (R$)",
    "salario_relativo_ti": "Salário TI / salário médio geral",
    "pct_fem_concluintes_ti": "% mulheres entre concluintes de TI",
    "pct_fem_vinculos_ti": "% mulheres nos empregos de TI",
    "concluintes_por_100_vinculos": "Concluintes por 100 empregos de TI",
    "participacao_ti_emprego": "% do emprego formal que é TI",
}


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def correlacao(x: pd.Series, y: pd.Series) -> dict:
    m = x.notna() & y.notna() & np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    if len(x) < 5:
        return {"n": len(x)}
    r, p_r = stats.pearsonr(x, y)
    rho, p_rho = stats.spearmanr(x, y)
    return {"n": len(x), "pearson_r": r, "pearson_p": p_r,
            "spearman_rho": rho, "spearman_p": p_rho}


def forca(r: float) -> str:
    a = abs(r)
    if a < 0.1:
        return "desprezível"
    if a < 0.3:
        return "fraca"
    if a < 0.5:
        return "moderada"
    if a < 0.7:
        return "forte"
    return "muito forte"


def agregado(painel: pd.DataFrame, ufs=None) -> pd.DataFrame:
    """Indicadores de um grupo de UFs calculados como soma/soma (não média de taxas)."""
    d = painel if ufs is None else painel[painel["sigla_uf"].isin(ufs)]
    g = d.groupby("ano")[["concluintes_ti", "vinculos_ti", "populacao"]].sum()
    return pd.DataFrame({
        "concluintes_ti_100k": g["concluintes_ti"] / g["populacao"] * 1e5,
        "vinculos_ti_100k": g["vinculos_ti"] / g["populacao"] * 1e5,
        "concluintes_por_100_vinculos": 100 * g["concluintes_ti"] / g["vinculos_ti"],
    })


# ---------------------------------------------------------------------------
# 1. Estatística descritiva
# ---------------------------------------------------------------------------
def descritiva(painel: pd.DataFrame, ano: int) -> pd.DataFrame:
    cols = ["concluintes_ti_100k", "vinculos_ti_100k", "salario_medio_ti",
            "salario_relativo_ti", "concluintes_por_100_vinculos",
            "participacao_ti_emprego", "pct_fem_concluintes_ti", "pct_fem_vinculos_ti"]
    d = painel[painel["ano"] == ano].set_index("sigla_uf")[cols]
    tab = d.describe().T[["mean", "std", "min", "50%", "max"]]
    tab.columns = ["media", "desvio_padrao", "minimo", "mediana", "maximo"]
    tab["cv_pct"] = 100 * tab["desvio_padrao"] / tab["media"]
    if FOCO in d.index:
        tab[f"valor_{FOCO}"] = d.loc[FOCO]
        tab[f"posicao_{FOCO}_de_27"] = d.rank(ascending=False).loc[FOCO].astype(int)
    tab.index = [ROTULOS.get(i, i) for i in tab.index]
    tab.round(2).to_csv(OUT / f"01_descritiva_{ano}.csv")
    return tab


# ---------------------------------------------------------------------------
# 2. Correlações
# ---------------------------------------------------------------------------
def correlacoes(painel: pd.DataFrame, ano: int) -> pd.DataFrame:
    linhas = []
    for x, y, nome in PARES:
        corte = painel[painel["ano"] == ano]
        linhas.append({"pergunta": nome, "recorte": f"corte transversal {ano}",
                       **correlacao(corte[x], corte[y])})
        linhas.append({"pergunta": nome, "recorte": "painel (todos os anos)",
                       **correlacao(painel[x], painel[y])})
    tab = pd.DataFrame(linhas)
    tab["forca"] = tab["pearson_r"].apply(lambda r: forca(r) if pd.notna(r) else "")
    tab.round(4).to_csv(OUT / "02_correlacoes.csv", index=False)

    # Estabilidade: correlação P1 em cada ano
    por_ano = pd.DataFrame([
        {"ano": a, **correlacao(g["concluintes_ti_100k"], g["vinculos_ti_100k"])}
        for a, g in painel.groupby("ano")
    ])
    por_ano.round(4).to_csv(OUT / "03_correlacao_P1_por_ano.csv", index=False)
    return tab


# ---------------------------------------------------------------------------
# 3. Regressões
# ---------------------------------------------------------------------------
def regressoes(painel: pd.DataFrame, ano: int) -> dict:
    d = painel.copy()
    d["log_vinc"] = np.log(d["vinculos_ti_100k"])
    d["log_conc"] = np.log(d["concluintes_ti_100k"])
    d["log_conc_lag"] = np.log(d["concluintes_ti_100k_lag1"])
    d["log_sal"] = np.log(d["salario_medio_ti"])

    res = {}

    # M1 - corte transversal (n = 27): elasticidade emprego x formação
    corte = d[d["ano"] == ano].dropna(subset=["log_vinc", "log_conc"])
    m1 = smf.ols("log_vinc ~ log_conc", data=corte).fit(cov_type="HC1")
    res["M1"] = m1

    # M2 - painel agrupado com defasagem e efeito de ano; erros agrupados por UF
    p = d.dropna(subset=["log_vinc", "log_conc_lag"])
    m2 = smf.ols("log_vinc ~ log_conc_lag + C(ano)", data=p).fit(
        cov_type="cluster", cov_kwds={"groups": p["sigla_uf"]})
    res["M2"] = m2

    # M3 - efeitos fixos de UF e ano: variação DENTRO de cada estado
    m3 = smf.ols("log_vinc ~ log_conc_lag + C(sigla_uf) + C(ano)", data=p).fit(
        cov_type="cluster", cov_kwds={"groups": p["sigla_uf"]})
    res["M3"] = m3

    # M4 - salário x formação (corte transversal)
    c4 = d[d["ano"] == ano].dropna(subset=["log_sal", "log_conc"])
    m4 = smf.ols("log_sal ~ log_conc", data=c4).fit(cov_type="HC1")
    res["M4"] = m4

    # Diagnósticos do M1 (pressupostos da regressão)
    sw = stats.shapiro(m1.resid)
    bp = het_breuschpagan(m1.resid, m1.model.exog)
    res["diag_M1"] = {"shapiro_W": sw.statistic, "shapiro_p": sw.pvalue,
                      "breusch_pagan_LM": bp[0], "breusch_pagan_p": bp[1]}

    # Resíduo do RN: acima de 0 = mais emprego do que o esperado pela formação
    corte = corte.assign(residuo=m1.resid, previsto=np.exp(m1.fittedvalues))
    res["residuos_M1"] = corte[["sigla_uf", "concluintes_ti_100k", "vinculos_ti_100k",
                                "previsto", "residuo"]].sort_values("residuo")
    res["residuos_M1"].round(4).to_csv(OUT / f"05_residuos_M1_{ano}.csv", index=False)

    with open(OUT / "04_modelos.txt", "w", encoding="utf-8") as f:
        descr = {
            "M1": f"log(empregos TI/100k) ~ log(concluintes TI/100k) | corte {ano}, erros HC1",
            "M2": "log(empregos TI/100k) ~ log(concluintes t-1) + efeito de ano | painel, erros por UF",
            "M3": "log(empregos TI/100k) ~ log(concluintes t-1) + efeitos fixos UF e ano",
            "M4": f"log(salário médio TI) ~ log(concluintes TI/100k) | corte {ano}, erros HC1",
        }
        for k in ("M1", "M2", "M3", "M4"):
            f.write(f"{'=' * 78}\n{k}: {descr[k]}\n{'=' * 78}\n")
            f.write(res[k].summary().as_text() + "\n\n")
        f.write("Diagnósticos M1\n" + "\n".join(
            f"  {k}: {v:.4f}" for k, v in res["diag_M1"].items()))
    return res


# ---------------------------------------------------------------------------
# 4. Gráficos
# ---------------------------------------------------------------------------
def _rotular_pontos(ax, d, x, y):
    for _, r in d.iterrows():
        destaque = r["sigla_uf"] == FOCO
        ax.annotate(r["sigla_uf"], (r[x], r[y]), xytext=(4, 3),
                    textcoords="offset points", fontsize=8 if not destaque else 10,
                    color=TINTA if destaque else TINTA_SEC,
                    fontweight="bold" if destaque else "normal")


def grafico_dispersao(painel, ano, x, y, nome_arq, titulo, log=True):
    d = painel[painel["ano"] == ano].dropna(subset=[x, y])
    fig, ax = plt.subplots(figsize=(7.5, 5.5))
    outras, foco = d[d["sigla_uf"] != FOCO], d[d["sigla_uf"] == FOCO]
    ax.scatter(outras[x], outras[y], s=48, color=COR_OUTRAS,
               edgecolor="white", linewidth=1.5, zorder=3, label="Demais UFs")
    ax.scatter(foco[x], foco[y], s=90, color=COR_FOCO,
               edgecolor="white", linewidth=2, zorder=4, label=FOCO)

    # Reta de regressão (na escala usada no gráfico)
    xs, ys = (np.log(d[x]), np.log(d[y])) if log else (d[x], d[y])
    b, a = np.polyfit(xs, ys, 1)
    grade = np.linspace(xs.min(), xs.max(), 100)
    linha = a + b * grade
    ax.plot(np.exp(grade) if log else grade, np.exp(linha) if log else linha,
            color=TINTA_SEC, linewidth=2, linestyle="--", zorder=2, label="Tendência")
    if log:
        ax.set_xscale("log")
        ax.set_yscale("log")
        fmt = matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}".replace(",", "."))
        for eixo in (ax.xaxis, ax.yaxis):
            eixo.set_major_formatter(fmt)
            eixo.set_minor_formatter(fmt)
            eixo.set_minor_locator(matplotlib.ticker.LogLocator(subs=(2, 3, 5)))
        ax.tick_params(which="minor", labelsize=8)

    _rotular_pontos(ax, d, x, y)
    c = correlacao(d[x], d[y])
    ax.set_title(titulo, loc="left", color=TINTA, pad=24)
    ax.text(0, 1.02, f"{ano} · n = {c['n']} UFs · Pearson r = {c['pearson_r']:.2f} "
            f"(p = {c['pearson_p']:.3f}) · Spearman ρ = {c['spearman_rho']:.2f}",
            transform=ax.transAxes, fontsize=9, color=TINTA_SEC, va="bottom")
    ax.set_xlabel(ROTULOS.get(x, x) + (" (escala log)" if log else ""))
    ax.set_ylabel(ROTULOS.get(y, y) + (" (escala log)" if log else ""))
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(1.01, 1))
    ax.text(0, -0.14, "Fontes: INEP (Censo da Educação Superior), MTE (RAIS), IBGE.",
            transform=ax.transAxes, fontsize=8, color=TINTA_SEC)
    fig.savefig(OUT / nome_arq)
    plt.close(fig)


def grafico_evolucao(painel):
    series = {
        FOCO: (agregado(painel, [FOCO]), COR_FOCO),
        "Nordeste": (agregado(painel, NORDESTE), COR_NE),
        "Brasil": (agregado(painel), COR_BR),
    }
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for ax, col, tit in zip(
        axes, ["concluintes_ti_100k", "vinculos_ti_100k"],
        ["Concluintes de TI por 100 mil hab.", "Empregos formais de TI por 100 mil hab."],
    ):
        for nome, (s, cor) in series.items():
            ax.plot(s.index, s[col], color=cor, linewidth=2, marker="o",
                    markersize=5, markeredgecolor="white", label=nome)
            ax.annotate(nome, (s.index[-1], s[col].iloc[-1]), xytext=(6, 0),
                        textcoords="offset points", fontsize=9, color=TINTA, va="center")
        ax.set_title(tit, loc="left", color=TINTA, fontsize=11)
        ax.set_ylim(bottom=0)
        ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
    axes[0].legend(frameon=False, loc="lower right")
    fig.suptitle("Formação e emprego em TI: RN, Nordeste e Brasil",
                 x=0.06, ha="left", fontweight="bold", color=TINTA)
    fig.tight_layout()
    fig.savefig(OUT / "g1_evolucao_rn_ne_br.png")
    plt.close(fig)


def grafico_barras_relacao(painel, ano):
    col = "concluintes_por_100_vinculos"
    d = painel[painel["ano"] == ano].sort_values(col)
    cores = [COR_FOCO if u == FOCO else COR_OUTRAS for u in d["sigla_uf"]]
    fig, ax = plt.subplots(figsize=(7.5, 7))
    ax.barh(d["sigla_uf"], d[col], color=cores, height=0.72, edgecolor="white", linewidth=1)
    br = agregado(painel).loc[ano, col]
    ax.axvline(br, color=TINTA_SEC, linestyle="--", linewidth=1.5)
    ax.set_ylim(-0.7, len(d) + 0.6)
    ax.text(br, len(d) - 0.1, f" Brasil: {br:.1f}", color=TINTA_SEC, fontsize=9)
    rn = d.loc[d["sigla_uf"] == FOCO, col]
    if len(rn):
        ax.text(rn.iloc[0], list(d["sigla_uf"]).index(FOCO), f" {rn.iloc[0]:.1f}",
                va="center", fontsize=9, color=TINTA, fontweight="bold")
    ax.set_title(f"Concluintes de TI para cada 100 empregos formais de TI ({ano})",
                 loc="left", color=TINTA)
    ax.set_xlabel("Valores altos = forma muito em relação ao mercado formal local")
    ax.grid(axis="y", visible=False)
    fig.savefig(OUT / "g4_concluintes_por_100_empregos.png")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 5. Relatório
# ---------------------------------------------------------------------------
def relatorio(painel, ano, desc, corr, mods):
    def lin(pergunta, recorte):
        r = corr[(corr["pergunta"] == pergunta) & (corr["recorte"] == recorte)]
        if r.empty or pd.isna(r["pearson_r"].iloc[0]):
            return "n/d"
        r = r.iloc[0]
        sig = "significativa" if r["pearson_p"] < 0.05 else "não significativa"
        return (f"r = {r['pearson_r']:.2f} ({r['forca']}, {sig}, p = {r['pearson_p']:.3f}); "
                f"ρ = {r['spearman_rho']:.2f}; n = {int(r['n'])}")

    m1, m2, m3, m4 = (mods[k] for k in ("M1", "M2", "M3", "M4"))
    res = mods["residuos_M1"].set_index("sigla_uf")
    rn_res = res.loc[FOCO] if FOCO in res.index else None
    diag = mods["diag_M1"]

    txt = [f"# Resultados automáticos - Formação x Mercado de TI ({config.ANO_INICIO}-{config.ANO_FIM})",
           "", f"Painel: {painel['sigla_uf'].nunique()} UFs x {painel['ano'].nunique()} anos "
           f"= {len(painel)} observações. Corte transversal de referência: {ano}.", "",
           "## Correlações", ""]
    for _, _, nome in PARES:
        txt.append(f"- **{nome}**")
        txt.append(f"  - {ano}: {lin(nome, f'corte transversal {ano}')}")
        txt.append(f"  - painel: {lin(nome, 'painel (todos os anos)')}")
    txt += ["", "## Regressões (coeficiente = elasticidade)", "",
            f"- **M1** (corte {ano}): +1% em concluintes/100k → "
            f"{m1.params['log_conc']:+.2f}% em empregos/100k "
            f"(p = {m1.pvalues['log_conc']:.3f}; R² = {m1.rsquared:.2f})",
            f"- **M2** (painel, formação t-1, efeito de ano): {m2.params['log_conc_lag']:+.2f} "
            f"(p = {m2.pvalues['log_conc_lag']:.3f}; R² = {m2.rsquared:.2f})",
            f"- **M3** (efeitos fixos UF e ano): {m3.params['log_conc_lag']:+.2f} "
            f"(p = {m3.pvalues['log_conc_lag']:.3f}) - mede se, DENTRO de um mesmo estado, "
            "anos com mais formação antecedem anos com mais emprego",
            f"- **M4** (salário x formação, {ano}): {m4.params['log_conc']:+.2f} "
            f"(p = {m4.pvalues['log_conc']:.3f}; R² = {m4.rsquared:.2f})",
            "", "### Pressupostos do M1",
            f"- Normalidade dos resíduos (Shapiro-Wilk): W = {diag['shapiro_W']:.3f}, "
            f"p = {diag['shapiro_p']:.3f}",
            f"- Homocedasticidade (Breusch-Pagan): LM = {diag['breusch_pagan_LM']:.3f}, "
            f"p = {diag['breusch_pagan_p']:.3f} (erros robustos HC1 já usados)", ""]
    if rn_res is not None:
        pos = list(res.index).index(FOCO) + 1
        txt += [f"## Posição do {FOCO}", "",
                f"- Concluintes de TI/100k: {rn_res['concluintes_ti_100k']:.1f}; "
                f"empregos de TI/100k observados: {rn_res['vinculos_ti_100k']:.1f}; "
                f"previstos pelo M1: {rn_res['previsto']:.1f}",
                f"- Resíduo: {rn_res['residuo']:+.3f} (≈ {100 * (np.exp(rn_res['residuo']) - 1):+.0f}% "
                f"em relação ao esperado) - {pos}º menor de {len(res)} UFs",
                "- Resíduo negativo: o estado tem MENOS emprego formal em TI do que o "
                "esperado para o volume de formação (indício de que o mercado local não "
                "absorve todos os formados). Positivo: o contrário.", ""]
        if f"valor_{FOCO}" in desc:
            txt += [f"### Indicadores do {FOCO} em {ano} (posição entre as 27 UFs)", ""]
            for i, r in desc.iterrows():
                txt.append(f"- {i}: {r[f'valor_{FOCO}']:.2f} "
                           f"({int(r[f'posicao_{FOCO}_de_27'])}º; média das UFs {r['media']:.2f})")
    txt += ["", "## Gráficos", "",
            "- g1_evolucao_rn_ne_br.png", "- g2_dispersao_formacao_emprego.png",
            "- g3_dispersao_formacao_salario.png", "- g4_concluintes_por_100_empregos.png",
            "- g5_dispersao_mulheres.png", "",
            "> Lembrete: correlação não implica causalidade. Os resultados indicam "
            "associação entre formação e mercado, não que um cause o outro."]
    (OUT / "relatorio.md").write_text("\n".join(txt), encoding="utf-8")


def main() -> None:
    painel = pd.read_csv(config.ARQ_PAINEL)
    ano = int(painel["ano"].max())
    print(f"Painel: {len(painel)} linhas; ano de referência {ano}")

    desc = descritiva(painel, ano)
    corr = correlacoes(painel, ano)
    mods = regressoes(painel, ano)

    grafico_evolucao(painel)
    grafico_dispersao(painel, ano, "concluintes_ti_100k", "vinculos_ti_100k",
                      "g2_dispersao_formacao_emprego.png",
                      "Estados que formam mais em TI têm mais emprego em TI?")
    grafico_dispersao(painel, ano, "concluintes_ti_100k", "salario_medio_ti",
                      "g3_dispersao_formacao_salario.png",
                      "Formação em TI e salário médio em TI")
    grafico_barras_relacao(painel, ano)
    grafico_dispersao(painel, ano, "pct_fem_concluintes_ti", "pct_fem_vinculos_ti",
                      "g5_dispersao_mulheres.png",
                      "Mulheres na formação x mulheres no mercado de TI", log=False)

    relatorio(painel, ano, desc, corr, mods)
    print(f"OK: resultados em {OUT}")


if __name__ == "__main__":
    main()
