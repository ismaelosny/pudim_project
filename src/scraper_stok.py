from playwright.sync_api import sync_playwright
import json
import time

def mapear_stok():
    print("🚀 Iniciando navegador automatizado com Playwright...")
    
    with sync_playwright() as p:
        # Abre o navegador em modo 'headless' (escondido)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Variável para guardar o JSON assim que ele for interceptado
        dados_capturados = {}

        # O PULO DO GATO: Função que inspeciona todas as respostas de rede do site
        def interceptar_resposta(response):
            try:
                # 💡 Correção aqui: usamos response.status em vez de response.status_code
                if "loja/buscas/produtos/termo/" in response.url and response.status == 200:
                    print("🎯 API Oculta Detectada no tráfego! Capturando dados...")
                    nonlocal dados_capturados
                    dados_capturados = response.json()
            except Exception as e:
                # Evita que qualquer erro interno trave o fechamento do navegador
                print(f"⚠️ Erro ao processar resposta de rede: {e}")

        # Dizemos para a página monitorar todas as respostas de rede
        page.on("response", interceptar_resposta)

        # URL exata que você usou no navegador (já com o CD 17 da sua região)
        url_busca = "https://www.stokonline.com.br/busca?termo=leite%20condensado"
        
        print(f"⏳ Acessando o site e aguardando o carregamento dos preços...")
        page.goto(url_busca, wait_until="networkidle", timeout=60000)
        
        # Damos uma pequena pausa de segurança para garantir que o script de rede processou tudo
        time.sleep(3)

        # Se conseguimos interceptar o JSON com sucesso
        if dados_capturados:
            with open("dados_produtos_stok.json", "w", encoding="utf-8") as f:
                json.dump(dados_capturados, f, indent=4, ensure_ascii=False)
            print("✅ Sucesso absoluto! Arquivo 'dados_produtos_stok.json' gerado com dados reais.")
        else:
            print("❌ O site carregou, mas a requisição da API não foi interceptada.")

        browser.close()
        print("🔒 Navegador fechado com segurança.")

if __name__ == "__main__":
    mapear_stok()