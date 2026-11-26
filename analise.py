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
import argparse
import textwrap
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
import descritiva
from descritiva import ROTULOS

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
# 1. Estatística descritiva -> ver descritiva.py
# ---------------------------------------------------------------------------


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
# 2b. Testes de hipótese (normalidade, Wilcoxon, Mann-Whitney)
# ---------------------------------------------------------------------------
def _decisao(p: float) -> str:
    return "rejeita H0" if p < 0.05 else "não rejeita H0"


def crescimento_uf(painel: pd.DataFrame, ano_ini: int, ano_fim: int) -> pd.DataFrame:
    """Crescimento % de concluintes e de vínculos de TI de cada UF entre dois anos."""
    a = descritiva.corte(painel, ano_ini)[["concluintes_ti", "vinculos_ti"]]
    b = descritiva.corte(painel, ano_fim)[["concluintes_ti", "vinculos_ti"]]
    c = 100 * (b / a - 1)
    c.columns = ["cresc_concluintes_pct", "cresc_vinculos_pct"]
    c["diferenca_pp"] = c["cresc_concluintes_pct"] - c["cresc_vinculos_pct"]
    return c.dropna()


def testes_hipotese(painel: pd.DataFrame, ano_ini: int, ano_fim: int) -> pd.DataFrame:
    d = descritiva.corte(painel, ano_fim)
    linhas = []

    # a) Normalidade de cada indicador (Shapiro-Wilk)
    for col in descritiva.INDICADORES:
        s = d[col].dropna()
        w, p = stats.shapiro(s)
        linhas.append({
            "teste": f"Shapiro-Wilk: {ROTULOS[col]} ({ano_fim})", "variavel": col,
            "hipotese_nula": "os valores das UFs vêm de uma distribuição normal",
            "hipotese_alternativa": "a distribuição não é normal",
            "estatistica": w, "p_valor": p, "n": len(s), "decisao_5pct": _decisao(p),
            "interpretacao": ("normalidade rejeitada: preferir mediana e testes não "
                              "paramétricos" if p < 0.05 else
                              "sem evidência contra a normalidade"),
        })

    # b) Wilcoxon pareado: crescimento de concluintes x crescimento de vínculos
    c = crescimento_uf(painel, ano_ini, ano_fim)
    c.round(2).to_csv(OUT / f"06b_crescimento_uf_{ano_ini}_{ano_fim}.csv")
    w = stats.wilcoxon(c["cresc_concluintes_pct"], c["cresc_vinculos_pct"],
                       alternative="greater")
    n_maior = int((c["diferenca_pp"] > 0).sum())
    pos_rn = int(c["diferenca_pp"].rank(ascending=False, method="min").loc[FOCO])
    conclusao = ("há evidência de que, nas UFs em geral, a formação cresceu mais que o emprego"
                 if w.pvalue < 0.05 else
                 "no conjunto das UFs não há evidência de que a formação tenha crescido mais "
                 "que o emprego")
    linhas.append({
        "teste": f"Wilcoxon pareado: crescimento % concluintes x vínculos de TI ({ano_ini}-{ano_fim})",
        "variavel": "cresc_concluintes_pct - cresc_vinculos_pct",
        "hipotese_nula": "mediana da diferença (cresc. concluintes - cresc. vínculos) <= 0",
        "hipotese_alternativa": "os concluintes cresceram mais que os empregos (mediana > 0)",
        "estatistica": w.statistic, "p_valor": w.pvalue, "n": len(c),
        "decisao_5pct": _decisao(w.pvalue),
        "interpretacao": (
            f"{conclusao}. Mediana do cresc. dos concluintes {br(c['cresc_concluintes_pct'].median())}% x "
            f"vínculos {br(c['cresc_vinculos_pct'].median())}%; diferença mediana "
            f"{br(c['diferenca_pp'].median())} p.p.; em {n_maior} de {len(c)} UFs a formação "
            f"cresceu mais que o emprego. {FOCO}: {br(c.loc[FOCO, 'cresc_concluintes_pct'], 0)}% x "
            f"{br(c.loc[FOCO, 'cresc_vinculos_pct'], 0)}% (diferença de "
            f"{br(c.loc[FOCO, 'diferenca_pp'], 0)} p.p., {pos_rn}ª maior entre as UFs)"),
        "mediana_grupo_1": c["cresc_concluintes_pct"].median(),
        "mediana_grupo_2": c["cresc_vinculos_pct"].median(),
        "n_maior": n_maior, "pos_rn": pos_rn,
        "dif_rn": c.loc[FOCO, "diferenca_pp"],
    })

    # c) e d) Mann-Whitney: Nordeste x demais UFs
    ne = d.index.isin(NORDESTE)
    for col, alt, h1, sentido in [
        ("concluintes_por_100_vinculos", "greater",
         "o Nordeste forma mais em relação ao emprego (valores maiores)", "maior"),
        ("salario_medio_ti", "less", "o Nordeste paga menos em TI (valores menores)", "menor"),
    ]:
        g1, g2 = d.loc[ne, col].dropna(), d.loc[~ne, col].dropna()
        u = stats.mannwhitneyu(g1, g2, alternative=alt)
        dec = 0 if col == "salario_medio_ti" else 2
        linhas.append({
            "teste": f"Mann-Whitney U: {ROTULOS[col]}, Nordeste x demais UFs ({ano_fim})",
            "variavel": col,
            "hipotese_nula": "as distribuições do Nordeste e das demais UFs são iguais",
            "hipotese_alternativa": h1,
            "estatistica": u.statistic, "p_valor": u.pvalue, "n": len(g1) + len(g2),
            "decisao_5pct": _decisao(u.pvalue),
            "interpretacao": (
                f"mediana Nordeste (n={len(g1)}) {br(g1.median(), dec)} x demais "
                f"(n={len(g2)}) {br(g2.median(), dec)}; " +
                (f"há evidência de que o Nordeste tem valores {sentido}es"
                 if u.pvalue < 0.05 else
                 f"sem evidência suficiente de que o Nordeste tenha valores {sentido}es")),
            "mediana_grupo_1": g1.median(), "mediana_grupo_2": g2.median(),
        })

    tab = pd.DataFrame(linhas)
    saida = tab.rename(columns={
        "hipotese_nula": "hipotese_nula_H0", "hipotese_alternativa": "hipotese_alternativa_H1",
        "decisao_5pct": "decisao_5pct"})
    saida = saida.drop(columns=["variavel", "mediana_grupo_1", "mediana_grupo_2",
                                "n_maior", "pos_rn", "dif_rn"])
    saida["estatistica"] = saida["estatistica"].round(4)
    saida["p_valor"] = saida["p_valor"].map(lambda v: f"{v:.4g}")
    saida.to_csv(OUT / "06_testes_hipotese.csv", index=False)
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


