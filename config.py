"""
Configurações centrais do projeto.

Formação em TI (INEP) x Emprego em TI (RAIS) nas UFs brasileiras.
Edite aqui o período, as ocupações e os cursos considerados "TI".
"""
from pathlib import Path

# ---------------------------------------------------------------------------
# Pastas
# ---------------------------------------------------------------------------
RAIZ = Path(__file__).resolve().parent
DADOS_BRUTOS = RAIZ / "dados" / "brutos"
DADOS_PROC = RAIZ / "dados" / "processados"
RESULTADOS = RAIZ / "resultados"

for _p in (DADOS_BRUTOS, DADOS_PROC, RESULTADOS):
    _p.mkdir(parents=True, exist_ok=True)

# Arquivos intermediários (saída das etapas de coleta)
ARQ_RAIS = DADOS_PROC / "rais_ti_uf_ano.csv"
ARQ_INEP = DADOS_PROC / "inep_ti_uf_ano.csv"
ARQ_POP = DADOS_PROC / "populacao_uf_ano.csv"
ARQ_PAINEL = DADOS_PROC / "painel_uf_ano.csv"

# ---------------------------------------------------------------------------
# Período de análise
# ---------------------------------------------------------------------------
ANO_INICIO = 2015
ANO_FIM = 2023  # RAIS e Censo 2024 já existem; amplie se estiverem disponíveis

UF_FOCO = "RN"

# Coluna do INEP usada nos indicadores de formação (concluintes_ti_100k,
# concluintes_por_100_vinculos, defasagem e crescimento):
#   "concluintes_ti"            -> todos os cursos (presenciais + EAD)  [padrão]
#   "concluintes_ti_presencial" -> só cursos presenciais (teste de robustez EAD)
# `python analise.py --presencial` roda a versão presencial sem alterar este valor.
COLUNA_FORMACAO = "concluintes_ti"

# ---------------------------------------------------------------------------
# Base dos Dados / BigQuery
# ---------------------------------------------------------------------------
# ID do SEU projeto no Google Cloud (crie um gratuito em console.cloud.google.com)
BILLING_PROJECT_ID = "projeto-estatistica-515719"

# ---------------------------------------------------------------------------
# Definição de "ocupação de TI" (CBO 2002 - famílias de 4 dígitos)
# Justifique esta escolha na metodologia do trabalho.
# ---------------------------------------------------------------------------
CBO_TI = {
    "1425": "Gerentes de tecnologia da informação",
    "2122": "Engenheiros em computação",
    "2123": "Administradores de tecnologia da informação",
    "2124": "Analistas de tecnologia da informação",
    "3171": "Técnicos de desenvolvimento de sistemas e aplicações",
    "3172": "Técnicos em operação e monitoração de computadores",
}

# ---------------------------------------------------------------------------
# Definição de "curso de TI" no Censo da Educação Superior (CINE Brasil)
# Área geral 06 = "Computação e Tecnologias da Informação e Comunicação (TIC)"
# ---------------------------------------------------------------------------
CINE_AREA_GERAL_TI = 6

# URL dos microdados do Censo da Educação Superior (INEP)
URL_INEP = (
    "https://download.inep.gov.br/microdados/"
    "microdados_censo_da_educacao_superior_{ano}.zip"
)

# Siglas das UFs (para validação)
UFS = [
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT",
    "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO",
]
