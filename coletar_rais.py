"""
Etapa 1 - Coleta da RAIS (MTE) via Base dos Dados (BigQuery).

A agregação por UF e ano é feita DENTRO do BigQuery, então só uma tabela
pequena (27 UFs x N anos) é baixada para o seu computador.

Pré-requisitos:
    pip install basedosdados
    Ter um projeto no Google Cloud e definir BILLING_PROJECT_ID em config.py
    (o nível gratuito do BigQuery cobre esta consulta com folga).

Uso:
    python coletar_rais.py
Saída:
    dados/processados/rais_ti_uf_ano.csv
"""
import config

CBOS_SQL = ", ".join(f"'{c}'" for c in config.CBO_TI)

# Confira os nomes das colunas no dicionário da tabela em
# https://basedosdados.org/dataset/3e7c4d58-96ba-448e-b053-d385a829ef00
QUERY = f"""
WITH base AS (
  SELECT
    ano,
    sigla_uf,
    SUBSTR(CAST(cbo_2002 AS STRING), 1, 4) IN ({CBOS_SQL}) AS eh_ti,
    CAST(sexo AS STRING) AS sexo,
    SAFE_CAST(valor_remuneracao_media AS FLOAT64) AS remuneracao
  FROM `basedosdados.br_me_rais.microdados_vinculos`
  WHERE ano BETWEEN {config.ANO_INICIO} AND {config.ANO_FIM}
    AND CAST(vinculo_ativo_3112 AS STRING) = '1'
)
SELECT
  ano,
  sigla_uf,
  COUNT(*)                                    AS vinculos_total,
  COUNTIF(eh_ti)                              AS vinculos_ti,
  COUNTIF(eh_ti AND sexo = '2')               AS vinculos_ti_fem,
  AVG(IF(eh_ti AND remuneracao > 0, remuneracao, NULL)) AS salario_medio_ti,
  APPROX_QUANTILES(IF(eh_ti AND remuneracao > 0, remuneracao, NULL), 100)[OFFSET(50)]
                                              AS salario_mediano_ti,
  AVG(IF(remuneracao > 0, remuneracao, NULL)) AS salario_medio_geral
FROM base
GROUP BY ano, sigla_uf
ORDER BY ano, sigla_uf
"""


def main() -> None:
    import basedosdados as bd  # import aqui para o resto do projeto rodar sem ele

    print("Consultando a RAIS no BigQuery (pode levar alguns minutos)...")
    df = bd.read_sql(QUERY, billing_project_id=config.BILLING_PROJECT_ID)

    df["ano"] = df["ano"].astype(int)
    df["sigla_uf"] = df["sigla_uf"].str.upper()
    df.to_csv(config.ARQ_RAIS, index=False)
    print(f"OK: {len(df)} linhas salvas em {config.ARQ_RAIS}")


if __name__ == "__main__":
    main()
