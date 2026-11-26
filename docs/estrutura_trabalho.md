# Formação superior e emprego formal em Tecnologia da Informação: o gargalo do Rio Grande do Norte é a formação ou a absorção pelo mercado?

Disciplina: Estatística Aplicada à Análise de Dados

> Texto-base do trabalho, organizado nos três blocos da orientação (Caracterização; Análise estatística; Referências), com o fluxo PROBLEMA → DADOS → ANÁLISE ESTATÍSTICA → DIÁLOGO → CONTRIBUIÇÕES distribuído entre eles. Todos os números vêm de `resultados/` (gerados por `python juntar_bases.py` e `python analise.py`). Se os dados forem atualizados, confira os valores em `resultados/relatorio.md`.

---

# 1 CARACTERIZAÇÃO

## 1.1 Resumo

O discurso de "apagão" de profissionais de Tecnologia da Informação (TI) no Brasil costuma sustentar propostas de expansão da formação superior na área. Este trabalho investiga se esse diagnóstico se aplica ao Rio Grande do Norte (RN). Foram cruzados dados secundários do Censo da Educação Superior (INEP), da Relação Anual de Informações Sociais (RAIS/MTE) e das estimativas populacionais do IBGE, formando um painel das 27 unidades da federação (UFs) entre 2015 e 2023 (243 observações). A análise combinou estatística descritiva (média, mediana, moda de Czuber, desvio-padrão, quartis e outliers pelo critério de Tukey), testes de Shapiro-Wilk, Wilcoxon e Mann-Whitney, correlações e regressões log-log. Em 2023, o RN registrou 22,1 concluintes de TI para cada 100 empregos formais da área, acima do terceiro quartil nacional (mediana de 14,4) e quarto maior valor do país. Entre 2015 e 2023, os concluintes cresceram 216% (63% considerando apenas cursos presenciais) e os vínculos, 43%. O salário médio de TI no estado (R$ 4.660,20) ficou abaixo do primeiro quartil, e o Nordeste apresentou mais concluintes por emprego (p = 0,021) e salários menores (p = 0,003) que as demais UFs. Os resultados indicam que, no RN, o gargalo está na absorção dos formados pelo mercado formal local, e não na formação. Como contribuição metodológica, propõe-se o indicador "concluintes por 100 empregos de TI", reproduzível anualmente com dados públicos.

**Palavras-chave:** mercado de trabalho em TI; formação superior; Rio Grande do Norte; estatística não paramétrica; RAIS.

## 1.2 Introdução

O debate público sobre o setor de tecnologia no Brasil é marcado pela ideia de escassez: empresas e entidades setoriais relatam dificuldade de contratação, e projeções de déficit de profissionais são frequentemente usadas para justificar a abertura de cursos e vagas na área. Esse diagnóstico, porém, costuma ser formulado para o país como um todo, sem distinguir realidades regionais muito diferentes entre si.

O Rio Grande do Norte ilustra essa questão. O estado ampliou de forma expressiva sua formação superior em TI na última década, mas sua estrutura produtiva tem participação pequena de empresas de tecnologia em comparação com polos como São Paulo, Santa Catarina e o Distrito Federal. Se a escassez fosse o problema central também no RN, seria de esperar que o emprego formal crescesse ao menos no mesmo ritmo da formação, e que os salários refletissem a disputa por profissionais. Se, ao contrário, o estado forma mais do que o mercado local absorve, a receita de "formar mais" teria efeito limitado ou estimularia a saída de profissionais para outros estados.

A literatura consultada trata o tema principalmente pelo lado da oferta de formação. Albano, Zanatta e Garcia (2013) avaliam se a formação superior em TI no Rio Grande do Sul é adequada às necessidades do mercado de trabalho daquele estado, examinando a relação entre os cursos oferecidos e as demandas das empresas. O estudo é restrito a uma única unidade da federação e não compara estados entre si. Costa e Martins (2016) realizam uma análise quantitativa da formação do estoque de mão de obra qualificada em TI no Brasil e concluem que o número de formados na área está aquém da necessidade do mercado. Trata-se de um diagnóstico para o país agregado, coerente com o discurso de escassez.