def br(v: float, dec: int = 1) -> str:
    """Número no formato brasileiro (1.234,5)."""
    return f"{v:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")


FONTE = "Fontes: INEP (Censo da Educação Superior), MTE (RAIS), IBGE."
NOTA_BOX = ("Caixa: Q1 a Q3; linha interna: mediana; bigodes: até 1,5·IQR; "
            "siglas: outliers pelo critério de Tukey.")


def _caixa(ax, valores, pos, largura=0.5):
    ax.boxplot(valores, positions=[pos], widths=largura, whis=1.5, showfliers=False,
               patch_artist=True, zorder=2,
               boxprops={"facecolor": "#f1f0ea", "edgecolor": TINTA_SEC, "linewidth": 1.2},
               medianprops={"color": TINTA, "linewidth": 2},
               whiskerprops={"color": TINTA_SEC, "linewidth": 1.2},
               capprops={"color": TINTA_SEC, "linewidth": 1.2})


def _pontos_caixa(ax, s: pd.Series, pos: float, dec: int, rng, rotular_rn=True):
    """Pontos das UFs sobre o boxplot (jitter leve), RN destacado e outliers rotulados."""
    m = descritiva.medidas(s)
    outl = s[(s < m["limite_inferior_tukey"]) | (s > m["limite_superior_tukey"])]
    jit = pd.Series(rng.uniform(-0.09, 0.09, len(s)), index=s.index)
    outras = s.drop(FOCO, errors="ignore")
    ax.scatter(pos + jit[outras.index], outras, s=26, color=COR_OUTRAS,
               edgecolor="white", linewidth=0.8, zorder=3)
    if FOCO in s.index:
        ax.scatter(pos + jit[FOCO], s[FOCO], s=70, color=COR_FOCO,
                   edgecolor="white", linewidth=1.5, zorder=5)
        if rotular_rn:
            ax.annotate(f"{FOCO} {br(s[FOCO], dec)}", (pos + jit[FOCO], s[FOCO]),
                        xytext=(pos - 0.34, s[FOCO]), textcoords="data", ha="right",
                        va="center", fontsize=9, color=COR_FOCO, fontweight="bold",
                        arrowprops={"arrowstyle": "-", "color": COR_FOCO, "linewidth": 1})
    # Outliers: rótulo à direita; se muito perto do anterior, alterna para a esquerda
    faixa = s.max() - s.min()
    ultimo, lado = None, 1
    for uf, v in outl.sort_values().items():
        lado = -lado if (ultimo is not None and abs(v - ultimo) < 0.05 * faixa) else 1
        ax.annotate(uf, (pos + jit[uf], v), xytext=(9 * lado, 0), textcoords="offset points",
                    ha="left" if lado > 0 else "right", va="center",
                    fontsize=8.5, color=TINTA)
        ultimo = v
    return m


