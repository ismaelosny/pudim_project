import json
import os
import re
import pandas as pd
from datetime import datetime

def extrair_atributos(texto):
    """
    Extrai marca, peso e tipo do produto para criar uma chave única de comparação.
    Aplica a regra de três tipos básicos, definindo 'semidesnatado' como padrão.
    """
    if not texto:
        return "produto_indefinido"
    
    # 1. Padronização primária do texto e remoção de caracteres especiais
    texto_min = texto.lower().replace(",", ".")
    texto_min = texto_min.replace("ç", "c")
    texto_min = texto_min.replace("á", "a").replace("â", "a").replace("ã", "a")
    texto_min = texto_min.replace("é", "e").replace("ê", "e")
    texto_min = texto_min.replace("í", "i").replace("ó", "o").replace("ô", "o")
    
    # 2. Isolamento do peso/volume (formato padrão ex: 395g ou 1.18kg)
    peso_match = re.search(r'(\d+(?:\.\d+)?)\s*(g|kg)', texto_min)
    peso = peso_match.group(0).replace(" ", "") if peso_match else "unidade"
    
    # 3. Classificação em três tipos básicos com base nas regras de negócio
    if "zero lactose" in texto_min or "0 lactose" in texto_min or "diet" in texto_min:
        tipo = "zero_lactose"
    elif "integral" in texto_min:
        tipo = "integral"
    else:
        tipo = "semidesnatado"
        
    # 4. Isolamento da marca com tratamento de contingência
    marca = None
    marcas_conhecidas = ["moca", "piracanjuba", "italac", "marajoara", "triangulo", "itambe", "frimesa"]
    
    for m in marcas_conhecidas:
        if m in texto_min:
            marca = m
            break
            
    # Captura a primeira palavra após o termo âncora caso a marca seja desconhecida
    if not marca:
        termo_ancora = "leite condensado "
        if termo_ancora in texto_min:
            posicao_inicial = texto_min.find(termo_ancora) + len(termo_ancora)
            trecho_restante = texto_min[posicao_inicial:]
            palavras_restantes = trecho_restante.split()
            if palavras_restantes:
                marca = palavras_restantes[0]
        
        if not marca:
            marca = "indeterminada"
        
    return f"{marca}_{tipo}_{peso}"

def extrair_atacadao():
    caminho = "dados_produtos_atacadao.json"
    produtos = []
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)
            edges = dados["data"]["search"]["products"]["edges"]
            for item in edges:
                node = item["node"]
                nome = node.get("name", "")
                preco = node.get("offers", {}).get("lowPrice", None)
                if nome and preco is not None:
                    produtos.append({
                        "chave_procura": extrair_atributos(nome),
                        "produto_atacadao": nome,
                        "preco_atacadao": float(preco)
                    })
        except Exception as e:
            print(f"⚠️ Erro ao processar Atacadão: {e}")
    return pd.DataFrame(produtos)

def extrair_stok():
    caminho = "dados_produtos_stok.json"
    produtos = []
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)
            itens = dados.get("data", {}).get("produtos", [])
            for item in itens:
                nome = item.get("descricao", "")
                preco = item.get("preco", None)
                codigo_barras = item.get("codigo_barras", "")
                if "leite condensado" in nome.lower() and "pé de moça" not in nome.lower():
                    if nome and preco is not None:
                        produtos.append({
                            "chave_procura": extrair_atributos(nome),
                            "produto_stok": nome,
                            "preco_stok": float(preco),
                            "codigo_barras": str(codigo_barras).strip()
                        })
        except Exception as e:
            print(f"⚠️ Erro ao processar Stok: {e}")
    return pd.DataFrame(produtos)

def extrair_desco():
    caminho = "dados_produtos_desco.json"
    produtos = []
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                conteudo = json.load(f)
            
            lista = conteudo if isinstance(conteudo, list) else conteudo.get("data", [])
            for item in lista:
                nome = item.get("descricao", "")
                preco = item.get("preco", None)
                codigo_barras = item.get("codigo_barras", "")
                if "leite condensado" in nome.lower() and "creme de leite" not in nome.lower():
                    if nome and preco is not None:
                        produtos.append({
                            "chave_procura": extrair_atributos(nome),
                            "produto_desco": nome,
                            "preco_desco": float(preco),
                            "codigo_barras": str(codigo_barras).strip()
                        })
        except Exception as e:
            print(f"⚠️ Erro ao processar Desco: {e}")
    return pd.DataFrame(produtos)