Nenhum dos dois estudos confronta, de forma sistemática, formação e emprego em todas as UFs, com testes estatísticos, nem analisa o caso do RN. Este trabalho ocupa esse espaço: compara as 27 UFs ao longo de nove anos e posiciona o RN em relação às demais.

## 1.3 Problema e pergunta de pesquisa

**Problema.** Existe um discurso nacional de escassez de profissionais de TI que orienta políticas de expansão da formação. Não se sabe se esse diagnóstico descreve a situação do Rio Grande do Norte.

**Pergunta de pesquisa.** No Rio Grande do Norte, o principal gargalo da área de TI é a falta de formação superior ou a baixa capacidade do mercado formal local de absorver os profissionais formados?

## 1.4 Objetivos

**Objetivo geral.** Analisar a relação entre formação superior e emprego formal em TI nas 27 UFs brasileiras entre 2015 e 2023, com foco na posição do Rio Grande do Norte.

**Objetivos específicos.**

1. Descrever a distribuição, entre as UFs, dos indicadores de formação, emprego, salário e participação feminina em TI, em 2015 e 2023.
2. Situar o RN em cada indicador (valor, posição no ranking e faixa de quartil) e acompanhar sua evolução entre 2015 e 2023.
3. Testar se a formação cresceu mais que o emprego nas UFs e se o Nordeste difere das demais regiões quanto à relação formação/emprego e ao salário em TI.
4. Estimar a associação entre formação e emprego entre os estados e dentro de cada estado ao longo do tempo.
5. Confrontar os resultados com a literatura e indicar implicações para o poder público, as empresas e as instituições de ensino.

## 1.5 Dados e método

**Fontes (dados secundários).**

| Base | Órgão | Variáveis utilizadas |
|---|---|---|
| Censo da Educação Superior (microdados) | INEP | cursos da área geral CINE 06 (Computação e TIC): ingressantes, matrículas, concluintes (total, mulheres, presenciais) |
| RAIS Vínculos | MTE, via Base dos Dados | vínculos ativos em 31/12 nas ocupações de TI: quantidade, mulheres, salário médio; vínculos e salário médio totais da UF |
| Estimativas de população | IBGE, via Base dos Dados | população residente por UF e ano |

**Definição de "TI".** Na formação, consideraram-se os cursos da área geral 06 da Classificação Internacional Normalizada da Educação adaptada para cursos de graduação e sequenciais (CINE Brasil), "Computação e Tecnologias da Informação e Comunicação". No mercado, consideraram-se seis famílias da Classificação Brasileira de Ocupações (CBO 2002): 1425 (gerentes de TI), 2122 (engenheiros em computação), 2123 (administradores de TI), 2124 (analistas de TI), 3171 (técnicos de desenvolvimento de sistemas e aplicações) e 3172 (técnicos em operação e monitoração de computadores).

**Período e unidade de análise.** De 2015 a 2023, por UF e ano. As três bases foram agregadas por UF e ano e unidas pela chave `sigla_uf + ano` (RAIS e INEP por junção interna; população por junção à esquerda), resultando em um painel de 27 UFs × 9 anos = 243 observações. Registros da RAIS sem UF identificada ("IGNORADO", 2021 a 2023) foram descartados.

**Indicadores.**

| Indicador | Definição |
|---|---|
| Concluintes de TI por 100 mil habitantes | concluintes de TI / população × 100.000 |
| Empregos formais de TI por 100 mil habitantes | vínculos de TI / população × 100.000 |
| Concluintes por 100 empregos de TI | concluintes de TI / vínculos de TI × 100 |
| Salário médio em TI | média da remuneração dos vínculos de TI (R$) |
| Salário relativo de TI | salário médio de TI / salário médio geral da UF |
| Participação da TI no emprego | vínculos de TI / vínculos totais × 100 |
| % de mulheres na formação e no mercado | concluintes e vínculos femininos / total × 100 |

