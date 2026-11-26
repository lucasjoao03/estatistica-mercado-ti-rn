"""
Etapa 4 - Junção das bases (chave: sigla_uf + ano) e criação dos indicadores.

Entrada:
    dados/processados/rais_ti_uf_ano.csv
    dados/processados/inep_ti_uf_ano.csv
    dados/processados/populacao_uf_ano.csv
Saída:
    dados/processados/painel_uf_ano.csv
"""
import pandas as pd

import config

CHAVE = ["sigla_uf", "ano"]


def carregar() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rais = pd.read_csv(config.ARQ_RAIS)
    inep = pd.read_csv(config.ARQ_INEP)
    pop = pd.read_csv(config.ARQ_POP)
    bases = {"RAIS": rais, "INEP": inep, "População": pop}
    for nome, df in bases.items():
        df["sigla_uf"] = df["sigla_uf"].str.upper().str.strip()
        df["ano"] = df["ano"].astype(int)
        # Descarta linhas cuja UF não é uma das 27 (ex.: "IGNORADO" na RAIS)
        invalidas = ~df["sigla_uf"].isin(config.UFS)
        if invalidas.any():
            descr = ", ".join(f"{u}/{a}" for u, a in
                              df.loc[invalidas, ["sigla_uf", "ano"]].itertuples(index=False))
            print(f"  {nome}: {int(invalidas.sum())} linha(s) com UF fora das 27 "
                  f"descartada(s) ({descr})")
        bases[nome] = df[~invalidas].copy()
    return bases["RAIS"], bases["INEP"], bases["População"]


def checar_juncao(rais: pd.DataFrame, inep: pd.DataFrame) -> None:
    """Mostra quais combinações UF-ano existem só em uma das bases."""
    teste = rais[CHAVE].merge(inep[CHAVE], on=CHAVE, how="outer", indicator=True)
    so_rais = teste[teste["_merge"] == "left_only"]
    so_inep = teste[teste["_merge"] == "right_only"]
    print(f"  Combinações UF-ano: RAIS={len(rais)}  INEP={len(inep)}  "
          f"em comum={int((teste['_merge'] == 'both').sum())}")
    if len(so_rais):
        print(f"  Só na RAIS: {so_rais[CHAVE].values.tolist()[:10]}")
    if len(so_inep):
        print(f"  Só no INEP: {so_inep[CHAVE].values.tolist()[:10]}")


def criar_indicadores(df: pd.DataFrame) -> pd.DataFrame:
    p100k = df["populacao"] / 100_000

    # Formação
    df["concluintes_ti_100k"] = df["concluintes_ti"] / p100k
    df["matriculas_ti_100k"] = df["matriculas_ti"] / p100k
    df["pct_fem_concluintes_ti"] = 100 * df["concluintes_ti_fem"] / df["concluintes_ti"]

    # Mercado
    df["vinculos_ti_100k"] = df["vinculos_ti"] / p100k
    df["participacao_ti_emprego"] = 100 * df["vinculos_ti"] / df["vinculos_total"]
    df["salario_relativo_ti"] = df["salario_medio_ti"] / df["salario_medio_geral"]
    df["pct_fem_vinculos_ti"] = 100 * df["vinculos_ti_fem"] / df["vinculos_ti"]

    # Relação formação x mercado: formados no ano para cada 100 empregos de TI
    df["concluintes_por_100_vinculos"] = 100 * df["concluintes_ti"] / df["vinculos_ti"]

    # Defasagem e crescimento (dentro de cada UF)
    df = df.sort_values(CHAVE)
    g = df.groupby("sigla_uf")
    df["concluintes_ti_100k_lag1"] = g["concluintes_ti_100k"].shift(1)
    df["cresc_vinculos_ti_pct"] = 100 * g["vinculos_ti"].pct_change()
    df["cresc_concluintes_ti_pct"] = 100 * g["concluintes_ti"].pct_change()
    return df


def main() -> None:
    rais, inep, pop = carregar()
    checar_juncao(rais, inep)

    painel = (
        rais.merge(inep, on=CHAVE, how="inner", validate="one_to_one")
            .merge(pop, on=CHAVE, how="left", validate="one_to_one")
    )
    faltando_pop = painel["populacao"].isna().sum()
    if faltando_pop:
        print(f"  ATENÇÃO: {faltando_pop} linhas sem população")

    painel = criar_indicadores(painel)
    painel.to_csv(config.ARQ_PAINEL, index=False)
    print(f"OK: painel com {len(painel)} linhas "
          f"({painel['sigla_uf'].nunique()} UFs x {painel['ano'].nunique()} anos) "
          f"salvo em {config.ARQ_PAINEL}")


if __name__ == "__main__":
    main()
