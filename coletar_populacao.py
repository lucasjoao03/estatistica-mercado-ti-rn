"""
Etapa 3 - População por UF e ano (IBGE) via Base dos Dados.

Usada só para normalizar os indicadores (por 100 mil habitantes), evitando
que estados grandes dominem as correlações.

Uso:
    python coletar_populacao.py
Saída:
    dados/processados/populacao_uf_ano.csv
"""
import pandas as pd

import config

QUERY = f"""
SELECT ano, sigla_uf, populacao
FROM `basedosdados.br_ibge_populacao.uf`
WHERE ano BETWEEN {config.ANO_INICIO} AND {config.ANO_FIM}
"""


def completar_anos(df: pd.DataFrame) -> pd.DataFrame:
    """Interpola linearmente anos sem estimativa (ex.: ano de Censo)."""
    anos = range(config.ANO_INICIO, config.ANO_FIM + 1)
    partes = []
    for uf, g in df.groupby("sigla_uf"):
        g = g.set_index("ano").reindex(anos)
        g["populacao"] = g["populacao"].interpolate(limit_direction="both")
        g["sigla_uf"] = uf
        partes.append(g.reset_index())
    return pd.concat(partes, ignore_index=True)


def main() -> None:
    import basedosdados as bd

    df = bd.read_sql(QUERY, billing_project_id=config.BILLING_PROJECT_ID)
    df["ano"] = df["ano"].astype(int)
    df = completar_anos(df)
    df.to_csv(config.ARQ_POP, index=False)
    print(f"OK: {len(df)} linhas salvas em {config.ARQ_POP}")


if __name__ == "__main__":
    main()
