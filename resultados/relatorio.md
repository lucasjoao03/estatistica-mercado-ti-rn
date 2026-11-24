# Resultados automáticos - Formação x Mercado de TI (2015-2023)

Painel: 27 UFs x 9 anos = 243 observações. Corte transversal de referência: 2023.

## Correlações

- **P1 Formação x emprego**
  - 2023: r = 0.95 (muito forte, significativa, p = 0.000); ρ = 0.88; n = 27
  - painel: r = 0.45 (moderada, significativa, p = 0.000); ρ = 0.70; n = 243
- **P2 Formação x salário médio TI**
  - 2023: r = 0.85 (muito forte, significativa, p = 0.000); ρ = 0.73; n = 27
  - painel: r = 0.78 (muito forte, significativa, p = 0.000); ρ = 0.60; n = 243
- **P2 Formação x salário relativo TI**
  - 2023: r = 0.36 (moderada, não significativa, p = 0.066); ρ = 0.67; n = 27
  - painel: r = 0.24 (fraca, significativa, p = 0.000); ρ = 0.35; n = 243
- **P3 Formação (t-1) x emprego (t)**
  - 2023: r = 0.95 (muito forte, significativa, p = 0.000); ρ = 0.91; n = 27
  - painel: r = 0.43 (moderada, significativa, p = 0.000); ρ = 0.67; n = 216
- **P3 Crescimento formação x crescimento emprego**
  - 2023: r = 0.12 (fraca, não significativa, p = 0.564); ρ = -0.23; n = 27
  - painel: r = 0.01 (desprezível, não significativa, p = 0.933); ρ = 0.18; n = 216
- **P4 % mulheres formação x mercado**
  - 2023: r = 0.60 (forte, significativa, p = 0.001); ρ = 0.64; n = 27
  - painel: r = 0.06 (desprezível, não significativa, p = 0.330); ρ = 0.22; n = 243

## Regressões (coeficiente = elasticidade)

- **M1** (corte 2023): +1% em concluintes/100k → +1.29% em empregos/100k (p = 0.000; R² = 0.84)
- **M2** (painel, formação t-1, efeito de ano): +1.15 (p = 0.000; R² = 0.48)
- **M3** (efeitos fixos UF e ano): +0.03 (p = 0.891) - mede se, DENTRO de um mesmo estado, anos com mais formação antecedem anos com mais emprego
- **M4** (salário x formação, 2023): +0.35 (p = 0.000; R² = 0.71)

### Pressupostos do M1
- Normalidade dos resíduos (Shapiro-Wilk): W = 0.961, p = 0.389
- Homocedasticidade (Breusch-Pagan): LM = 0.037, p = 0.847 (erros robustos HC1 já usados)

## Posição do RN

- Concluintes de TI/100k: 25.4; empregos de TI/100k observados: 114.9; previstos pelo M1: 182.1
- Resíduo: -0.461 (≈ -37% em relação ao esperado) - 3º menor de 27 UFs
- Resíduo negativo: o estado tem MENOS emprego formal em TI do que o esperado para o volume de formação (indício de que o mercado local não absorve todos os formados). Positivo: o contrário.

### Indicadores do RN em 2023 (posição entre as 27 UFs)

- Concluintes de TI por 100 mil hab.: 25.43 (13º; média das UFs 30.38)
- Empregos formais de TI por 100 mil hab.: 114.90 (20º; média das UFs 256.11)
- Salário médio em TI (R$): 4660.20 (24º; média das UFs 6106.72)
- Salário TI / salário médio geral: 1.48 (22º; média das UFs 1.72)
- Concluintes por 100 empregos de TI: 22.13 (4º; média das UFs 14.79)
- % do emprego formal que é TI: 0.55 (18º; média das UFs 0.88)
- % mulheres entre concluintes de TI: 13.69 (20º; média das UFs 15.14)
- % mulheres nos empregos de TI: 17.02 (22º; média das UFs 18.81)

## Gráficos

- g1_evolucao_rn_ne_br.png
- g2_dispersao_formacao_emprego.png
- g3_dispersao_formacao_salario.png
- g4_concluintes_por_100_empregos.png
- g5_dispersao_mulheres.png

> Lembrete: correlação não implica causalidade. Os resultados indicam associação entre formação e mercado, não que um cause o outro.