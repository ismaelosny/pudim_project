import requests
import json
import re

def extrair_precos_stok_automatico():
    print("🚀 Iniciando sessão automática no Stok Center...")
    session = requests.Session()
    
    # Cabeçalhos padrão para parecer um navegador real
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8"
    }
    
    # Passo 1: Acessa a página inicial para o servidor gerar os cookies e registrar a conexão
    print("⏳ Acessando a página inicial para coletar cookies do servidor...")
    pag_inicial = session.get("https://www.stokonline.com.br/", headers=headers, timeout=15)
    
    # Passo 2: Configuramos os cabeçalhos específicos que a API exige
    api_headers = {
        "User-Agent": headers["User-Agent"],
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": headers["Accept-Language"],
        "Origin": "https://www.stokonline.com.br",
        "Referer": "https://www.stokonline.com.br/"
    }
    
    # Passo 3: Disparada direta utilizando a URL da sua região (Centro de Distribuição 17)
    # Deixamos o parâmetro session vazio para ver se a API aceita a validação apenas pelos cookies gerados no Passo 1
    url = "https://services.vipcommerce.com.br/api-admin/v1/org/130/filial/1/centro_distribuicao/17/loja/buscas/produtos/termo/leite+condensado"
    params = {
        "page": "1",
        "session": "" 
    }
    
    print("📡 Disparando requisição contra a API de produtos...")
    resposta = session.get(url, params=params, headers=api_headers, timeout=15)
    
    print(f"📡 Status da Resposta da API: {resposta.status_code}")
    
    if resposta.status_code == 200:
        with open("dados_produtos_stok.json", "w", encoding="utf-8") as f:
            json.dump(resposta.json(), f, indent=4, ensure_ascii=False)
        print("✅ Sucesso! O arquivo 'dados_produtos_stok.json' foi gerado automaticamente.")
    else:
        print(f"❌ O servidor rejeitou o acesso automatizado simples (Status {resposta.status_code}).")

if __name__ == '__main__':
    extrair_precos_stok_automatico()