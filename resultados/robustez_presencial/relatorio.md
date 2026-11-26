# Resultados automáticos - Formação x Mercado de TI (2015-2023)

Gerado por `analise.py`. Segue o fluxo PROBLEMA → DADOS → ANÁLISE ESTATÍSTICA → DIÁLOGO → CONTRIBUIÇÕES; o diálogo com a literatura e as contribuições estão em `docs/estrutura_trabalho.md`.

## 1. Dados

- **Fontes secundárias**: INEP - Censo da Educação Superior (cursos da área CINE 06, Computação e TIC); MTE - RAIS Vínculos (vínculos ativos em 31/12 nas CBOs 1425, 2122, 2123, 2124, 3171, 3172); IBGE - estimativas de população. RAIS e população obtidas via Base dos Dados.
- **Período**: 2015 a 2023; **painel**: 27 UFs x 9 anos = 243 observações.
- **Junção**: chave `sigla_uf + ano` (RAIS x INEP por junção interna, população por junção à esquerda); linhas com UF fora das 27 (ex.: "IGNORADO" na RAIS) são descartadas.
- **Cortes transversais de referência**: 2015 e 2023 (n = 27 UFs cada).
- **Formação (concluintes) considerada**: só cursos presenciais.

## 2. Estatística descritiva

### 2.1 Resumo entre as 27 UFs (2023)

| Indicador | Média (x̄) | Mediana (x̃) | Moda (Czuber) | s | CV (%) | Q1 | Q3 | RN | Faixa do RN (posição) |
|---|---|---|---|---|---|---|---|---|---|
| Concluintes de TI por 100 mil hab. | 12,47 | 10,54 | 9,16 | 10,00 | 80,2 | 6,93 | 12,85 | 12,41 | entre a mediana e Q3 (9º) |
| Empregos formais de TI por 100 mil hab. | 256,11 | 152,62 | 159,68 | 256,19 | 100,0 | 111,56 | 313,27 | 114,90 | entre Q1 e a mediana (20º) |
| Concluintes por 100 empregos de TI | 6,24 | 6,03 | 4,23 | 2,78 | 44,6 | 3,84 | 7,79 | 10,80 | acima de Q3 (2º) |
| Salário médio em TI (R$) | 6.106,72 | 5.678,75 | 5.127,88 | 1.536,54 | 25,2 | 5.086,21 | 6.860,02 | 4.660,20 | abaixo de Q1 (24º) |
| Salário TI / salário médio geral | 1,72 | 1,68 | 1,51 | 0,27 | 15,5 | 1,50 | 1,91 | 1,48 | abaixo de Q1 (22º) |
| % do emprego formal que é TI | 0,88 | 0,67 | 0,53 | 0,55 | 62,1 | 0,52 | 1,11 | 0,55 | entre Q1 e a mediana (18º) |
| % mulheres entre concluintes de TI | 15,14 | 14,63 | 14,37 | 2,39 | 15,8 | 13,69 | 16,74 | 13,69 | entre Q1 e a mediana (20º) |
| % mulheres nos empregos de TI | 18,81 | 19,09 | 20,06 | 2,65 | 14,1 | 17,55 | 20,41 | 17,02 | abaixo de Q1 (22º) |

Tabela completa (variância, amplitude, IQR, assimetria, outliers, classe modal): `01_descritiva_2023.csv` (e `01_descritiva_2015.csv`). Posição: 1º = maior valor.

### 2.2 RN: 2015 x 2023

| Indicador | RN 2015 | RN 2023 | Variação (%) | Faixa 2015 | Faixa 2023 | Posição |
|---|---|---|---|---|---|---|
| Concluintes de TI (nº) | 251 | 410 | 63,3% | entre Q1 e a mediana | entre a mediana e Q3 | 20º → 14º |
| Empregos formais de TI (nº) | 2.661 | 3.795 | 42,6% | entre Q1 e a mediana | entre Q1 e a mediana | 18º → 19º |
| Concluintes de TI por 100 mil hab. | 7,29 | 12,41 | 70,2% | abaixo de Q1 | entre a mediana e Q3 | 23º → 9º |
| Empregos formais de TI por 100 mil hab. | 77,31 | 114,90 | 48,6% | entre Q1 e a mediana | entre Q1 e a mediana | 18º → 20º |
| Concluintes por 100 empregos de TI | 9,43 | 10,80 | 14,5% | entre Q1 e a mediana | acima de Q3 | 15º → 2º |
| Salário médio em TI (R$) | 3.253,73 | 4.660,20 | 43,2% | abaixo de Q1 | abaixo de Q1 | 22º → 24º |
| Salário TI / salário médio geral | 1,60 | 1,48 | -7,8% | entre Q1 e a mediana | abaixo de Q1 | 18º → 22º |
| % do emprego formal que é TI | 0,44 | 0,55 | 25,4% | entre Q1 e a mediana | entre Q1 e a mediana | 20º → 18º |
| % mulheres entre concluintes de TI | 10,53 | 13,69 | 30,1% | abaixo de Q1 | entre Q1 e a mediana | 25º → 20º |
| % mulheres nos empregos de TI | 16,42 | 17,02 | 3,7% | abaixo de Q1 | abaixo de Q1 | 24º → 22º |