**Métodos estatísticos.** (i) Estatística descritiva entre as 27 UFs em 2015 e 2023: média, mediana, moda de Czuber (classes pela regra de Sturges, k = 6), desvio-padrão amostral, variância, coeficiente de variação, quartis (interpolação linear), amplitude interquartil, assimetria e outliers pelo critério de Tukey (1,5·IQR). (ii) Testes de hipótese a 5% de significância: Shapiro-Wilk (normalidade), Wilcoxon pareado e Mann-Whitney U (não paramétricos). (iii) Correlações de Pearson e Spearman. (iv) Regressões log-log em corte transversal e em painel, com erros robustos e efeitos fixos de UF e ano. (v) Teste de robustez com apenas os concluintes de cursos presenciais. O processamento foi feito em Python (pandas, SciPy, statsmodels e matplotlib), com código reproduzível.

---

# 2 ANÁLISE ESTATÍSTICA

## 2.1 Estatística descritiva

A Tabela 1 resume a distribuição dos indicadores entre as 27 UFs em 2023 (tabela completa em `resultados/01_descritiva_2023.csv`; a de 2015 está em `01_descritiva_2015.csv`).

**Tabela 1 – Medidas descritivas entre as 27 UFs, 2023**

| Indicador | Média (x̄) | Mediana (x̃) | Moda (Czuber) | s | CV (%) | Q1 | Q3 | RN | Faixa do RN (posição) |
|---|---|---|---|---|---|---|---|---|---|
| Concluintes de TI por 100 mil hab. | 30,38 | 24,86 | 22,99 | 23,00 | 75,7 | 17,45 | 32,94 | 25,43 | entre a mediana e Q3 (13º) |
| Empregos formais de TI por 100 mil hab. | 256,11 | 152,62 | 159,68 | 256,19 | 100,0 | 111,56 | 313,27 | 114,90 | entre Q1 e a mediana (20º) |
| Concluintes por 100 empregos de TI | 14,79 | 14,44 | 14,94 | 5,28 | 35,7 | 10,95 | 16,90 | 22,13 | acima de Q3 (4º) |
| Salário médio em TI (R$) | 6.106,72 | 5.678,75 | 5.127,88 | 1.536,54 | 25,2 | 5.086,21 | 6.860,02 | 4.660,20 | abaixo de Q1 (24º) |
| Salário TI / salário médio geral | 1,72 | 1,68 | 1,51 | 0,27 | 15,5 | 1,50 | 1,91 | 1,48 | abaixo de Q1 (22º) |
| % do emprego formal que é TI | 0,88 | 0,67 | 0,53 | 0,55 | 62,1 | 0,52 | 1,11 | 0,55 | entre Q1 e a mediana (18º) |
| % mulheres entre concluintes de TI | 15,14 | 14,63 | 14,37 | 2,39 | 15,8 | 13,69 | 16,74 | 13,69 | entre Q1 e a mediana (20º) |
| % mulheres nos empregos de TI | 18,81 | 19,09 | 20,06 | 2,65 | 14,1 | 17,55 | 20,41 | 17,02 | abaixo de Q1 (22º) |

Fonte: elaboração própria a partir de INEP, MTE (RAIS) e IBGE. Posição: 1º = maior valor.

**Forma das distribuições.** Em sete dos oito indicadores a média supera a mediana, o que indica assimetria à direita. Os casos mais acentuados são os empregos de TI por 100 mil habitantes (média de 256,1 contra mediana de 152,6; CV de 100%; outliers SC, SP e DF), os concluintes por 100 mil habitantes (30,4 contra 24,9; CV de 76%; outliers SP e DF) e o salário médio de TI (R$ 6.106,72 contra R$ 5.678,75; outliers SP e DF). A assimetria é forte (|g| ≥ 1) em quatro indicadores, e o teste de Shapiro-Wilk rejeita a normalidade em quatro dos oito (Seção 2.2). Como poucos polos tecnológicos puxam a média para cima, a **mediana** e os **quartis** são as referências adequadas para situar o RN, e as comparações foram feitas com testes não paramétricos. O Gráfico g6 (`resultados/g6_boxplots_2023.png`) mostra essas distribuições, com o RN destacado e os outliers identificados.