def grafico_boxplots(painel, ano):
    cols = ["concluintes_ti_100k", "vinculos_ti_100k",
            "concluintes_por_100_vinculos", "salario_medio_ti"]
    d = descritiva.corte(painel, ano)
    rng = np.random.default_rng(42)
    fig, axes = plt.subplots(1, len(cols), figsize=(14, 5.6))
    for ax, col in zip(axes, cols):
        dec = 0 if col == "salario_medio_ti" else 1
        _caixa(ax, d[col].dropna(), 0)
        m = _pontos_caixa(ax, d[col].dropna(), 0, dec, rng)
        ax.set_xlim(-0.8, 0.5)
        ax.set_xticks([])
        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(
            lambda v, _: br(v, 0) if v >= 100 or float(v).is_integer() else br(v, 1)))
        ax.grid(axis="x", visible=False)
        ax.set_title(textwrap.fill(ROTULOS[col], 22), loc="left", color=TINTA, fontsize=10.5)
        ax.text(0, -0.06, f"mediana {br(m['mediana'], dec)}\n{FOCO}: {m[f'faixa_quartil_{FOCO}']}",
                transform=ax.transAxes, fontsize=8.5, color=TINTA_SEC, va="top")
    fig.suptitle(f"Distribuição dos indicadores entre as 27 UFs ({ano})",
                 x=0.01, ha="left", fontweight="bold", color=TINTA)
    fig.text(0.01, -0.04, f"{NOTA_BOX} Pontos: UFs ({FOCO} em azul).\n{FONTE}",
             fontsize=8, color=TINTA_SEC)
    fig.tight_layout()
    fig.savefig(OUT / f"g6_boxplots_{ano}.png")
    plt.close(fig)


def grafico_boxplot_dois_anos(painel, ano_ini, ano_fim):
    col = "concluintes_por_100_vinculos"
    rng = np.random.default_rng(7)
    fig, ax = plt.subplots(figsize=(7.5, 5.8))
    pts = {}
    for pos, a in enumerate((ano_ini, ano_fim)):
        s = descritiva.corte(painel, a)[col].dropna()
        _caixa(ax, s, pos)
        m = _pontos_caixa(ax, s, pos, 1, rng, rotular_rn=False)
        pts[a] = (pos, s[FOCO], m)
    (x0, y0, m0), (x1, y1, m1) = pts[ano_ini], pts[ano_fim]
    ax.plot([x0, x1], [y0, y1], color=COR_FOCO, linestyle="--", linewidth=1.3, zorder=4)
    for lado, (a, (x, y, m)) in zip((-1, 1), pts.items()):
        ax.annotate(f"{FOCO} {a}: {br(y)}\n{m[f'faixa_quartil_{FOCO}']}\n"
                    f"({m[f'posicao_{FOCO}']}º de 27)",
                    (x, y), xytext=(x + 0.36 * lado, y), textcoords="data",
                    ha="right" if lado < 0 else "left", va="center", fontsize=9,
                    color=COR_FOCO, fontweight="bold",
                    arrowprops={"arrowstyle": "-", "color": COR_FOCO, "linewidth": 1})
    ax.set_xticks([0, 1], [str(ano_ini), str(ano_fim)])
    ax.set_xlim(-1.4, 1.9)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: br(v, 0)))
    ax.grid(axis="x", visible=False)
    ax.set_ylabel(ROTULOS[col])
    ax.set_title(f"Concluintes por 100 empregos de TI: {ano_ini} x {ano_fim}",
                 loc="left", color=TINTA, pad=24)
    ax.text(0, 1.02, f"{FOCO}: {m0[f'faixa_quartil_{FOCO}']} em {ano_ini} → "
            f"{m1[f'faixa_quartil_{FOCO}']} em {ano_fim}",
            transform=ax.transAxes, fontsize=9, color=TINTA_SEC, va="bottom")
    ax.text(0, -0.1, f"{NOTA_BOX}\n{FONTE}", transform=ax.transAxes,
            fontsize=8, color=TINTA_SEC, va="top")
    fig.savefig(OUT / f"g7_boxplot_{ano_ini}_x_{ano_fim}.png")
    plt.close(fig)


