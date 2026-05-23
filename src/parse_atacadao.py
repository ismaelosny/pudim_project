import json

def extrair_dados_reais():
    try:
        # Lendo o arquivo JSON real enviado pelo seu script
        with open("dados_produtos_atacadao.json", "r", encoding="utf-8") as f:
            dados = json.load(f)
        
        # Caminho exato do GraphQL: data -> search -> products -> edges
        edges = dados["data"]["search"]["products"]["edges"]
        total_count = dados["data"]["search"]["products"]["pageInfo"]["totalCount"]
        
        print(f"📊 --- {total_count} PRODUTOS TRAZIDOS PELA API (NOVO HAMBURGO) --- \n")
        
        for item in edges:
            # Em GraphQL, o objeto real fica sempre dentro da chave 'node'
            produto = item["node"]
            
            nome = produto.get("name", "Sem nome")
            marca = produto.get("brand", {}).get("name", "Sem marca")
            preco = produto.get("offers", {}).get("lowPrice", 0.0)
            
            print(f"🥛 Produto: {nome}")
            print(f"🏷️  Marca:   {marca}")
            print(f"💰 Preço:   R$ {preco:.2f}")
            print("-" * 50)
            
    except FileNotFoundError:
        print("❌ Arquivo 'dados_produtos_atacadao.json' não encontrado na pasta.")
    except KeyError as e:
        print(f"❌ Erro na estrutura do JSON: Chave {e} não encontrada.")

if __name__ == '__main__':
    extrair_dados_reais()   