def consolidar_pipeline():
    print("📊 Iniciando mesclagem lógica por mapeamento de atributos...")

    df_atacadao = extrair_atacadao()
    df_stok = extrair_stok()
    df_desco = extrair_desco()

    if not df_atacadao.empty: df_atacadao = df_atacadao.drop_duplicates(subset=["chave_procura"])
    if not df_stok.empty: df_stok = df_stok.drop_duplicates(subset=["chave_procura"])
    if not df_desco.empty: df_desco = df_desco.drop_duplicates(subset=["chave_procura"])

    df_final = pd.DataFrame(columns=["chave_procura"])

    if not df_atacadao.empty:
        df_final = df_atacadao if df_final.empty else pd.merge(df_final, df_atacadao, on="chave_procura", how="outer")
    
    if not df_stok.empty:
        df_final = df_stok if df_final.empty else pd.merge(df_final, df_stok, on="chave_procura", how="outer")
        
    if not df_desco.empty:
        df_final = df_desco if df_final.empty else pd.merge(df_final, df_desco, on="chave_procura", how="outer")

    if df_final.empty or len(df_final.columns) <= 1:
        print("❌ Dados insuficientes para consolidação.")
        return

    df_final["Produto"] = df_final.get("produto_atacadao", pd.Series(dtype=str)).fillna(
        df_final.get("produto_stok", pd.Series(dtype=str))
    ).fillna(
        df_final.get("produto_desco", pd.Series(dtype=str))
    )

    col_barras_stok = df_final.get("codigo_barras_x")
    col_barras_desco = df_final.get("codigo_barras_y")
    
    if col_barras_stok is not None and col_barras_desco is not None:
        df_final["Código de Barras"] = df_final["codigo_barras_x"].fillna(df_final["codigo_barras_y"]).fillna("-")
    elif col_barras_stok is not None:
        df_final["Código de Barras"] = df_final["codigo_barras_x"].fillna("-")
    elif col_barras_desco is not None:
        df_final["Código de Barras"] = df_final["codigo_barras_y"].fillna("-")
    else:
        df_final["Código de Barras"] = "-"

    for col in ["preco_atacadao", "preco_stok", "preco_desco"]:
        if col not in df_final.columns:
            df_final[col] = None

    df_final = df_final[["Código de Barras", "Produto", "preco_atacadao", "preco_stok", "preco_desco"]]
    df_final.columns = ["Código de Barras", "Produto", "Atacadão", "Stok Center", "Desco"]
    df_final["Data da Recolha"] = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")

    # 5. Consolidação secundária de segurança por Código de Barras
    # Agrupa linhas com o mesmo código de barras válido e recupera o primeiro valor numérico não nulo
    df_validos = df_final[df_final["Código de Barras"] != "-"].copy()
    df_invalidos = df_final[df_final["Código de Barras"] == "-"].copy()

    if not df_validos.empty:
        df_validos = df_validos.groupby("Código de Barras").agg({
            "Produto": "first",
            "Atacadão": "first",
            "Stok Center": "first",
            "Desco": "first",
            "Data da Recolha": "first"
        }).reset_index()

    # Reunifica os produtos tratados com os itens sem código de barras (provenientes do Atacadão)
    df_final = pd.concat([df_validos, df_invalidos], ignore_index=True)
    df_final = df_final.sort_values(by="Produto")

    # 6. Gravação do arquivo final tratado
    ficheiro_saida = "precos_leite_condensado.csv"
    df_final.to_csv(ficheiro_saida, index=False, encoding="utf-8")
    
    print(f"✅ Consolidação final concluída. Ficheiro '{ficheiro_saida}' gerado.")
    print("\n👀 Resultado do Cruzamento de Preços:")
    print(df_final.to_string(index=False))

if __name__ == "__main__":
    consolidar_pipeline()