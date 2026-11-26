# Roteiro dos slides – seminário (≈ 10 slides, ~15 min)

Mesmos blocos do trabalho: **Caracterização** (slides 1–4) → **Análise estatística** (slides 5–9) → **Referências** (slide 10). Os números vêm de `resultados/relatorio.md`; os arquivos indicados estão em `resultados/`.

---

## Bloco 1 – CARACTERIZAÇÃO

### Slide 1 – Capa
- **Título:** Formação superior e emprego formal em TI: o gargalo do RN é a formação ou a absorção pelo mercado?
- Disciplina: Estatística Aplicada à Análise de Dados
- Autor(a), professor(a), data
- Subtítulo: 27 UFs, 2015–2023, dados públicos (INEP + RAIS + IBGE)
- **Visual:** nenhum (ou miniatura do `g7_boxplot_2015_x_2023.png`)

### Slide 2 – Artigos estudados
- **Albano, Zanatta e Garcia (2013):** a formação superior em TI no RS é adequada ao mercado? Análise de um único estado, sem comparação entre UFs
- **Costa e Martins (2016):** o número de formados em TI no Brasil está aquém da necessidade do mercado (Brasil agregado)
- Ponto em comum: os dois olham pelo lado da **falta ou adequação da formação**
- **Lacuna:** nenhum compara formação × emprego entre as 27 UFs com testes estatísticos, nem analisa o RN
- **Visual:** dois cartões lado a lado (artigo → conclusão → limite)

### Slide 3 – Problema e objetivo
- **Problema:** existe um discurso nacional de "apagão" de profissionais de TI. Isso vale para o RN?
- **Pergunta:** no RN, o gargalo é a formação ou a absorção pelo mercado formal local?
- **Objetivo geral:** analisar formação × emprego formal em TI nas 27 UFs (2015–2023), com foco no RN
- Específicos: descrever as distribuições, situar o RN por quartis, testar diferenças (Wilcoxon, Mann-Whitney), estimar associações
- **Visual:** `g1_evolucao_rn_ne_br.png` (formação e emprego por 100 mil hab.: RN × Nordeste × Brasil)

### Slide 4 – Dados e método (dados secundários)
- **INEP**, Censo da Educação Superior: concluintes dos cursos CINE 06 (Computação e TIC)
- **RAIS/MTE**: vínculos formais em 6 famílias CBO de TI (1425, 2122, 2123, 2124, 3171, 3172) e salário médio; **IBGE**: população
- Junção por **UF + ano**: painel de 27 UFs × 9 anos = **243 observações**
- Indicador-chave: **concluintes por 100 empregos de TI** (formados no ano ÷ empregos × 100)
- Métodos: descritiva (x̄, x̃, moda de Czuber, s, quartis, Tukey) → testes não paramétricos → correlação e regressão; robustez sem EAD
- **Visual:** diagrama simples INEP + RAIS + IBGE → painel UF × ano → indicadores

---

## Bloco 2 – ANÁLISE ESTATÍSTICA

### Slide 5 – Estatística descritiva (descrever)
- Concluintes por 100 empregos, 2023: **x̄ = 14,79; x̃ = 14,44; moda (Czuber) = 14,94; s = 5,28; CV = 36%**
- Q1 = 10,95 e Q3 = 16,90 → **RN = 22,13, acima de Q3 (4º de 27)**; outlier: AC
- Empregos de TI/100 mil hab.: média 256,1 × mediana 152,6 (CV 100%; outliers DF, SC, SP) → **distribuições assimétricas, a mediana é a referência**
- Salário médio de TI: **RN R$ 4.660 (abaixo de Q1)**, contra mediana de R$ 5.679 (outliers DF e SP)
- **RN 2015 → 2023:** concluintes **266 → 840 (+216%)**; empregos de TI **2.661 → 3.795 (+43%)**; concluintes por 100 empregos 10,0 (17º) → 22,1 (4º)
- **Visual:** `g6_boxplots_2023.png` (principal) + `g7_boxplot_2015_x_2023.png`; opcional: `g8_histograma_concluintes_por_100_empregos_2023.png`. Tabela: `01c_rn_2015_x_2023.csv`