def grafico_histograma(painel, ano):
    col = "concluintes_por_100_vinculos"
    s = descritiva.corte(painel, ano)[col].dropna()
    m = descritiva.medidas(s)
    _, _, lim = descritiva.classes_sturges(s)
    fig, ax = plt.subplots(figsize=(8, 5))
    freq, _, _ = ax.hist(s, bins=lim, color=COR_OUTRAS, edgecolor="white",
                         linewidth=1.5, zorder=2)
    linhas = [("Média", m["media"], COR_NE, "-"),
              ("Mediana", m["mediana"], COR_BR, "--"),
              ("Moda (Czuber)", m["moda_czuber"], TINTA, ":")]
    for nome, v, cor, est in linhas:
        ax.axvline(v, color=cor, linestyle=est, linewidth=2.2, zorder=3,
                   label=f"{nome}: {br(v, 2)}")
    v_rn = s[FOCO]
    topo = freq.max()
    ax.annotate(f"{FOCO}: {br(v_rn, 2)}\n{m[f'faixa_quartil_{FOCO}']}",
                xy=(v_rn, 0), xytext=(v_rn, topo * 0.55), ha="center", fontsize=9,
                color=COR_FOCO, fontweight="bold",
                arrowprops={"arrowstyle": "-|>", "color": COR_FOCO, "linewidth": 1.5})
    ax.scatter([v_rn], [0], marker="o", s=60, color=COR_FOCO, edgecolor="white",
               linewidth=1.5, zorder=5, clip_on=False)
    ax.set_xticks(lim, [br(v, 1) for v in lim])
    ax.set_ylim(0, topo * 1.15)
    ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
    ax.grid(axis="x", visible=False)
    ax.set_xlabel(f"{ROTULOS[col]} (classes de Sturges: k = {len(lim) - 1}, "
                  f"h = {br(lim[1] - lim[0], 2)})")
    ax.set_ylabel("Número de UFs")
    ax.set_title(f"Distribuição de concluintes por 100 empregos de TI ({ano})",
                 loc="left", color=TINTA, pad=24)
    ax.text(0, 1.02, f"27 UFs · desvio-padrão {br(m['desvio_padrao'], 2)} · "
            f"CV {br(m['cv_pct'], 0)}% · assimetria {br(m['assimetria'], 2)}",
            transform=ax.transAxes, fontsize=9, color=TINTA_SEC, va="bottom")
    ax.legend(frameon=False, loc="upper right")
    ax.text(0, -0.17, FONTE, transform=ax.transAxes, fontsize=8, color=TINTA_SEC)
    fig.savefig(OUT / f"g8_histograma_concluintes_por_100_empregos_{ano}.png")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 5. Relatório
# ---------------------------------------------------------------------------
def fp(p: float) -> str:
    """p-valor formatado."""
    return "p < 0,001" if p < 0.001 else f"p = {br(p, 3)}"


def _tabela_md(cab: list, linhas: list) -> list:
    return (["| " + " | ".join(cab) + " |", "|" + "|".join("---" for _ in cab) + "|"]
            + ["| " + " | ".join(str(c) for c in l) + " |" for l in linhas])