O indicador central do trabalho, **concluintes por 100 empregos de TI**, tem distribuição mais próxima da simetria (média de 14,79, mediana de 14,44 e moda de Czuber de 14,94; classe modal de 13,58 a 16,99, com 9 UFs). O RN, com 22,13, está acima do terceiro quartil (16,90), em uma classe da qual é o único integrante (20,39 a 23,79; Gráfico g8, `resultados/g8_histograma_concluintes_por_100_empregos_2023.png`, e `resultados/01b_tabela_frequencias_concluintes_por_100_vinculos_2023.csv`). Apenas o Acre é outlier superior nesse indicador. No agregado nacional (soma dos concluintes sobre a soma dos vínculos), a razão foi de 9,97 em 2023, menos da metade da observada no RN.

**Tabela 2 – Rio Grande do Norte, 2015 × 2023**

| Indicador | RN 2015 | RN 2023 | Variação | Faixa 2015 | Faixa 2023 | Posição |
|---|---|---|---|---|---|---|
| Concluintes de TI (nº) | 266 | 840 | +215,8% | abaixo de Q1 | entre Q1 e a mediana | 23º → 15º |
| Empregos formais de TI (nº) | 2.661 | 3.795 | +42,6% | entre Q1 e a mediana | entre Q1 e a mediana | 18º → 19º |
| Concluintes de TI por 100 mil hab. | 7,73 | 25,43 | +229,1% | abaixo de Q1 | entre a mediana e Q3 | 24º → 13º |
| Empregos formais de TI por 100 mil hab. | 77,31 | 114,90 | +48,6% | entre Q1 e a mediana | entre Q1 e a mediana | 18º → 20º |
| Concluintes por 100 empregos de TI | 10,00 | 22,13 | +121,4% | entre Q1 e a mediana | acima de Q3 | 17º → 4º |
| Salário médio em TI (R$) | 3.253,73 | 4.660,20 | +43,2% | abaixo de Q1 | abaixo de Q1 | 22º → 24º |
| Salário TI / salário médio geral | 1,60 | 1,48 | −7,8% | entre Q1 e a mediana | abaixo de Q1 | 18º → 22º |

Fonte: `resultados/01c_rn_2015_x_2023.csv`.

Entre 2015 e 2023, o RN saiu do grupo de menor formação per capita (abaixo de Q1) para a metade superior, enquanto o emprego formal de TI per capita permaneceu entre Q1 e a mediana e caiu duas posições. Com isso, a razão concluintes/empregos passou da metade inferior (10,0; 17º) para acima de Q3 (22,1; 4º), como mostra o Gráfico g7 (`resultados/g7_boxplot_2015_x_2023.png`). O salário médio de TI continuou abaixo de Q1, e o salário relativo de TI (comparado ao salário médio do próprio estado) recuou e também passou para abaixo de Q1.

## 2.2 Testes de hipótese

Todos os testes usam nível de significância de 5% (detalhes em `resultados/06_testes_hipotese.csv`).

**a) Normalidade (Shapiro-Wilk, 2023).** H0: os valores das UFs seguem distribuição normal. A normalidade foi rejeitada para concluintes por 100 mil habitantes (p < 0,001), empregos por 100 mil habitantes (p < 0,001), salário médio de TI (p = 0,003) e participação da TI no emprego (p < 0,001). Não foi rejeitada para concluintes por 100 empregos (p = 0,099), salário relativo (p = 0,282) e percentuais de mulheres (p = 0,584 e p = 0,099). Como parte das variáveis não é normal e n = 27 é pequeno, as comparações usam testes não paramétricos.

**b) Wilcoxon pareado (crescimento da formação × crescimento do emprego, 2015–2023, n = 27).** H0: a mediana da diferença (crescimento % dos concluintes − crescimento % dos vínculos) é menor ou igual a zero; H1: os concluintes cresceram mais que os empregos. Resultado: W = 226, p = 0,193, **H0 não rejeitada**. No conjunto das UFs, a mediana do crescimento dos concluintes (65,9%) superou a dos vínculos (52,3%), mas a formação cresceu mais que o emprego em apenas 15 das 27 UFs, e a diferença não é estatisticamente significativa. Portanto, a expansão da formação acima do emprego **não é um padrão nacional generalizado**. O RN é um caso extremo: +216% contra +43%, diferença de 173 pontos percentuais, a 2ª maior do país (atrás apenas de Sergipe; `resultados/06b_crescimento_uf_2015_2023.csv`).

