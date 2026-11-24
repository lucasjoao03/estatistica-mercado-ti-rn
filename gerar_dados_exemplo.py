"""
Gera dados FICTÍCIOS no mesmo formato das etapas de coleta, só para testar o
pipeline (juntar_bases.py e analise.py) antes de ter os dados reais.

NÃO use estes números no trabalho.

Uso:
    python gerar_dados_exemplo.py            # não sobrescreve dados reais
    python gerar_dados_exemplo.py --forcar   # sobrescreve
"""
import sys

import numpy as np
import pandas as pd

import config

rng = np.random.default_rng(42)

# População aproximada (milhões) só para ter ordens de grandeza plausíveis
POP = {"AC": .9, "AL": 3.3, "AM": 4.1, "AP": .8, "BA": 14.1, "CE": 8.8, "DF": 2.8,
       "ES": 3.8, "GO": 7.1, "MA": 6.8, "MG": 20.5, "MS": 2.8, "MT": 3.7, "PA": 8.1,
       "PB": 4.0, "PE": 9.1, "PI": 3.3, "PR": 11.4, "RJ": 16.1, "RN": 3.3, "RO": 1.6,
       "RR": .6, "RS": 10.9, "SC": 7.6, "SE": 2.2, "SP": 44.4, "TO": 1.5}


def main() -> None:
    reais = [p for p in (config.ARQ_RAIS, config.ARQ_INEP, config.ARQ_POP) if p.exists()]
    if reais and "--forcar" not in sys.argv:
        raise SystemExit(f"Já existem arquivos em {config.DADOS_PROC}. Use --forcar.")

    anos = range(config.ANO_INICIO, config.ANO_FIM + 1)
    # "Intensidade tecnológica" latente de cada UF
    intens = {uf: rng.normal(0, 0.45) + (0.5 if uf in ("SP", "DF", "SC", "PR", "RS") else 0)
              for uf in config.UFS}
    rais, inep, pop = [], [], []
    for uf in config.UFS:
        for i, ano in enumerate(anos):
            p = POP[uf] * 1e6 * (1 + 0.006 * i)
            conc_100k = np.exp(2.6 + 0.6 * intens[uf] + 0.03 * i + rng.normal(0, .12))
            vinc_100k = np.exp(5.2 + 0.9 * intens[uf] + 0.05 * i + rng.normal(0, .10))
            conc, vinc = int(conc_100k * p / 1e5), int(vinc_100k * p / 1e5)
            pop.append({"ano": ano, "sigla_uf": uf, "populacao": int(p)})
            inep.append({"ano": ano, "sigla_uf": uf, "cursos_ti": int(conc / 25) + 3,
                         "ingressantes_ti": conc * 3, "matriculas_ti": conc * 7,
                         "concluintes_ti": conc,
                         "concluintes_ti_fem": int(conc * rng.uniform(.12, .2)),
                         "concluintes_ti_presencial": int(conc * .6),
                         "concluintes_ti_publica": int(conc * .3)})
            sal = 4200 * np.exp(0.25 * intens[uf] + 0.04 * i + rng.normal(0, .06))
            rais.append({"ano": ano, "sigla_uf": uf, "vinculos_total": int(p * .25),
                         "vinculos_ti": vinc,
                         "vinculos_ti_fem": int(vinc * rng.uniform(.15, .25)),
                         "salario_medio_ti": sal, "salario_mediano_ti": sal * .8,
                         "salario_medio_geral": 2700 * (1 + 0.04 * i)})

    pd.DataFrame(rais).to_csv(config.ARQ_RAIS, index=False)
    pd.DataFrame(inep).to_csv(config.ARQ_INEP, index=False)
    pd.DataFrame(pop).to_csv(config.ARQ_POP, index=False)
    print("Dados FICTÍCIOS gerados em", config.DADOS_PROC)


if __name__ == "__main__":
    main()