### 2.3 Forma das distribuições e escolha da medida de referência

Em 7 dos 8 indicadores a média supera a mediana, sinal de assimetria à direita causada por poucos estados muito acima dos demais. Os casos mais marcantes: Empregos formais de TI por 100 mil hab.: média 256,11 x mediana 152,62 (CV 100%, outliers SC, SP, DF); Concluintes de TI por 100 mil hab.: média 12,47 x mediana 10,54 (CV 80%, outliers SP, DF); Salário médio em TI (R$): média 6.106,72 x mediana 5.678,75 (CV 25%, outliers SP, DF); % do emprego formal que é TI: média 0,88 x mediana 0,67 (CV 62%, outliers DF, SP). A assimetria é forte (|g| ≥ 1) em 5 indicadores e o teste de Shapiro-Wilk rejeita a normalidade em 5 dos 8. Como a média é puxada pelos polos (DF, SC, SP), a **mediana** e os **quartis** são as referências mais adequadas para situar o RN, e os testes de comparação usados são não paramétricos.

Notas de método: quartis por `pandas.quantile` (interpolação linear); moda de Czuber calculada sobre classes de Sturges (k = 6 para n = 27); outliers pelo critério de Tukey (1,5·IQR). Tabelas de frequências: `01b_tabela_frequencias_*.csv`.

## 3. Testes de hipótese

### 3.1 Normalidade (Shapiro-Wilk, 2023)

H0: os valores das 27 UFs vêm de uma distribuição normal.

| Indicador | W | p-valor | Decisão (5%) |
|---|---|---|---|
| Concluintes de TI por 100 mil hab. | 0,645 | p < 0,001 | rejeita H0 |
| Empregos formais de TI por 100 mil hab. | 0,713 | p < 0,001 | rejeita H0 |
| Concluintes por 100 empregos de TI | 0,923 | p = 0,046 | rejeita H0 |
| Salário médio em TI (R$) | 0,872 | p = 0,003 | rejeita H0 |
| Salário TI / salário médio geral | 0,955 | p = 0,282 | não rejeita H0 |
| % do emprego formal que é TI | 0,838 | p < 0,001 | rejeita H0 |
| % mulheres entre concluintes de TI | 0,969 | p = 0,584 | não rejeita H0 |
| % mulheres nos empregos de TI | 0,936 | p = 0,099 | não rejeita H0 |

### 3.2 Comparações (não paramétricas)

- **Wilcoxon pareado: crescimento % concluintes x vínculos de TI (2015-2023)**
  - H0: mediana da diferença (cresc. concluintes - cresc. vínculos) <= 0; H1: os concluintes cresceram mais que os empregos (mediana > 0)
  - estatística = 13,0; p = 1,000; n = 27 → **não rejeita H0**
  - no conjunto das UFs não há evidência de que a formação tenha crescido mais que o emprego. Mediana do cresc. dos concluintes -18,2% x vínculos 52,3%; diferença mediana -72,0 p.p.; em 3 de 27 UFs a formação cresceu mais que o emprego. RN: 63% x 43% (diferença de 21 p.p., 2ª maior entre as UFs)
- **Mann-Whitney U: Concluintes por 100 empregos de TI, Nordeste x demais UFs (2023)**
  - H0: as distribuições do Nordeste e das demais UFs são iguais; H1: o Nordeste forma mais em relação ao emprego (valores maiores)
  - estatística = 127,0; p = 0,010; n = 27 → **rejeita H0**
  - mediana Nordeste (n=9) 7,89 x demais (n=18) 5,33; há evidência de que o Nordeste tem valores maiores
- **Mann-Whitney U: Salário médio em TI (R$), Nordeste x demais UFs (2023)**
  - H0: as distribuições do Nordeste e das demais UFs são iguais; H1: o Nordeste paga menos em TI (valores menores)
  - estatística = 26,0; p = 0,003; n = 27 → **rejeita H0**
  - mediana Nordeste (n=9) 4.989 x demais (n=18) 6.334; há evidência de que o Nordeste tem valores menores

### 3.3 Correlações (Pearson e Spearman)