**c) Mann-Whitney U (concluintes por 100 empregos, Nordeste × demais UFs, 2023).** H0: as distribuições são iguais; H1: o Nordeste forma mais em relação ao emprego. Resultado: U = 121, p = 0,021, **H0 rejeitada**. Mediana do Nordeste (9 UFs): 15,10; demais 18 UFs: 11,79. Há evidência de que, no Nordeste, a formação é maior em relação ao emprego disponível.

**d) Mann-Whitney U (salário médio de TI, Nordeste × demais UFs, 2023).** H0: as distribuições são iguais; H1: o Nordeste paga menos em TI. Resultado: U = 26, p = 0,003, **H0 rejeitada**. Mediana do Nordeste: R$ 4.989; demais: R$ 6.334. O resultado é compatível com a menor disputa por profissionais na região.

**e) Correlações.** Entre os estados, formação e emprego estão fortemente associados: em 2023, r de Pearson = 0,95 e ρ de Spearman = 0,88 (p < 0,001; n = 27) entre concluintes e empregos por 100 mil habitantes. A associação de Pearson, contudo, oscila bastante entre os anos (de 0,26 a 0,95), por ser sensível aos polos DF e SP, enquanto a de Spearman se mantém entre 0,56 e 0,88 (`resultados/03_correlacao_P1_por_ano.csv`). Já o crescimento da formação e o crescimento do emprego de um ano para o outro não se correlacionam (r = 0,01; p = 0,933; painel, n = 216). A formação também se associa ao salário médio de TI (r = 0,85 em 2023), o que reflete o porte dos polos tecnológicos.

**f) Regressões (resumo; `resultados/04_modelos.txt`).** No corte de 2023 (M1), cada 1% a mais de concluintes por habitante está associado a 1,29% a mais de empregos de TI por habitante (p < 0,001; R² = 0,84). No painel com formação defasada (M2), a elasticidade é de 1,15 (p < 0,001). No modelo com efeitos fixos de UF e ano (M3), que considera apenas a variação **dentro** de cada estado, o coeficiente cai para 0,03 e perde a significância (p = 0,891): anos com mais formação em um estado não antecederam anos com mais emprego nesse mesmo estado. Pelo M1, o RN tem 114,9 empregos de TI por 100 mil habitantes, contra 182,1 esperados para o seu nível de formação (resíduo ≈ −37%, o 3º mais negativo entre as UFs, atrás de PB e AC).

**g) Robustez (cursos presenciais).** Como os concluintes de cursos a distância (EAD) são registrados na UF informada ao Censo, repetiu-se a análise apenas com cursos presenciais (`resultados/robustez_presencial/`). O RN continua acima de Q3 em concluintes por 100 empregos (10,8 contra mediana de 6,0; 2º do país), e a correlação entre formação e emprego permanece alta (r = 0,90). O crescimento dos concluintes presenciais no RN, porém, foi de 63%, ainda superior ao dos vínculos (43%), mas bem menor que os 216% do total. Ou seja, boa parte da expansão recente da formação no estado vem do EAD. No conjunto das UFs, a formação presencial cresceu menos que o emprego (diferença mediana de −72 pontos percentuais; Wilcoxon p = 1,000).

## 2.3 Lacuna dos artigos e tese

**Lacuna.** Os dois artigos tratam o problema pelo lado da falta ou da adequação da formação, no Rio Grande do Sul (ALBANO; ZANATTA; GARCIA, 2013) ou no Brasil agregado (COSTA; MARTINS, 2016). Nenhum deles compara formação e emprego entre todas as UFs com testes estatísticos, nem analisa o Rio Grande do Norte.

**Tese.** *No Rio Grande do Norte, o gargalo da área de TI não é a falta de formação, e sim a baixa capacidade do mercado formal local de absorver os profissionais formados.*