def relatorio(painel, ano, desc, corr, testes, mods, robustez=None, versao=""):
    ano_ini = config.ANO_INICIO
    d23, rn = desc["desc"][ano], desc["rn"]

    def lin(pergunta, recorte):
        r = corr[(corr["pergunta"] == pergunta) & (corr["recorte"] == recorte)]
        if r.empty or pd.isna(r["pearson_r"].iloc[0]):
            return "n/d"
        r = r.iloc[0]
        sig = "significativa" if r["pearson_p"] < 0.05 else "não significativa"
        return (f"r = {br(r['pearson_r'], 2)} ({r['forca']}, {sig}, {fp(r['pearson_p'])}); "
                f"ρ de Spearman = {br(r['spearman_rho'], 2)} ({fp(r['spearman_p'])}); "
                f"n = {int(r['n'])}")

    m1, m2, m3, m4 = (mods[k] for k in ("M1", "M2", "M3", "M4"))
    diag = mods["diag_M1"]
    ufs, anos = painel["sigla_uf"].nunique(), painel["ano"].nunique()

    txt = [f"# Resultados automáticos - Formação x Mercado de TI "
           f"({painel['ano'].min()}-{painel['ano'].max()})",
           "", "Gerado por `analise.py`. Segue o fluxo PROBLEMA → DADOS → ANÁLISE ESTATÍSTICA "
           "→ DIÁLOGO → CONTRIBUIÇÕES; o diálogo com a literatura e as contribuições estão "
           "em `docs/estrutura_trabalho.md`.", ""]

    # ---- 1. Dados
    txt += ["## 1. Dados", "",
            "- **Fontes secundárias**: INEP - Censo da Educação Superior (cursos da área "
            f"CINE {config.CINE_AREA_GERAL_TI:02d}, Computação e TIC); MTE - RAIS Vínculos "
            f"(vínculos ativos em 31/12 nas CBOs {', '.join(config.CBO_TI)}); IBGE - "
            "estimativas de população. RAIS e população obtidas via Base dos Dados.",
            f"- **Período**: {painel['ano'].min()} a {painel['ano'].max()}; "
            f"**painel**: {ufs} UFs x {anos} anos = {len(painel)} observações.",
            "- **Junção**: chave `sigla_uf + ano` (RAIS x INEP por junção interna, população "
            "por junção à esquerda); linhas com UF fora das 27 (ex.: \"IGNORADO\" na RAIS) "
            "são descartadas.",
            f"- **Cortes transversais de referência**: {ano_ini} e {ano} (n = 27 UFs cada).",
            f"- **Formação (concluintes) considerada**: {versao}.",
            ""]

    # ---- 2. Descritiva
    cab = ["Indicador", "Média (x̄)", "Mediana (x̃)", "Moda (Czuber)", "s", "CV (%)",
           "Q1", "Q3", f"{FOCO}", f"Faixa do {FOCO} (posição)"]
    linhas = [[r["indicador"], br(r["media"], 2), br(r["mediana"], 2), br(r["moda_czuber"], 2),
               br(r["desvio_padrao"], 2), br(r["cv_pct"], 1), br(r["q1"], 2), br(r["q3"], 2),
               br(r[f"valor_{FOCO}"], 2),
               f"{r[f'faixa_quartil_{FOCO}']} ({int(r[f'posicao_{FOCO}_de_27'])}º)"]
              for _, r in d23.iterrows()]
    txt += ["## 2. Estatística descritiva", "",
            f"### 2.1 Resumo entre as 27 UFs ({ano})", ""] + _tabela_md(cab, linhas) + [
            "", f"Tabela completa (variância, amplitude, IQR, assimetria, outliers, classe "
            f"modal): `01_descritiva_{ano}.csv` (e `01_descritiva_{ano_ini}.csv`). "
            "Posição: 1º = maior valor.", ""]

    cab = ["Indicador", f"{FOCO} {ano_ini}", f"{FOCO} {ano}", "Variação (%)",
           f"Faixa {ano_ini}", f"Faixa {ano}", "Posição"]
    dc = {"concluintes_ti": 0, "vinculos_ti": 0}
    linhas = [[r["indicador"], br(r[f"valor_{FOCO}_{ano_ini}"], dc.get(v, 2)),
               br(r[f"valor_{FOCO}_{ano}"], dc.get(v, 2)), f"{br(r['variacao_pct'], 1)}%",
               r[f"faixa_quartil_{ano_ini}"], r[f"faixa_quartil_{ano}"],
               f"{int(r[f'posicao_{ano_ini}_de_27'])}º → {int(r[f'posicao_{ano}_de_27'])}º"]
              for v, r in rn.iterrows()]
    txt += [f"### 2.2 {FOCO}: {ano_ini} x {ano}", ""] + _tabela_md(cab, linhas) + [""]

    # Forma das distribuições (parágrafo gerado a partir dos números)
    mais = d23[d23["media"] > d23["mediana"]]
    destaque = ["vinculos_ti_100k", "concluintes_ti_100k", "salario_medio_ti",
                "participacao_ti_emprego"]
    partes = [f"{d23.loc[c, 'indicador']}: média {br(d23.loc[c, 'media'], 2)} x mediana "
              f"{br(d23.loc[c, 'mediana'], 2)} (CV {br(d23.loc[c, 'cv_pct'], 0)}%, outliers "
              f"{d23.loc[c, 'outliers_tukey']})" for c in destaque]
    sw = testes[testes["teste"].str.startswith("Shapiro")]
    n_rej = int((sw["p_valor"] < 0.05).sum())
    fortes = d23[d23["classificacao_assimetria"].str.startswith("forte")]
    outl = sorted({u.strip() for o in d23.loc[destaque, "outliers_tukey"]
                   for u in o.split(",") if u.strip() != "nenhum"})
    txt += ["### 2.3 Forma das distribuições e escolha da medida de referência", "",
            f"Em {len(mais)} dos {len(d23)} indicadores a média supera a mediana, sinal de "
            "assimetria à direita causada por poucos estados muito acima dos demais. Os casos "
            "mais marcantes: " + "; ".join(partes) + ". "
            f"A assimetria é forte (|g| ≥ 1) em {len(fortes)} indicadores e o teste de "
            f"Shapiro-Wilk rejeita a normalidade em {n_rej} dos {len(sw)}. Como a média é "
            f"puxada pelos polos ({', '.join(outl)}), a **mediana** e os **quartis** são as "
            f"referências mais adequadas para situar o {FOCO}, e os testes de comparação "
            "usados são não paramétricos.", "",
            "Notas de método: quartis por `pandas.quantile` (interpolação linear); moda de "
            f"Czuber calculada sobre classes de Sturges (k = {int(d23['n_classes_sturges'].iloc[0])} "
            "para n = 27); outliers pelo critério de Tukey (1,5·IQR). Tabelas de frequências: "
            "`01b_tabela_frequencias_*.csv`.", ""]

    # ---- 3. Testes
    cab = ["Indicador", "W", "p-valor", "Decisão (5%)"]
    linhas = [[ROTULOS[r["variavel"]], br(r["estatistica"], 3), fp(r["p_valor"]),
               r["decisao_5pct"]] for _, r in sw.iterrows()]
    txt += ["## 3. Testes de hipótese", "", f"### 3.1 Normalidade (Shapiro-Wilk, {ano})", "",
            "H0: os valores das 27 UFs vêm de uma distribuição normal.", ""] + \
        _tabela_md(cab, linhas) + ["", "### 3.2 Comparações (não paramétricas)", ""]
    for _, r in testes[~testes["teste"].str.startswith("Shapiro")].iterrows():
        txt += [f"- **{r['teste']}**",
                f"  - H0: {r['hipotese_nula']}; H1: {r['hipotese_alternativa']}",
                f"  - estatística = {br(r['estatistica'], 1)}; {fp(r['p_valor'])}; "
                f"n = {int(r['n'])} → **{r['decisao_5pct']}**",
                f"  - {r['interpretacao']}"]
    txt += ["", "### 3.3 Correlações (Pearson e Spearman)", ""]
    for _, _, nome in PARES:
        txt.append(f"- **{nome}**")
        txt.append(f"  - {ano}: {lin(nome, f'corte transversal {ano}')}")
        txt.append(f"  - painel: {lin(nome, 'painel (todos os anos)')}")
    txt += ["", "Detalhes: `06_testes_hipotese.csv`, `06b_crescimento_uf_*.csv`, "
            "`02_correlacoes.csv`, `03_correlacao_P1_por_ano.csv`.", ""]

    # ---- 4. Regressões
    m3_sig = m3.pvalues["log_conc_lag"] < 0.05
    txt += ["## 4. Regressões (resumo; coeficiente = elasticidade)", "",
            f"- **M1** (corte {ano}): +1% em concluintes/100k ↔ "
            f"{br(m1.params['log_conc'], 2)}% em empregos/100k "
            f"({fp(m1.pvalues['log_conc'])}; R² = {br(m1.rsquared, 2)})",
            f"- **M2** (painel, formação t-1, efeito de ano): {br(m2.params['log_conc_lag'], 2)} "
            f"({fp(m2.pvalues['log_conc_lag'])}; R² = {br(m2.rsquared, 2)})",
            f"- **M3** (efeitos fixos de UF e ano): {br(m3.params['log_conc_lag'], 2)} "
            f"({fp(m3.pvalues['log_conc_lag'])}) - DENTRO de um mesmo estado, anos com mais "
            "formação " + ("antecedem" if m3_sig else "não antecedem de forma significativa")
            + " anos com mais emprego",
            f"- **M4** (salário x formação, {ano}): {br(m4.params['log_conc'], 2)} "
            f"({fp(m4.pvalues['log_conc'])}; R² = {br(m4.rsquared, 2)})",
            f"- Pressupostos do M1: Shapiro-Wilk dos resíduos W = {br(diag['shapiro_W'], 3)}, "
            f"{fp(diag['shapiro_p'])}; Breusch-Pagan LM = {br(diag['breusch_pagan_LM'], 3)}, "
            f"{fp(diag['breusch_pagan_p'])} (erros robustos HC1). Saída completa: "
            "`04_modelos.txt`.", ""]

    # ---- 5. Posição do RN
    res = mods["residuos_M1"].set_index("sigla_uf")
    if FOCO in res.index:
        r = res.loc[FOCO]
        pos = list(res.index).index(FOCO) + 1
        c = rn.loc["concluintes_por_100_vinculos"]
        w = testes[testes["teste"].str.startswith("Wilcoxon")].iloc[0]
        cl, vi = rn.loc["concluintes_ti"], rn.loc["vinculos_ti"]
        sal = d23.loc["salario_medio_ti"]
        txt += [f"## 5. Posição do {FOCO}", "",
                f"- Concluintes por 100 empregos de TI: {br(c[f'valor_{FOCO}_{ano_ini}'], 1)} "
                f"({c[f'faixa_quartil_{ano_ini}']}) em {ano_ini} → "
                f"{br(c[f'valor_{FOCO}_{ano}'], 1)} ({c[f'faixa_quartil_{ano}']}, "
                f"{int(c[f'posicao_{ano}_de_27'])}º de 27) em {ano}; mediana das UFs em {ano}: "
                f"{br(c[f'mediana_UFs_{ano}'], 1)}.",
                f"- Concluintes de TI: {br(cl[f'valor_{FOCO}_{ano_ini}'], 0)} → "
                f"{br(cl[f'valor_{FOCO}_{ano}'], 0)} ({br(cl['variacao_pct'], 0)}%); empregos "
                f"formais de TI: {br(vi[f'valor_{FOCO}_{ano_ini}'], 0)} → "
                f"{br(vi[f'valor_{FOCO}_{ano}'], 0)} ({br(vi['variacao_pct'], 0)}%). Diferença "
                f"entre os dois crescimentos: {br(w['dif_rn'], 0)} p.p., a {int(w['pos_rn'])}ª maior entre as 27 UFs.",
                f"- Salário médio em TI: R$ {br(sal[f'valor_{FOCO}'], 2)} "
                f"({sal[f'faixa_quartil_{FOCO}']}; mediana das UFs R$ {br(sal['mediana'], 2)}).",
                f"- Modelo M1: empregos de TI/100k observados {br(r['vinculos_ti_100k'], 1)} x "
                f"previstos pelo volume de formação {br(r['previsto'], 1)}; resíduo "
                f"{br(r['residuo'], 3)} (≈ {br(100 * (np.exp(r['residuo']) - 1), 0)}% em relação "
                f"ao esperado), o {pos}º menor de {len(res)} UFs. Resíduo negativo = menos emprego "
                "formal do que o esperado para a formação (indício de baixa absorção local).", ""]

    # ---- 6. Robustez (preenchida quando calculada)
    if robustez:
        txt += robustez + [""]

    txt += ["## Arquivos gerados", "",
            f"- Tabelas: `01_descritiva_{ano_ini}.csv`, `01_descritiva_{ano}.csv`, "
            f"`01b_tabela_frequencias_*.csv`, `01c_rn_{ano_ini}_x_{ano}.csv`, "
            "`02_correlacoes.csv`, `03_correlacao_P1_por_ano.csv`, `04_modelos.txt`, "
            f"`05_residuos_M1_{ano}.csv`, `06_testes_hipotese.csv`, "
            f"`06b_crescimento_uf_{ano_ini}_{ano}.csv`",
            "- Gráficos: `g1_evolucao_rn_ne_br.png`, `g2_dispersao_formacao_emprego.png`, "
            "`g3_dispersao_formacao_salario.png`, `g4_concluintes_por_100_empregos.png`, "
            f"`g5_dispersao_mulheres.png`, `g6_boxplots_{ano}.png`, "
            f"`g7_boxplot_{ano_ini}_x_{ano}.png`, "
            f"`g8_histograma_concluintes_por_100_empregos_{ano}.png`",
            "", "> Correlação não implica causalidade. Os resultados indicam associação e "
            "indícios, não relações de causa e efeito."]
    (OUT / "relatorio.md").write_text("\n".join(txt), encoding="utf-8")


