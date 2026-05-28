import json
import os

def tratar_dados_desco():
    arquivo_bruto = "dados_produtos_desco.json"
    arquivo_limpo = "produtos_desco_tratados.json"
    
    if not os.path.exists(arquivo_bruto):
        print(f"❌ Erro: Arquivo bruto '{arquivo_bruto}' não encontrado para tratamento.")
        return

    print(f"📦 Iniciando o tratamento de dados do Desco...")
    
    with open(arquivo_bruto, "r", encoding="utf-8") as f:
        conteudo = json.load(f)
    
    # Lista onde vamos guardar os produtos limpos
    produtos_tratados = []
    
    # A API confirmou que os produtos ficam direto na lista dentro de 'data'
    lista_produtos = conteudo.get("data", [])
    
    for item in lista_produtos:
        try:
            nome = item.get("descricao", "Desconhecido").strip()
            codigo_barras = item.get("codigo_barras", "Sem EAN")
            
            # Captura o preço regular de venda
            preco_regular = float(item.get("preco", 0))
            preco_final = preco_regular
            
            # Se o item tiver uma oferta ativa, validamos o preço promocional
            if item.get("em_oferta") and item.get("oferta"):
                oferta_info = item["oferta"]
                # Pega o preço de oferta (atacado/faixa) se existir
                preco_compra = oferta_info.get("preco_oferta") or oferta_info.get("menor_preco")
                if preco_compra:
                    preco_final = float(preco_compra)
            
            # Monta o dicionário padronizado do Pudim Project
            produto_formatado = {
                "produto": nome,
                "codigo_barras": codigo_barras,
                "preco": preco_final,
                "supermercado": "Desco"
            }
            
            produtos_tratados.append(produto_formatado)
            
        except Exception as e:
            print(f"⚠️ Erro ao tratar item individual: {e}")
            continue

    # Salva o resultado final tratado
    with open(arquivo_limpo, "w", encoding="utf-8") as f:
        json.dump(produtos_tratados, f, indent=4, ensure_ascii=False)
        
    print(f"✅ Sucesso! {len(produtos_tratados)} produtos do Desco foram tratados e salvos em '{arquivo_limpo}'.")

if __name__ == "__main__":
    tratar_dados_desco()