Os indícios que sustentam a tese são: (i) o RN está acima de Q3 em concluintes por 100 empregos, com mais que o dobro da razão nacional, inclusive quando se consideram apenas cursos presenciais; (ii) a formação cresceu muito mais que o emprego formal entre 2015 e 2023, com a 2ª maior diferença entre as UFs; (iii) o emprego observado está cerca de 37% abaixo do esperado para o nível de formação do estado; (iv) o salário médio e o salário relativo de TI estão abaixo de Q1, o que é pouco compatível com um quadro de escassez; e (v) o Nordeste como um todo forma mais em relação ao emprego e paga menos que as demais UFs.

## 2.4 Diálogo com a literatura

Costa e Martins (2016) defendem que a formação em TI no Brasil está abaixo da necessidade do mercado. Os dados do RN apontam o contrário no contexto local: o estado está acima de Q3 em concluintes por 100 empregos (22,1, contra mediana nacional de 14,4) e a formação cresceu bem mais que o emprego (+216% contra +43%; +63% considerando apenas cursos presenciais). O resultado não invalida o diagnóstico dos autores para o agregado nacional: a razão concluintes/empregos do Brasil como um todo foi de apenas 9,97 em 2023, e, considerando somente cursos presenciais, a formação cresceu menos que o emprego em 24 das 27 UFs. O que os dados mostram é que a média nacional esconde realidades estaduais distintas.

Albano, Zanatta e Garcia (2013) avaliam a adequação da formação ao mercado apenas no Rio Grande do Sul. Este trabalho amplia a análise para as 27 UFs, com testes estatísticos. Formação e emprego estão fortemente associados entre os estados (r ≈ 0,95 em 2023): estados com mais emprego em TI também formam mais. Dentro de um mesmo estado, porém, o aumento da formação não foi acompanhado de mais emprego (modelo com efeitos fixos sem significância, p = 0,891). Isso sugere que a associação entre estados reflete o porte dos polos tecnológicos, e não um efeito da formação sobre o emprego local.

**Síntese.** A tese de escassez pode valer para o país agregado ou para polos tecnológicos, mas não descreve o RN, onde os indícios apontam para um gargalo na absorção pelo mercado formal.

## 2.5 Contribuição (o "business")

- **Poder público e parques tecnológicos:** priorizar a atração e a retenção de empresas de tecnologia, em vez de expandir vagas de formação. O indicador de concluintes por 100 empregos sinaliza onde o investimento em demanda tende a render mais que o investimento em oferta.
- **Empresas (o "business"):** o RN oferece profissionais disponíveis com custo salarial abaixo do primeiro quartil nacional (R$ 4.660,20, contra mediana de R$ 5.678,75), argumento para a instalação de centros de desenvolvimento e operações remotas no estado.
- **Instituições de ensino:** priorizar qualidade, especialização (pós-graduação) e empregabilidade (estágios, parcerias com empresas, preparação para o trabalho remoto) em vez da ampliação do número de vagas.
- **Contribuição metodológica:** o indicador "concluintes por 100 empregos de TI", com posição por quartis, é reproduzível anualmente com dados públicos (INEP e RAIS) e permite acompanhar o equilíbrio entre formação e mercado em qualquer UF.

## 2.6 Justificativa

O discurso de escassez de profissionais de TI é nacional, mas a realidade de cada estado é diferente, como mostram a forte assimetria dos indicadores e a dispersão entre as UFs. Aplicar ao RN a receita de "formar mais" pode apenas aumentar a saída de profissionais qualificados para outros estados, sem resolver a falta de oportunidades locais. Além disso, essas bases públicas ainda não tinham sido cruzadas para o RN, o que torna o trabalho útil para orientar decisões de política pública, de investimento privado e de planejamento das instituições de ensino.

## 2.7 Limitações

