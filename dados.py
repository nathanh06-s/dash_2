import pandas as pd

# Define tipo de unidade com base no prefixo
def tipo_unidade(filial):
    if pd.isna(filial):
        return None
    if str(filial).startswith("01"):
        return "Hospital"
    elif str(filial).startswith("02"):
        return "Operadora"
    return None

# Define tipo de NF com base no conteúdo ou na base
def tipo_nf(base, valor):
    if base in ["regularizacao", "lancamento"]:
        valor = str(valor).upper().strip()
        if valor == "NFS":
            return "Serviço"
        elif valor == "NF":
            return "Produto"
    return "Serviço"

# Lista de arquivos .xlsx
arquivos = {
    "aba": "aba.xlsx",
    "comissao": "comissao.xlsx",
    "comweb": "comweb.xlsx",
    "lancamento": "lancamento.xlsx",
    "odonto": "odonto.xlsx",
    "opme": "opme.xlsx",
    "regularizacao": "regularizacao.xlsx",
    "repasse": "repasse.xlsx",
    "repeventuais": "repeventuais.xlsx",
    "repnip": "repnip.xlsx",
    "websolus": "websolus.xlsx"
}

# Colunas que vamos usar (todas as bases agora têm Regional)
colunas_utilizadas = ["Descrição", "Filial - H/O", "Início", "Requisitante", "Regional", "NF Servico/Produto", "Situação"]

lista_df = []

# Passo extra: gerar mapeamento de nome da unidade → tipo (base lancamento)
mapeamento_tipo_unidade = {}
try:
    df_ref = pd.read_excel("lancamento.xlsx", usecols=lambda col: col in colunas_utilizadas)
    df_ref = df_ref[df_ref["Filial - H/O"].notna()]
    df_ref["Nome_Limpo"] = df_ref["Filial - H/O"].str.split(" - ", n=1).str[1].str.strip()
    df_ref["Tipo_Unidade"] = df_ref["Filial - H/O"].apply(tipo_unidade)
    mapeamento_tipo_unidade = df_ref.dropna(subset=["Nome_Limpo", "Tipo_Unidade"]) \
        .drop_duplicates(subset=["Nome_Limpo"]) \
        .set_index("Nome_Limpo")["Tipo_Unidade"].to_dict()
except Exception as e:
    print("[ERRO] Falha ao gerar mapeamento de tipo de unidade:", e)

# Processa todas as bases
for nome_base, arquivo in arquivos.items():
    try:
        df = pd.read_excel(arquivo, usecols=lambda col: col in colunas_utilizadas)
        df["Base"] = nome_base
        df["Fluxo"] = df["Descrição"]

        # Tipo de unidade — bases com prefixo numérico
        if nome_base not in ["comweb", "websolus"]:
            df["Tipo_Unidade"] = df["Filial - H/O"].apply(tipo_unidade)
        else:
            # Usa nome da unidade como chave de mapeamento
            df["Nome_Limpo"] = df["Filial - H/O"].str.strip()
            df["Tipo_Unidade"] = df["Nome_Limpo"].map(mapeamento_tipo_unidade)

        # Tipo de NF
        if "NF Servico/Produto" in df.columns:
            df["Tipo_NF"] = df["NF Servico/Produto"].apply(lambda x: tipo_nf(nome_base, x))
        else:
            df["Tipo_NF"] = "Serviço"

        # Mês (nome em português)
        df["Mes"] = pd.to_datetime(df["Início"], dayfirst=True, errors='coerce').dt.month_name(locale="pt_BR")

        lista_df.append(df)

    except Exception as e:
        print(f"[ERRO] Erro ao ler {arquivo}: {e}")

# Junta tudo num único DataFrame
if lista_df:
    df_geral = pd.concat(lista_df, ignore_index=True)
else:
    print("[ERRO FATAL] Nenhum dataframe foi carregado. Verifique os arquivos .xlsx.")
    df_geral = pd.DataFrame()  # previne falha total no app.py

# ✅ Forçar conversão da coluna "Início" para datetime no df_geral final
df_geral["Início"] = pd.to_datetime(df_geral["Início"], dayfirst=True, errors="coerce")

# Debug opcional
if __name__ == "__main__":
    print("Total de linhas:", len(df_geral))
    print("Colunas:", df_geral.columns.tolist())
    print("\n[CHECK] Linhas por regional:")
    print(df_geral["Regional"].value_counts(dropna=False))
    print("\n[CHECK] Linhas sem Tipo_Unidade:")
    print(df_geral[df_geral["Tipo_Unidade"].isna()][["Base", "Filial - H/O"]].drop_duplicates().head(20))