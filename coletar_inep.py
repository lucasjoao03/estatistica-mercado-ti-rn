"""
Etapa 2 - Coleta do Censo da Educação Superior (INEP).

Para cada ano, baixa o .zip de microdados do INEP, lê o arquivo de cursos
(MICRODADOS_CADASTRO_CURSOS_AAAA.CSV), filtra os cursos da área geral CINE 06
(Computação e TIC) e soma ingressantes, matrículas e concluintes por UF.

Se o download automático falhar (o site do INEP às vezes recusa conexões),
baixe o .zip pelo navegador em
https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-da-educacao-superior
e coloque-o em dados/brutos/ com o nome original. O script usa o arquivo local.

Uso:
    python coletar_inep.py
Saída:
    dados/processados/inep_ti_uf_ano.csv
"""
import zipfile
from pathlib import Path

import pandas as pd

import config

# Nomes possíveis das colunas (o layout mudou levemente entre anos)
ALTERNATIVAS = {
    "SG_UF": ["SG_UF", "SG_UF_CURSO", "SG_UF_IES"],
    "CO_CINE_AREA_GERAL": ["CO_CINE_AREA_GERAL"],
    "TP_REDE": ["TP_REDE"],
    "TP_MODALIDADE_ENSINO": ["TP_MODALIDADE_ENSINO"],
    "QT_ING": ["QT_ING"],
    "QT_MAT": ["QT_MAT"],
    "QT_CONC": ["QT_CONC"],
    "QT_CONC_FEM": ["QT_CONC_FEM"],
}
QUANTIDADES = ["QT_ING", "QT_MAT", "QT_CONC", "QT_CONC_FEM"]


def _usar_certificados_do_sistema() -> None:
    """O servidor do INEP envia a cadeia de certificados incompleta. O pacote
    truststore faz o Python usar o repositório de certificados do sistema
    operacional (o mesmo do navegador), que consegue completar a cadeia.
    A verificação de segurança continua ligada."""
    try:
        import truststore
        truststore.inject_into_ssl()
    except ImportError:
        print("  Aviso: instale 'truststore' (pip install truststore) "
              "para evitar erros de certificado do INEP.")


def baixar_zip(ano: int, tentativas: int = 4) -> Path:
    destino = config.DADOS_BRUTOS / f"microdados_censo_da_educacao_superior_{ano}.zip"
    if destino.exists() and zipfile.is_zipfile(destino):
        print(f"  {ano}: usando arquivo local {destino.name}")
        return destino

    import time

    import requests

    url = config.URL_INEP.format(ano=ano)
    tmp = destino.with_suffix(".part")
    for tentativa in range(1, tentativas + 1):
        try:
            # Retoma de onde parou se a conexão caiu antes
            ja_baixado = tmp.stat().st_size if tmp.exists() else 0
            headers = {"Range": f"bytes={ja_baixado}-"} if ja_baixado else {}
            print(f"  {ano}: baixando (tentativa {tentativa}"
                  f"{f', retomando de {ja_baixado / 1e6:.0f} MB' if ja_baixado else ''})")
            with requests.get(url, stream=True, timeout=120, headers=headers) as r:
                if r.status_code == 416 and zipfile.is_zipfile(tmp):  # já estava completo
                    tmp.replace(destino)
                    return destino
                if ja_baixado and r.status_code != 206:  # servidor não aceitou retomar
                    ja_baixado = 0
                r.raise_for_status()
                with open(tmp, "ab" if ja_baixado else "wb") as f:
                    for bloco in r.iter_content(chunk_size=1 << 20):
                        f.write(bloco)
            if not zipfile.is_zipfile(tmp):
                raise IOError("arquivo baixado está incompleto ou corrompido")
            tmp.replace(destino)
            return destino
        except Exception as e:
            print(f"  {ano}: tentativa {tentativa} falhou ({type(e).__name__})")
            if tentativa == tentativas:
                raise
            time.sleep(10 * tentativa)


def ler_cursos(caminho_zip: Path) -> pd.DataFrame:
    with zipfile.ZipFile(caminho_zip) as z:
        candidatos = [
            n for n in z.namelist()
            if "CURSOS" in n.upper() and n.upper().endswith(".CSV")
        ]
        if not candidatos:
            raise FileNotFoundError(
                f"Arquivo de cursos não encontrado em {caminho_zip.name}. "
                f"Conteúdo: {z.namelist()[:20]}"
            )
        with z.open(candidatos[0]) as f:
            cabecalho = pd.read_csv(f, sep=";", encoding="latin-1", nrows=0).columns

        renomear, usar = {}, []
        for padrao, opcoes in ALTERNATIVAS.items():
            achada = next((c for c in opcoes if c in cabecalho), None)
            if achada is None:
                if padrao in ("SG_UF", "CO_CINE_AREA_GERAL", "QT_CONC"):
                    raise KeyError(f"Coluna obrigatória {padrao} ausente em {candidatos[0]}")
                continue
            usar.append(achada)
            renomear[achada] = padrao

        with z.open(candidatos[0]) as f:
            df = pd.read_csv(f, sep=";", encoding="latin-1", usecols=usar, low_memory=False)
    return df.rename(columns=renomear)


def agregar(df: pd.DataFrame, ano: int) -> pd.DataFrame:
    df["CO_CINE_AREA_GERAL"] = pd.to_numeric(df["CO_CINE_AREA_GERAL"], errors="coerce")
    ti = df[df["CO_CINE_AREA_GERAL"] == config.CINE_AREA_GERAL_TI].copy()
    for c in QUANTIDADES:
        if c not in ti:
            ti[c] = pd.NA
        ti[c] = pd.to_numeric(ti[c], errors="coerce")

    g = ti.groupby("SG_UF")
    out = pd.DataFrame({
        "cursos_ti": g.size(),
        "ingressantes_ti": g["QT_ING"].sum(min_count=1),
        "matriculas_ti": g["QT_MAT"].sum(min_count=1),
        "concluintes_ti": g["QT_CONC"].sum(min_count=1),
        "concluintes_ti_fem": g["QT_CONC_FEM"].sum(min_count=1),
    })

    # Recortes úteis para análise de robustez
    if "TP_MODALIDADE_ENSINO" in ti:
        pres = ti[pd.to_numeric(ti["TP_MODALIDADE_ENSINO"], errors="coerce") == 1]
        out["concluintes_ti_presencial"] = pres.groupby("SG_UF")["QT_CONC"].sum()
    if "TP_REDE" in ti:
        pub = ti[pd.to_numeric(ti["TP_REDE"], errors="coerce") == 1]
        out["concluintes_ti_publica"] = pub.groupby("SG_UF")["QT_CONC"].sum()

    out = out.reset_index().rename(columns={"SG_UF": "sigla_uf"})
    out.insert(0, "ano", ano)
    return out


def main() -> None:
    _usar_certificados_do_sistema()
    partes = []
    for ano in range(config.ANO_INICIO, config.ANO_FIM + 1):
        try:
            caminho = baixar_zip(ano)
            partes.append(agregar(ler_cursos(caminho), ano))
            print(f"  {ano}: OK")
        except Exception as e:  # segue para os outros anos
            print(f"  {ano}: FALHOU -> {e}")

    if not partes:
        raise SystemExit("Nenhum ano processado. Verifique os downloads.")

    df = pd.concat(partes, ignore_index=True).fillna({
        "concluintes_ti_presencial": 0, "concluintes_ti_publica": 0,
    })
    df.to_csv(config.ARQ_INEP, index=False)
    print(f"OK: {len(df)} linhas salvas em {config.ARQ_INEP}")


if __name__ == "__main__":
    main()
