import json
import os
import pandas as pd

def tratar_dados_desco():
    print("⏳ A iniciar o tratamento de dados do Desco Super&Atacado...")
    
    caminho = "dados_produtos_desco.json"
    if not os.path.exists(caminho):
        print(f"❌ Ficheiro '{caminho}' não encontrado.")
        return None

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            conteudo = json.load(f)
    except Exception as e:
        print(f"❌ Erro ao ler o ficheiro JSON: {e}")
        return None

    # 💡 MATANDO O PROBLEMA: Extração ultra-defensiva passo a passo
    lista_produtos = []

    if isinstance(conteudo, list):
        # Se o JSON já for a lista direto no topo
        lista_produtos = conteudo
        
    elif isinstance(conteudo, dict):
        # Se for um dicionário, inspecionamos o que tem dentro do "data"
        campo_data = conteudo.get("data")
        campo_produtos = conteudo.get("produtos")

        if isinstance(campo_data, list):
            # Caso do Desco: {"data": [...]} -> data já é a lista!
            lista_produtos = campo_data
        elif isinstance(campo_data, dict):
            # Caso do Stok: {"data": {"produtos": [...]}}
            lista_produtos = campo_data.get("produtos", [])
        elif isinstance(campo_produtos, list):
            # Caso alternativo: {"produtos": [...]}
            lista_produtos = campo_produtos

    dados_limpos = []
    print(f"🔍 Total de itens brutos encontrados na API do Desco: {len(lista_produtos)}")

    for prod in lista_produtos:
        if not isinstance(prod, dict):
            continue
            
        nome_original = prod.get("descricao", "")
        preco_original = prod.get("preco", "0.0")
        
        # --- FILTRO TÁTICO: Manter OBRIGATORIAMENTE Leite Condensado puro ---
        nome_minusculo = nome_original.lower()
        if "leite condensado" not in nome_minusculo or "creme de leite" in nome_minusculo:
            continue

        nome_limpo = " ".join(nome_original.strip().split())

        try:
            preco_numerico = float(preco_original)
        except ValueError:
            preco_numerico = 0.0

        dados_limpos.append({
            "produto": nome_limpo,
            "preco": preco_numerico
        })

    # Criar e ordenar o DataFrame
    df_desco = pd.DataFrame(dados_limpos)
    
    if not df_desco.empty:
        df_desco = df_desco.sort_values(by="preco", ascending=True)
    
    return df_desco

if __name__ == "__main__":
    df_resultado = tratar_dados_desco()
    
    if df_resultado is not None and not df_resultado.empty:
        print("\n✅ Dados do Desco tratados com sucesso!")
        print("--------------------------------------------------")
        print(df_resultado.to_string(index=False))
        print("--------------------------------------------------")
        
        df_resultado.to_csv("desco_tratado.csv", index=False, encoding="utf-8")
        print("💾 Checkpoint gravado em 'desco_tratado.csv'")
    else:
        print("⚠️ Nenhum leite condensado passou pelos filtros.")