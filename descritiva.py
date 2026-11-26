"""
Estatística descritiva entre as 27 UFs (usado por analise.py).

Para cada indicador e ano de referência calcula:
  - n, média, mediana, desvio-padrão amostral (ddof=1), variância, CV (%),
    mínimo/máximo (com a UF), amplitude
  - quartis Q1, Q2, Q3 (pandas.quantile, método "linear") e IQR
  - assimetria (scipy.stats.skew, bias=False) e classificação textual
  - outliers pelo critério de Tukey (fora de [Q1 - 1,5·IQR ; Q3 + 1,5·IQR])
  - moda por classes: nº de classes pela regra de Sturges, classes de mesma
    amplitude, classe modal e moda de Czuber
  - valor do RN, posição no ranking (1 = maior) e faixa de quartil

Saídas (pasta passada em `out`):
  01_descritiva_<ano>.csv
  01b_tabela_frequencias_<indicador>_<ano>.csv
  01c_rn_<ano_ini>_x_<ano_fim>.csv
"""
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

import config

FOCO = config.UF_FOCO

INDICADORES = [
    "concluintes_ti_100k", "vinculos_ti_100k", "concluintes_por_100_vinculos",
    "salario_medio_ti", "salario_relativo_ti", "participacao_ti_emprego",
    "pct_fem_concluintes_ti", "pct_fem_vinculos_ti",
]

# Indicadores com tabela de frequências exportada
INDICADORES_FREQ = [
    "concluintes_ti_100k", "vinculos_ti_100k",
    "concluintes_por_100_vinculos", "salario_medio_ti",
]

