# Formação em TI × Emprego em TI nas UFs brasileiras (foco no RN)

Trabalho da disciplina **Estatística Aplicada à Análise de Dados**.

**Pergunta:** estados que formam mais profissionais de TI têm mais emprego formal
e salários maiores em TI? Onde o Rio Grande do Norte se posiciona nessa relação?

Junta **duas bases públicas** pela chave `UF + ano`, sem questionário nem entrevista:

| Base | Órgão | O que entra |
|---|---|---|
| Censo da Educação Superior | INEP | cursos da área CINE 06 (Computação e TIC): ingressantes, matrículas, concluintes (total e mulheres) |
| RAIS Vínculos | MTE (via Base dos Dados) | vínculos ativos em 31/12 nas CBOs de TI: quantidade, mulheres, salário médio e mediano |
| População (apoio) | IBGE (via Base dos Dados) | normalização por 100 mil habitantes |

## Estrutura

```
config.py               período, CBOs de TI, área CINE, ID do projeto Google Cloud
coletar_rais.py         etapa 1 - RAIS agregada por UF/ano (BigQuery)
coletar_inep.py         etapa 2 - Censo da Educação Superior agregado por UF/ano
coletar_populacao.py    etapa 3 - população por UF/ano
juntar_bases.py         etapa 4 - junção (UF + ano) e criação dos indicadores
descritiva.py           estatística descritiva completa (usado por analise.py)
analise.py              etapa 5 - descritiva, testes, correlações, regressões e gráficos
gerar_dados_exemplo.py  dados FICTÍCIOS para testar o pipeline
dados/processados/      CSVs intermediários
resultados/             tabelas, gráficos, modelos e relatorio.md
resultados/robustez_presencial/   mesma análise só com cursos presenciais
docs/                   texto-base do trabalho e roteiro dos slides
```

## Como rodar

```bash
pip install -r requirements.txt

# 1) Testar o pipeline com dados fictícios (opcional)
python gerar_dados_exemplo.py
python juntar_bases.py
python analise.py

# 2) Dados reais
#    - crie um projeto gratuito em console.cloud.google.com
#    - coloque o ID em BILLING_PROJECT_ID (config.py)
python coletar_rais.py
python coletar_populacao.py
python coletar_inep.py        # ~9 downloads grandes do INEP; pode demorar
python juntar_bases.py
python analise.py

# 3) Robustez: só cursos presenciais (grava em resultados/robustez_presencial/)
python analise.py --presencial
```

Os dados reais já processados estão em `dados/processados/`; para refazer a análise
basta rodar `python juntar_bases.py` e `python analise.py`.

Na primeira consulta ao BigQuery, o pacote `basedosdados` abre o navegador para
você autorizar sua conta Google.

Se o download do INEP falhar, baixe os `.zip` manualmente em
<https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-da-educacao-superior>
e coloque-os em `dados/brutos/`; o script usa os arquivos locais.

## Indicadores criados (juntar_bases.py)

| Indicador | Fórmula |
|---|---|
| `concluintes_ti_100k` | concluintes de TI / população × 100 mil |
| `vinculos_ti_100k` | empregos formais de TI / população × 100 mil |
| `concluintes_por_100_vinculos` | concluintes de TI / empregos de TI × 100 |
| `salario_relativo_ti` | salário médio TI / salário médio geral da UF |
| `participacao_ti_emprego` | % do emprego formal da UF que é TI |
| `pct_fem_concluintes_ti`, `pct_fem_vinculos_ti` | % de mulheres na formação e no mercado |
| `concluintes_ti_100k_lag1` | concluintes do ano anterior (defasagem) |

A coluna de concluintes usada nos indicadores de formação é definida em
`config.COLUNA_FORMACAO` (`"concluintes_ti"`, todos os cursos; alternativa:
`"concluintes_ti_presencial"`). O % de mulheres usa sempre o total, pois o INEP
não informa mulheres por modalidade. Linhas cuja `sigla_uf` não é uma das 27 UFs
(ex.: `IGNORADO` na RAIS de 2021-2023) são descartadas na junção, com aviso no console.

## Estatística descritiva (descritiva.py)

Calculada entre as 27 UFs em dois anos de referência, `config.ANO_INICIO` (2015) e o
último ano do painel (2023), para os indicadores `concluintes_ti_100k`,
`vinculos_ti_100k`, `concluintes_por_100_vinculos`, `salario_medio_ti`,
`salario_relativo_ti`, `participacao_ti_emprego`, `pct_fem_concluintes_ti` e
`pct_fem_vinculos_ti`.

- **Posição e dispersão**: n, média, mediana, desvio-padrão amostral (ddof = 1),
  variância, coeficiente de variação (%), mínimo e máximo (com a UF), amplitude.
- **Quartis**: Q1, Q2 e Q3 por `pandas.Series.quantile` com interpolação **linear**
  (padrão do pandas, equivalente ao "tipo 7" de Hyndman e Fan); amplitude
  interquartil IQR = Q3 - Q1.
- **Assimetria**: `scipy.stats.skew(bias=False)` (coeficiente ajustado à amostra);
  |g| < 0,5 simétrica, 0,5 ≤ |g| < 1 moderada, |g| ≥ 1 forte.
- **Outliers (critério de Tukey)**: valores abaixo de Q1 - 1,5·IQR ou acima de
  Q3 + 1,5·IQR, com a lista de UFs.
