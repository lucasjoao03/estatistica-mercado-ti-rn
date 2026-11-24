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
analise.py              etapa 5 - descritiva, correlações, regressões e gráficos
gerar_dados_exemplo.py  dados FICTÍCIOS para testar o pipeline
dados/processados/      CSVs intermediários
resultados/             tabelas, gráficos, modelos e relatorio.md
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
```

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

## Métodos estatísticos (analise.py)

1. **Descritiva** - média, desvio-padrão, coeficiente de variação, posição do RN (`01_descritiva_*.csv`)
2. **Correlação de Pearson e de Spearman** com p-valor, em corte transversal (n = 27) e no painel (`02_correlacoes.csv`); estabilidade ano a ano (`03_...csv`)
3. **Regressão linear (log-log)** (`04_modelos.txt`)
   - M1: corte transversal, erros robustos (HC1)
   - M2: painel com formação defasada (t-1) e efeito de ano, erros agrupados por UF
   - M3: efeitos fixos de UF e ano (variação dentro de cada estado)
   - M4: salário de TI × formação
4. **Pressupostos**: Shapiro-Wilk (normalidade dos resíduos) e Breusch-Pagan (homocedasticidade)
5. **Resíduo do RN** no M1: o estado tem mais ou menos emprego em TI do que o esperado pelo volume de formação? (`05_residuos_*.csv`)
6. **Gráficos**: evolução RN × Nordeste × Brasil, dispersões com reta de tendência, ranking de concluintes por 100 empregos

`relatorio.md` resume automaticamente todos os números para usar no texto.

## Limitações (citar na metodologia)

- **Classificações diferentes**: os cursos usam a CINE (INEP) e as ocupações usam a CBO (MTE); a definição de "TI" em cada base é uma escolha do autor (ver `config.py`).
- **RAIS cobre só emprego formal** (CLT e estatutários); PJ, freelancers e informais ficam de fora.
- **Migração e trabalho remoto**: quem se forma em uma UF pode trabalhar em outra.
- **Cursos EAD** são contados na UF da sede/local de oferta registrado no Censo; há recorte só com cursos presenciais (`concluintes_ti_presencial`) para teste de robustez.
- **Correlação não é causalidade**: os resultados mostram associação entre formação e mercado.
- Observações do painel não são independentes (mesma UF em vários anos); por isso os modelos de painel usam erros agrupados por UF.