- **P1 Formação x emprego**
  - 2023: r = 0,90 (muito forte, significativa, p < 0,001); ρ de Spearman = 0,82 (p < 0,001); n = 27
  - painel: r = 0,40 (moderada, significativa, p < 0,001); ρ de Spearman = 0,59 (p < 0,001); n = 243
- **P2 Formação x salário médio TI**
  - 2023: r = 0,76 (muito forte, significativa, p < 0,001); ρ de Spearman = 0,61 (p < 0,001); n = 27
  - painel: r = 0,63 (forte, significativa, p < 0,001); ρ de Spearman = 0,33 (p < 0,001); n = 243
- **P2 Formação x salário relativo TI**
  - 2023: r = 0,29 (fraca, não significativa, p = 0,139); ρ de Spearman = 0,59 (p = 0,001); n = 27
  - painel: r = 0,29 (fraca, significativa, p < 0,001); ρ de Spearman = 0,40 (p < 0,001); n = 243
- **P3 Formação (t-1) x emprego (t)**
  - 2023: r = 0,91 (muito forte, significativa, p < 0,001); ρ de Spearman = 0,77 (p < 0,001); n = 27
  - painel: r = 0,37 (moderada, significativa, p < 0,001); ρ de Spearman = 0,56 (p < 0,001); n = 216
- **P3 Crescimento formação x crescimento emprego**
  - 2023: r = -0,02 (desprezível, não significativa, p = 0,927); ρ de Spearman = -0,23 (p = 0,246); n = 27
  - painel: r = 0,04 (desprezível, não significativa, p = 0,584); ρ de Spearman = -0,00 (p = 0,988); n = 216
- **P4 % mulheres formação x mercado**
  - 2023: r = 0,60 (forte, significativa, p < 0,001); ρ de Spearman = 0,64 (p < 0,001); n = 27
  - painel: r = 0,06 (desprezível, não significativa, p = 0,330); ρ de Spearman = 0,22 (p < 0,001); n = 243

Detalhes: `06_testes_hipotese.csv`, `06b_crescimento_uf_*.csv`, `02_correlacoes.csv`, `03_correlacao_P1_por_ano.csv`.

## 4. Regressões (resumo; coeficiente = elasticidade)

- **M1** (corte 2023): +1% em concluintes/100k ↔ 1,16% em empregos/100k (p < 0,001; R² = 0,69)
- **M2** (painel, formação t-1, efeito de ano): 1,06 (p < 0,001; R² = 0,43)
- **M3** (efeitos fixos de UF e ano): -0,01 (p = 0,981) - DENTRO de um mesmo estado, anos com mais formação não antecedem de forma significativa anos com mais emprego
- **M4** (salário x formação, 2023): 0,30 (p < 0,001; R² = 0,52)
- Pressupostos do M1: Shapiro-Wilk dos resíduos W = 0,949, p = 0,198; Breusch-Pagan LM = 0,852, p = 0,356 (erros robustos HC1). Saída completa: `04_modelos.txt`.

## 5. Posição do RN

- Concluintes por 100 empregos de TI: 9,4 (entre Q1 e a mediana) em 2015 → 10,8 (acima de Q3, 2º de 27) em 2023; mediana das UFs em 2023: 6,0.
- Concluintes de TI: 251 → 410 (63%); empregos formais de TI: 2.661 → 3.795 (43%). Diferença entre os dois crescimentos: 21 p.p., a 2ª maior entre as 27 UFs.
- Salário médio em TI: R$ 4.660,20 (abaixo de Q1; mediana das UFs R$ 5.678,75).
- Modelo M1: empregos de TI/100k observados 114,9 x previstos pelo volume de formação 224,9; resíduo -0,671 (≈ -49% em relação ao esperado), o 2º menor de 27 UFs. Resíduo negativo = menos emprego formal do que o esperado para a formação (indício de baixa absorção local).

## Arquivos gerados

- Tabelas: `01_descritiva_2015.csv`, `01_descritiva_2023.csv`, `01b_tabela_frequencias_*.csv`, `01c_rn_2015_x_2023.csv`, `02_correlacoes.csv`, `03_correlacao_P1_por_ano.csv`, `04_modelos.txt`, `05_residuos_M1_2023.csv`, `06_testes_hipotese.csv`, `06b_crescimento_uf_2015_2023.csv`
- Gráficos: `g1_evolucao_rn_ne_br.png`, `g2_dispersao_formacao_emprego.png`, `g3_dispersao_formacao_salario.png`, `g4_concluintes_por_100_empregos.png`, `g5_dispersao_mulheres.png`, `g6_boxplots_2023.png`, `g7_boxplot_2015_x_2023.png`, `g8_histograma_concluintes_por_100_empregos_2023.png`

> Correlação não implica causalidade. Os resultados indicam associação e indícios, não relações de causa e efeito.