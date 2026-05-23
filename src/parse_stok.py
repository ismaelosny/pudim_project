import json
import pandas as pd

def tratar_dados_stok():
    print("⏳ A iniciar o tratamento de dados do Stok Center...")
    
    # 1. Carregar o ficheiro bruto
    try:
        with open("dados_produtos_stok.json", "r", encoding="utf-8") as f:
            conteudo = json.load(f)
    except FileNotFoundError:
        print("❌ Ficheiro 'dados_produtos_stok.json' não encontrado.")
        return None

    lista_produtos = conteudo.get("data", {}).get("produtos", [])
    dados_limpos = []

    # 2. Varrer e tratar cada produto
    for prod in lista_produtos:
        nome_original = prod.get("descricao", "")
        preco_original = prod.get("preco", "0.0")
        
        # --- TRATAMENTO 1: Filtro de Relevância ---
        # Queremos apenas leite condensado, e não doces ou misturas secundárias
        nome_minusculo = nome_original.lower()
        if "leite condensado" not in nome_minusculo or "pé de moça" in nome_minusculo:
            continue # Salta este produto irrequieto

        # --- TRATAMENTO 2: Padronização de Texto ---
        # Remove espaços duplos ou quebras de linha que possam vir do e-commerce
        nome_limpo = " ".join(nome_original.strip().split())

        # --- TRATAMENTO 3: Conversão de Tipos (String para Float) ---
        try:
            preco_numerico = float(preco_original)
        except ValueError:
            preco_numerico = 0.0 # Caso o preço venha corrompido ou vazio

        # Guardar apenas o que nos interessa para o negócio
        dados_limpos.append({
            "produto": nome_limpo,
            "preco": preco_numerico
        })

    # 3. Utilizar o Pandas para estruturar e ordenar
    df_stok = pd.DataFrame(dados_limpos)
    
    if not df_stok.empty:
        # Ordena do mais barato para o mais caro
        df_stok = df_stok.sort_values(by="preco", ascending=True)
    
    return df_stok

if __name__ == "__main__":
    df_resultado = tratar_dados_stok()
    
    if df_resultado is not None and not df_resultado.empty:
        print("\n✅ Dados do Stok Center tratados com sucesso!")
        print("--------------------------------------------------")
        # Mostrar o DataFrame formatado no ecrã
        print(df_resultado.to_string(index=False))
        print("--------------------------------------------------")
        
        # Opcional: Guardar um checkpoint apenas do Stok tratado
        df_resultado.to_csv("stok_tratado.csv", index=False, encoding="utf-8")
        print("💾 Checkpoint gravado em 'stok_tratado.csv'")
    else:
        print("⚠️ Nenhum produto passou pelo filtro de tratamento.")