# ---------------------------------------------------------------------------
# 6. Robustez: todos os cursos x só presenciais (efeito do EAD)
# ---------------------------------------------------------------------------
NOMES_VERSAO = {"concluintes_ti": "todos os cursos (presencial + EAD)",
                "concluintes_ti_presencial": "só cursos presenciais"}


def numeros_chave(painel: pd.DataFrame, ano: int) -> dict:
    """Principais números de uma versão do painel (sem gravar arquivos)."""
    corte_a = painel[painel["ano"] == ano]
    c = correlacao(corte_a["concluintes_ti_100k"], corte_a["vinculos_ti_100k"])
    m = descritiva.medidas(descritiva.corte(painel, ano)["concluintes_por_100_vinculos"])
    cr = crescimento_uf(painel, config.ANO_INICIO, ano)
    w = stats.wilcoxon(cr["cresc_concluintes_pct"], cr["cresc_vinculos_pct"],
                       alternative="greater")
    return {
        "r_P1": c["pearson_r"], "p_P1": c["pearson_p"],
        "rn_c100": m[f"valor_{FOCO}"], "mediana_c100": m["mediana"],
        "q3_c100": m["q3"], "faixa_rn": m[f"faixa_quartil_{FOCO}"],
        "pos_rn": m[f"posicao_{FOCO}"],
        "rn_cresc_conc": cr.loc[FOCO, "cresc_concluintes_pct"],
        "rn_cresc_vinc": cr.loc[FOCO, "cresc_vinculos_pct"],
        "w_stat": w.statistic, "w_p": w.pvalue,
        "w_med_dif": cr["diferenca_pp"].median(),
    }