### Slide 6 – Testes de hipótese (comparar e inferir)
- **Shapiro-Wilk:** normalidade rejeitada em 4 de 8 indicadores (ex.: empregos/100k, salário) → testes **não paramétricos**
- **Mann-Whitney (concluintes por 100 empregos):** Nordeste 15,10 × demais 11,79 → **p = 0,021** (o NE forma mais em relação ao emprego)
- **Mann-Whitney (salário de TI):** Nordeste R$ 4.989 × demais R$ 6.334 → **p = 0,003** (o NE paga menos)
- **Wilcoxon (crescimento dos concluintes × dos empregos, 27 UFs):** **p = 0,193**, não significativo → não é um padrão nacional; o **RN tem a 2ª maior diferença** (+216% × +43%)
- **Correlação e regressão:** entre estados, r = 0,95 (2023); dentro do estado (efeitos fixos), coeficiente 0,03, **p = 0,891**; RN com emprego **≈ 37% abaixo do esperado** pela formação
- **Visual:** tabela-resumo de `06_testes_hipotese.csv` (teste | H0 | p | decisão) + `g2_dispersao_formacao_emprego.png`

### Slide 7 – Lacuna e tese científica
- **Lacuna:** a literatura vê o problema pela **falta de formação** (RS ou Brasil agregado), sem comparar as UFs nem olhar para o RN
- **Tese:** *"No Rio Grande do Norte, o gargalo da área de TI não é a falta de formação, e sim a baixa capacidade do mercado formal local de absorver os profissionais formados."*
- Indícios: acima de Q3 em concluintes/empregos · formação cresceu 5× mais que o emprego · emprego 37% abaixo do esperado · salário abaixo de Q1
- Robustez: **sem EAD, o RN continua acima de Q3 (2º)**; crescimento presencial de +63% contra +43% dos empregos
- **Visual:** frase da tese em destaque + `g4_concluintes_por_100_empregos.png`

### Slide 8 – Diálogo com a literatura (interpretar com cautela)
- **Costa e Martins (2016):** "formação abaixo da necessidade". **No RN, o contrário:** 22,1 concluintes por 100 empregos (mediana 14,4); +216% × +43%
- Mas o agregado Brasil é de 9,97 por 100 empregos, e sem EAD a formação cresceu menos que o emprego em 24 das 27 UFs → **a escassez pode valer para o país ou para os polos**
- **Albano et al. (2013):** só o RS. Aqui, 27 UFs com testes: forte associação **entre** estados (r ≈ 0,95), mas **dentro** do estado mais formação não trouxe mais emprego (p = 0,891)
- Síntese: a tese de escassez **não descreve o RN**; lá o gargalo é a absorção
- Cautela: são **associações e indícios**, não causalidade (RAIS não capta PJ, informalidade nem remoto)
- **Visual:** quadro de duas colunas "O que o artigo diz" × "O que os dados do RN mostram"

### Slide 9 – Contribuição, justificativa e implicações
- **Poder público e parques tecnológicos:** atrair e reter empresas de tecnologia em vez de abrir mais vagas
- **Empresas (o "business"):** profissionais disponíveis no RN com salário abaixo de Q1 (R$ 4.660 × mediana R$ 5.679) → centros de desenvolvimento no estado
- **Instituições de ensino:** qualidade, pós-graduação e empregabilidade, em vez de quantidade de vagas
- **Metodológica:** indicador "concluintes por 100 empregos de TI", reproduzível todo ano com dados públicos
- **Justificativa:** o discurso é nacional, mas cada estado é diferente; "formar mais" no RN pode aumentar a saída de profissionais; as bases ainda não tinham sido cruzadas para o RN
- **Visual:** três ícones (governo, empresa, universidade) com uma frase cada

---

## Bloco 3 – REFERÊNCIAS

### Slide 10 – Referências
- ALBANO, C. S.; ZANATTA, A. L.; GARCIA, F. T. Mercado de trabalho na área de TI e a formação superior no estado do Rio Grande do Sul. *Revista Eletrônica de Sistemas de Informação*, v. 12, n. 1, 2013.
- COSTA, M. A. M.; MARTINS, H. C. Análise quantitativa da formação do estoque de mão de obra qualificada de profissionais na área de TI. *Revista Eletrônica de Sistemas de Informação*, 2016.
- INEP. Microdados do Censo da Educação Superior, 2015-2023.
- BRASIL. MTE. Relação Anual de Informações Sociais (RAIS), 2015-2023; IBGE. Estimativas de população; BASE DOS DADOS.
- **Visual:** lista simples; rodapé com o link do repositório do projeto

---

### Dicas de apresentação
- No slide 5, comece pelo boxplot e só depois mostre os números: o público vê o RN "subindo" para fora da caixa.
- No slide 6, antecipe a pergunta sobre o Wilcoxon não significativo: ele mostra justamente que o RN é um caso particular, e não a regra nacional.
- Use sempre "indícios" e "associação"; evite "causa" e "prova".
