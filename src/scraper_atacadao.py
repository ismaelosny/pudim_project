import requests
import json

def mapear_atacadao():
    print("🚀 Disparando requisição direta na API GraphQL do Atacadão...")
    
    url = "https://www.atacadao.com.br/api/graphql"
    
    # Organizando as variáveis de localização que você capturou
    variables = {
        "first": 20,
        "after": "0",
        "sort": "score_desc",
        "term": "leite condensado",
        "selectedFacets": [
            {"key": "region-id", "value": "U1cjYXRhY2FkYW9icjE0Mg=="},
            {"key": "channel", "value": "{\"salesChannel\":\"2\",\"seller\":\"atacadaobr142\",\"regionId\":\"U1cjYXRhY2FkYW9icjE0Mg==\"}"},
            {"key": "locale", "value": "pt-BR"}
        ]
    }
    
    # Parâmetros de consulta da URL limpos
    params = {
        "operationName": "ProductsQuery",
        "variables": json.dumps(variables) # O GraphQL exige o envio das variáveis como string JSON
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    
    resposta = requests.get(url, params=params, headers=headers, timeout=15)
    print(f"📡 Status da Resposta: {resposta.status_code}")
    
    if resposta.status_code == 200:
        dados_json = resposta.json()
        
        # Salvando o JSON estruturado para inspecionarmos o nó dos preços
        with open("dados_produtos_atacadao.json", "w", encoding="utf-8") as f:
            json.dump(dados_json, f, indent=4, ensure_ascii=False)
            
        print("✅ Dados salvos com sucesso no arquivo: dados_produtos_atacadao.json")
    else:
        print("❌ Falha ao acessar a API.")

if __name__ == '__main__':
    mapear_atacadao()