def secao_robustez(painel: pd.DataFrame, ano: int) -> list:
    import juntar_bases  # import tardio: só é preciso aqui e no modo --presencial

    col_a = config.COLUNA_FORMACAO
    col_b = ("concluintes_ti_presencial" if col_a == "concluintes_ti" else "concluintes_ti")
    print(f"Robustez: recalculando com {col_b}")
    a = numeros_chave(painel, ano)
    b = numeros_chave(juntar_bases.montar_painel(col_b), ano)
    ver = [NOMES_VERSAO.get(col_a, col_a), NOMES_VERSAO.get(col_b, col_b)]
    linhas = [
        [f"Correlação P1 ({ano}, Pearson r)",
         *(f"{br(x['r_P1'], 2)} ({fp(x['p_P1'])})" for x in (a, b))],
        [f"{FOCO}: concluintes por 100 empregos ({ano})",
         *(f"{br(x['rn_c100'], 1)} (mediana {br(x['mediana_c100'], 1)}, Q3 {br(x['q3_c100'], 1)})"
           for x in (a, b))],
        [f"{FOCO}: faixa de quartil e posição",
         *(f"{x['faixa_rn']} ({x['pos_rn']}º)" for x in (a, b))],
        [f"{FOCO}: crescimento concluintes x vínculos ({config.ANO_INICIO}-{ano})",
         *(f"{br(x['rn_cresc_conc'], 0)}% x {br(x['rn_cresc_vinc'], 0)}%" for x in (a, b))],
        ["Wilcoxon (H1: concluintes cresceram mais que empregos)",
         *(f"W = {br(x['w_stat'], 0)}; {fp(x['w_p'])}; dif. mediana {br(x['w_med_dif'], 1)} p.p."
           for x in (a, b))],
    ]
    return ["## 6. Robustez: efeito dos cursos EAD", "",
            "Os concluintes de cursos EAD são contados na UF registrada no Censo, o que pode "
            "inflar a formação de alguns estados. A tabela repete os principais números "
            "usando só os cursos presenciais (`python analise.py --presencial` gera a análise "
            "completa em `resultados/robustez_presencial/`).", ""] + \
        _tabela_md(["Medida", *ver], linhas)