- **Moda para variável contínua (dados agrupados)**:
  1. número de classes pela regra de Sturges: k = teto(1 + 3,322·log10(n)), ou seja, k = 6 para n = 27;
  2. classes de mesma amplitude h = (máx - mín)/k, fechadas à esquerda
     (Li ⊢ Ls); a última classe inclui o máximo;
  3. classe modal = classe de maior frequência (em empate, a primeira);
  4. moda de Czuber: Mo = Li + [d1 / (d1 + d2)]·h, com d1 = f_modal - f_anterior e
     d2 = f_modal - f_posterior (frequência 0 quando não há classe anterior/posterior).
- **RN**: valor, posição no ranking (1 = maior) e faixa de quartil ("abaixo de Q1",
  "entre Q1 e a mediana", "entre a mediana e Q3", "acima de Q3").

Como várias distribuições são fortemente assimétricas (média bem acima da mediana,
CV alto e outliers DF, SP e SC), a mediana e os quartis são as referências usadas
para situar o RN.

## Métodos estatísticos (analise.py)

1. **Descritiva** - ver seção acima (`01_descritiva_*.csv`, `01b_*.csv`, `01c_*.csv`)
2. **Testes de hipótese** (`06_testes_hipotese.csv`; nível de significância de 5%)
   - Shapiro-Wilk de cada indicador descritivo em 2023 (justifica testes não paramétricos)
   - Wilcoxon pareado (`alternative="greater"`, n = 27): crescimento % dos concluintes
     x crescimento % dos vínculos de TI entre 2015 e 2023 em cada UF (`06b_crescimento_uf_*.csv`)
   - Mann-Whitney U, Nordeste (AL, BA, CE, MA, PB, PE, PI, RN, SE) x demais 18 UFs, em 2023:
     concluintes por 100 empregos (`alternative="greater"`) e salário médio de TI
     (`alternative="less"`), com as medianas dos dois grupos
3. **Correlação de Pearson e de Spearman** com p-valor, em corte transversal (n = 27) e no painel (`02_correlacoes.csv`); estabilidade ano a ano (`03_...csv`)
4. **Regressão linear (log-log)** (`04_modelos.txt`)
   - M1: corte transversal, erros robustos (HC1)
   - M2: painel com formação defasada (t-1) e efeito de ano, erros agrupados por UF
   - M3: efeitos fixos de UF e ano (variação dentro de cada estado)
   - M4: salário de TI × formação
5. **Pressupostos**: Shapiro-Wilk (normalidade dos resíduos) e Breusch-Pagan (homocedasticidade)
6. **Resíduo do RN** no M1: o estado tem mais ou menos emprego em TI do que o esperado pelo volume de formação? (`05_residuos_*.csv`)
7. **Robustez EAD**: os números principais (correlação P1, faixa do RN em concluintes
   por 100 empregos, Wilcoxon) são recalculados só com cursos presenciais e comparados
   no `relatorio.md`; `python analise.py --presencial` gera a análise completa nessa versão.
8. **Gráficos**: evolução RN × Nordeste × Brasil, dispersões com reta de tendência, ranking de concluintes por 100 empregos, boxplots, histograma

`relatorio.md` resume automaticamente todos os números para usar no texto, na ordem
Dados → Estatística descritiva → Testes de hipótese → Regressões → Posição do RN → Robustez.

### Saídas em `resultados/`

| Arquivo | Conteúdo |
|---|---|
| `01_descritiva_2015.csv`, `01_descritiva_2023.csv` | todas as medidas descritivas por indicador |
| `01b_tabela_frequencias_<indicador>_<ano>.csv` | classes de Sturges, ponto médio, frequências absoluta, relativa e acumulada, UFs de cada classe |
| `01c_rn_2015_x_2023.csv` | RN nos dois anos: valor, variação %, faixa de quartil e posição |
| `02_correlacoes.csv`, `03_correlacao_P1_por_ano.csv` | Pearson e Spearman |
| `04_modelos.txt`, `05_residuos_M1_2023.csv` | regressões e resíduos |
| `06_testes_hipotese.csv`, `06b_crescimento_uf_2015_2023.csv` | testes de hipótese e crescimento por UF |
| `g1` a `g5` | evolução, dispersões e ranking |
| `g6_boxplots_2023.png` | boxplots (um painel por indicador) com as UFs, o RN e os outliers |
| `g7_boxplot_2015_x_2023.png` | concluintes por 100 empregos em 2015 e 2023, RN nos dois anos |
| `g8_histograma_concluintes_por_100_empregos_2023.png` | histograma (Sturges) com média, mediana e moda de Czuber |
| `relatorio.md` | resumo automático com os números |

## Limitações (citar na metodologia)

- **Classificações diferentes**: os cursos usam a CINE (INEP) e as ocupações usam a CBO (MTE); a definição de "TI" em cada base é uma escolha do autor (ver `config.py`).
- **RAIS cobre só emprego formal** (CLT e estatutários); PJ, freelancers e informais ficam de fora.
- **Migração e trabalho remoto**: quem se forma em uma UF pode trabalhar em outra.
- **Cursos EAD** são contados na UF da sede/local de oferta registrado no Censo e podem inflar a formação de algumas UFs; há recorte só com cursos presenciais (`concluintes_ti_presencial`, `--presencial`) para teste de robustez.
- **UF "IGNORADO" na RAIS (2021-2023)**: esses vínculos não têm UF e são descartados na junção.
- **Trabalho remoto e PJ**: a RAIS registra o vínculo na UF do estabelecimento e não capta PJ nem informalidade; quem mora no RN e trabalha para empresa de outro estado não aparece no RN.
- **Correlação não é causalidade**: os resultados mostram associação e indícios, não causa e efeito.
- Observações do painel não são independentes (mesma UF em vários anos); por isso os modelos de painel usam erros agrupados por UF.