- **Classificações diferentes:** os cursos seguem a CINE (INEP) e as ocupações seguem a CBO (MTE); a definição de "TI" em cada base é uma escolha do autor.
- **Emprego formal apenas:** a RAIS cobre vínculos celetistas e estatutários; não capta trabalho como pessoa jurídica (PJ), informalidade nem profissionais que moram no RN e trabalham remotamente para empresas de outros estados. Parte dos formados pode estar ocupada fora do registro formal local.
- **Registros sem UF:** vínculos com UF "IGNORADO" na RAIS (2021 a 2023) foram descartados na junção.
- **Cursos EAD:** podem inflar a contagem de concluintes em algumas UFs. O teste de robustez mostra que a posição do RN se mantém, mas que boa parte do crescimento recente da formação no estado vem do EAD.
- **Migração:** quem se forma em uma UF pode trabalhar em outra; os dados agregados não permitem acompanhar trajetórias individuais.
- **Tamanho da amostra:** n = 27 UFs limita o poder dos testes; a correlação de Pearson é sensível a outliers (DF, SP, SC), por isso foi complementada por Spearman.
- **Associação, não causalidade:** os resultados indicam associação e indícios, não relações de causa e efeito.

## 2.8 Conclusão

O trabalho investigou se o discurso nacional de escassez de profissionais de TI se aplica ao Rio Grande do Norte. A estatística descritiva mostrou distribuições muito assimétricas entre as UFs, o que tornou a mediana e os quartis as referências adequadas. Por essas referências, o RN passou de uma posição intermediária para o quartil superior em concluintes por 100 empregos de TI (22,1, contra mediana de 14,4), com formação crescendo bem mais que o emprego formal. O estado também ficou abaixo do primeiro quartil em salário e com emprego cerca de 37% inferior ao esperado para seu nível de formação. Os testes indicaram que o Nordeste forma mais em relação ao emprego e paga menos que as demais UFs, e que a expansão da formação acima do emprego não é um padrão nacional: ela é particularmente intensa no RN. Esses indícios são compatíveis com a tese de que, no RN, o gargalo é a absorção dos formados pelo mercado formal local. Como desdobramentos, sugere-se incorporar dados de trabalho remoto e de migração de egressos e acompanhar anualmente o indicador proposto.

---

# 3 REFERÊNCIAS

ALBANO, C. S.; ZANATTA, A. L.; GARCIA, F. T. Mercado de trabalho na área de TI e a formação superior no estado do Rio Grande do Sul. **Revista Eletrônica de Sistemas de Informação**, v. 12, n. 1, 2013. DOI: 10.5329/RESI.2013.1201006.

BASE DOS DADOS. **Base dos Dados**: repositório de dados públicos tratados. Disponível em: https://basedosdados.org. Acesso em: 24 nov. 2026.

BRASIL. Ministério do Trabalho e Emprego. **Relação Anual de Informações Sociais (RAIS)**: microdados de vínculos, 2015-2023. Brasília: MTE. Disponível em: https://basedosdados.org (conjunto br_me_rais). Acesso em: 24 nov. 2026.

COSTA, M. A. M.; MARTINS, H. C. Análise quantitativa da formação do estoque de mão de obra qualificada de profissionais na área de TI. **Revista Eletrônica de Sistemas de Informação**, 2016.

INSTITUTO BRASILEIRO DE GEOGRAFIA E ESTATÍSTICA (IBGE). **Estimativas da população residente nos municípios e unidades da federação**, 2015-2023. Rio de Janeiro: IBGE. Disponível em: https://basedosdados.org (conjunto br_ibge_populacao). Acesso em: 24 nov. 2026.

INSTITUTO NACIONAL DE ESTUDOS E PESQUISAS EDUCACIONAIS ANÍSIO TEIXEIRA (INEP). **Microdados do Censo da Educação Superior**, 2015-2023. Brasília: Inep. Disponível em: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-da-educacao-superior. Acesso em: 24 nov. 2026.

---

### Notas para revisão (remover antes da entrega)

- Completar a referência de Costa e Martins (2016) com volume, número, páginas e DOI.
- Se quiser citar números do discurso de escassez na Introdução (p. ex., projeções de déficit de entidades setoriais), acrescentar a fonte nas referências.
- Conferir as datas de acesso (foram usadas as datas da coleta dos arquivos).