def main() -> None:
    global OUT
    parser = argparse.ArgumentParser(description="Análise formação x mercado de TI")
    parser.add_argument("--presencial", action="store_true",
                        help="usa só concluintes de cursos presenciais e grava em "
                             "resultados/robustez_presencial/")
    args = parser.parse_args()

    if args.presencial:
        import juntar_bases
        painel = juntar_bases.montar_painel("concluintes_ti_presencial")
        OUT = config.RESULTADOS / "robustez_presencial"
        OUT.mkdir(parents=True, exist_ok=True)
    else:
        painel = pd.read_csv(config.ARQ_PAINEL)
    ano = int(painel["ano"].max())
    print(f"Painel: {len(painel)} linhas; ano de referência {ano}")

    desc = descritiva.executar(painel, config.ANO_INICIO, ano, OUT)
    corr = correlacoes(painel, ano)
    testes = testes_hipotese(painel, config.ANO_INICIO, ano)
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
    grafico_boxplots(painel, ano)
    grafico_boxplot_dois_anos(painel, config.ANO_INICIO, ano)
    grafico_histograma(painel, ano)

    coluna = "concluintes_ti_presencial" if args.presencial else config.COLUNA_FORMACAO
    robustez = None if args.presencial else secao_robustez(painel, ano)
    relatorio(painel, ano, desc, corr, testes, mods, robustez,
              versao=NOMES_VERSAO.get(coluna, coluna))
    print(f"OK: resultados em {OUT}")


if __name__ == "__main__":
    main()