ROTULOS = {
    "concluintes_ti": "Concluintes de TI (nº)",
    "vinculos_ti": "Empregos formais de TI (nº)",
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

FAIXAS = ["abaixo de Q1", "entre Q1 e a mediana", "entre a mediana e Q3", "acima de Q3"]


# ---------------------------------------------------------------------------
# Funções básicas
# ---------------------------------------------------------------------------
def classificar_assimetria(g: float) -> str:
    a = abs(g)
    if a < 0.5:
        return "simétrica"
    lado = "positiva (cauda à direita)" if g > 0 else "negativa (cauda à esquerda)"
    return f"{'moderada' if a < 1 else 'forte'} {lado}"


def faixa_quartil(v: float, q1: float, q2: float, q3: float) -> str:
    if v < q1:
        return FAIXAS[0]
    if v < q2:
        return FAIXAS[1]
    if v <= q3:
        return FAIXAS[2]
    return FAIXAS[3]


def classes_sturges(s: pd.Series) -> tuple[int, float, np.ndarray]:
    """k = ceil(1 + 3,322·log10(n)); h = (máx - mín)/k; devolve (k, h, limites)."""
    n = s.count()
    k = math.ceil(1 + 3.322 * math.log10(n))
    mn, mx = s.min(), s.max()
    h = (mx - mn) / k
    limites = mn + h * np.arange(k + 1)
    limites[-1] = mx  # evita erro de ponto flutuante no último limite
    return k, h, limites


def tabela_frequencias(s: pd.Series) -> pd.DataFrame:
    """Classes [Li, Ls) de mesma amplitude; a última classe inclui o máximo."""
    s = s.dropna()
    k, h, lim = classes_sturges(s)
    idx = np.clip(np.searchsorted(lim, s.values, side="right") - 1, 0, k - 1)
    freq = np.bincount(idx, minlength=k)
    ufs = [", ".join(sorted(s.index[idx == i])) for i in range(k)]
    n = freq.sum()
    return pd.DataFrame({
        "classe": [f"{lim[i]:.2f} ⊢ {lim[i + 1]:.2f}" for i in range(k)],
        "limite_inferior": lim[:-1],
        "limite_superior": lim[1:],
        "ponto_medio": (lim[:-1] + lim[1:]) / 2,
        "freq_absoluta": freq,
        "freq_relativa_pct": 100 * freq / n,
        "freq_acumulada": np.cumsum(freq),
        "freq_acumulada_pct": 100 * np.cumsum(freq) / n,
        "ufs": ufs,
    })


def moda_czuber(tab: pd.DataFrame) -> dict:
    """Mo = Li + d1/(d1 + d2)·h, com d1 = f_modal - f_anterior e d2 = f_modal - f_posterior."""
    f = tab["freq_absoluta"].to_numpy()
    i = int(np.argmax(f))  # em empate, fica a primeira classe de maior frequência
    f_ant = f[i - 1] if i > 0 else 0
    f_pos = f[i + 1] if i < len(f) - 1 else 0
    d1, d2 = f[i] - f_ant, f[i] - f_pos
    li = tab["limite_inferior"].iloc[i]
    h = tab["limite_superior"].iloc[i] - li
    mo = li + (d1 / (d1 + d2)) * h if (d1 + d2) > 0 else li + h / 2
    return {"classe_modal": tab["classe"].iloc[i], "classe_modal_li": li,
            "classe_modal_ls": li + h, "freq_classe_modal": int(f[i]),
            "moda_czuber": mo, "n_classes_sturges": len(f), "amplitude_classe": h,
            "n_classes_modais": int((f == f[i]).sum())}


def medidas(s: pd.Series) -> dict:
    """Todas as medidas de um indicador (índice = sigla da UF)."""
    s = s.dropna()
    q1, q2, q3 = (s.quantile(q, interpolation="linear") for q in (0.25, 0.5, 0.75))
    iqr = q3 - q1
    lim_inf, lim_sup = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    fora = s[(s < lim_inf) | (s > lim_sup)].sort_values()
    g = stats.skew(s, bias=False)
    media, dp = s.mean(), s.std(ddof=1)
    d = {
        "n": int(s.count()), "media": media, "mediana": s.median(),
        "desvio_padrao": dp, "variancia": s.var(ddof=1), "cv_pct": 100 * dp / media,
        "minimo": s.min(), "uf_minimo": s.idxmin(),
        "maximo": s.max(), "uf_maximo": s.idxmax(), "amplitude": s.max() - s.min(),
        "q1": q1, "q2": q2, "q3": q3, "iqr": iqr,
        "limite_inferior_tukey": lim_inf, "limite_superior_tukey": lim_sup,
        "outliers_tukey": ", ".join(fora.index) if len(fora) else "nenhum",
        "assimetria": g, "classificacao_assimetria": classificar_assimetria(g),
    }
    d.update(moda_czuber(tabela_frequencias(s)))
    if FOCO in s.index:
        v = s.loc[FOCO]
        d[f"valor_{FOCO}"] = v
        d[f"posicao_{FOCO}"] = int(s.rank(ascending=False, method="min").loc[FOCO])
        d[f"faixa_quartil_{FOCO}"] = faixa_quartil(v, q1, q2, q3)
    return d


def corte(painel: pd.DataFrame, ano: int) -> pd.DataFrame:
    d = painel[painel["ano"] == ano].set_index("sigla_uf")
    return d[d.index.isin(config.UFS)]


# ---------------------------------------------------------------------------
# Tabelas exportadas
# ---------------------------------------------------------------------------
COLUNAS_SAIDA = {
    "indicador": "indicador", "variavel": "variavel", "n": "n",
    "media": "media", "mediana": "mediana", "moda_czuber": "moda_czuber",
    "classe_modal": "classe_modal", "freq_classe_modal": "freq_classe_modal",
    "n_classes_sturges": "n_classes_sturges", "amplitude_classe": "amplitude_classe",
    "desvio_padrao": "desvio_padrao", "variancia": "variancia", "cv_pct": "cv_pct",
    "minimo": "minimo", "uf_minimo": "uf_minimo", "maximo": "maximo",
    "uf_maximo": "uf_maximo", "amplitude": "amplitude",
    "q1": "q1", "q2": "q2_mediana", "q3": "q3", "iqr": "amplitude_interquartil",
    "limite_inferior_tukey": "limite_inferior_tukey",
    "limite_superior_tukey": "limite_superior_tukey", "outliers_tukey": "outliers_tukey",
    "assimetria": "assimetria", "classificacao_assimetria": "classificacao_assimetria",
    f"valor_{FOCO}": f"valor_{FOCO}", f"posicao_{FOCO}": f"posicao_{FOCO}_de_27",
    f"faixa_quartil_{FOCO}": f"faixa_quartil_{FOCO}",
}


def descritiva_ano(painel: pd.DataFrame, ano: int, out: Path) -> pd.DataFrame:
    """Tabela descritiva completa de um ano (uma linha por indicador)."""
    d = corte(painel, ano)
    linhas = []
    for col in INDICADORES:
        linhas.append({"indicador": ROTULOS.get(col, col), "variavel": col,
                       **medidas(d[col])})
    tab = pd.DataFrame(linhas)
    tab = tab[[c for c in COLUNAS_SAIDA if c in tab]].rename(columns=COLUNAS_SAIDA)
    tab.round(2).to_csv(out / f"01_descritiva_{ano}.csv", index=False)
    return tab.set_index("variavel")


def salvar_frequencias(painel: pd.DataFrame, ano: int, out: Path) -> dict:
    d = corte(painel, ano)
    tabs = {}
    for col in INDICADORES_FREQ:
        tab = tabela_frequencias(d[col])
        tab.round(2).to_csv(out / f"01b_tabela_frequencias_{col}_{ano}.csv", index=False)
        tabs[col] = tab
    return tabs


def rn_dois_anos(painel: pd.DataFrame, ano_ini: int, ano_fim: int, out: Path) -> pd.DataFrame:
    """Valor, faixa de quartil e posição do RN nos dois anos de referência."""
    linhas = []
    for col in ["concluintes_ti", "vinculos_ti"] + INDICADORES:
        r = {"indicador": ROTULOS.get(col, col), "variavel": col}
        for a in (ano_ini, ano_fim):
            m = medidas(corte(painel, a)[col])
            r[f"valor_{FOCO}_{a}"] = m[f"valor_{FOCO}"]
            r[f"mediana_UFs_{a}"] = m["mediana"]
            r[f"faixa_quartil_{a}"] = m[f"faixa_quartil_{FOCO}"]
            r[f"posicao_{a}_de_27"] = m[f"posicao_{FOCO}"]
        r["variacao_pct"] = 100 * (r[f"valor_{FOCO}_{ano_fim}"] / r[f"valor_{FOCO}_{ano_ini}"] - 1)
        linhas.append(r)
    tab = pd.DataFrame(linhas)
    ordem = ["indicador", "variavel",
             f"valor_{FOCO}_{ano_ini}", f"valor_{FOCO}_{ano_fim}", "variacao_pct",
             f"mediana_UFs_{ano_ini}", f"mediana_UFs_{ano_fim}",
             f"faixa_quartil_{ano_ini}", f"faixa_quartil_{ano_fim}",
             f"posicao_{ano_ini}_de_27", f"posicao_{ano_fim}_de_27"]
    tab = tab[ordem]
    tab.round(2).to_csv(out / f"01c_rn_{ano_ini}_x_{ano_fim}.csv", index=False)
    return tab.set_index("variavel")


def executar(painel: pd.DataFrame, ano_ini: int, ano_fim: int, out: Path) -> dict:
    return {
        "desc": {a: descritiva_ano(painel, a, out) for a in (ano_ini, ano_fim)},
        "freq": {a: salvar_frequencias(painel, a, out) for a in (ano_ini, ano_fim)},
        "rn": rn_dois_anos(painel, ano_ini, ano_fim, out),
    }
