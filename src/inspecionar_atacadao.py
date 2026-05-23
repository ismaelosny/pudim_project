from playwright.sync_api import sync_playwright
import re
import json

def inspecionar_rede_atacadao():
    print("🚀 Iniciando análise de tráfego total no Atacadão...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Expressão regular para identificar códigos EAN-13 brasileiros (começam com 789 seguidos de 10 dígitos)
        padrao_ean = re.compile(r'\b789\d{10}\b')
        
        requisicoes_com_ean = []

        def analisar_resposta(response):
            try:
                # Filtra apenas requisições que retornam dados do tipo JSON
                content_type = response.headers().get("content-type", "").lower()
                if "application/json" in content_type or "json" in response.url:
                    texto_resposta = response.text()
                    
                    # Busca ocorrências do padrão EAN-13 no texto bruto do JSON
                    encontrados = padrao_ean.findall(texto_resposta)
                    
                    if encontrados:
                        requisicoes_com_ean.append({
                            "url": response.url,
                            "codigos_detectados": list(set(encontrados))
                        })
                        print(f"🎯 Padrão EAN detectado na URL: {response.url[:80]}...")
            except Exception:
                # Ignora falhas de leitura de requisições assíncronas que fecham antes do término
                pass

        # Define o ouvinte para interceptar todas as respostas de rede
        page.on("response", analisar_resposta)

        url_busca = "https://www.atacadao.com.br/busca?termo=leite%20condensado"
        
        print("⏳ Carregando a página e varrendo requisições de fundo...")
        page.goto(url_busca, wait_until="networkidle", timeout=60000)
        
        browser.close()
        print("🔒 Análise de rede concluída.")
        
        # Exibe os resultados obtidos
        if requisicoes_com_ean:
            print("\n📊 --- RELATÓRIO DE REQUISIÇÕES COM EAN-13 ---")
            with open("log_trafego_atacadao.json", "w", encoding="utf-8") as f:
                json.dump(requisicoes_com_ean, f, indent=4, ensure_ascii=False)
            
            for item in requisicoes_com_ean:
                print(f"\nURL: {item['url']}")
                print(f"Códigos encontrados: {item['codigos_detectados']}")
            print("\n💾 Detalhes salvos em 'log_trafego_atacadao.json'")
        else:
            print("\n❌ Nenhuma das requisições JSON trafegadas continha códigos no padrão EAN-13 (789xxxxxxxxxx).")

if __name__ == "__main__":
    inspecionar_rede_atacadao()