from playwright.sync_api import sync_playwright
import json
import time

def mapear_desco():
    print("🚀 Iniciando navegador automatizado com Playwright para o Desco...")
    
    with sync_playwright() as p:
        # Abre o navegador em modo escondido (headless)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        dados_capturados = {}

        # 🕵️‍♂️ Função espiã adaptada para a rota de departamentos do Desco
        def interceptar_resposta(response):
            try:
                # Mudamos o filtro para capturar a rota de departamentos da VIP Commerce
                if "departamentos/10/produtos" in response.url and response.status == 200:
                    print("🎯 API Oculta do Desco detetada no tráfego! Capturando dados...")
                    nonlocal dados_capturados
                    dados_capturados = response.json()
            except Exception as e:
                print(f"⚠️ Erro ao processar resposta de rede: {e}")

        # Ativa o monitoramento de rede
        page.on("response", interceptar_resposta)

        # URL da categoria limpa que você encontrou
        url_categoria = "https://www.loja.desco.com.br/departamentos/matinais-e-sobremesas/leite-cond-e-creme-leite"
        
        print(f"⏳ Acessando o site do Desco e aguardando o carregamento dos 22 itens...")
        page.goto(url_categoria, wait_until="networkidle", timeout=60000)
        
        # Pausa de segurança para o script de rede processar
        time.sleep(3)

        # Se a interceptação funcionou, salva o arquivo
        if dados_capturados:
            with open("dados_produtos_desco.json", "w", encoding="utf-8") as f:
                json.dump(dados_capturados, f, indent=4, ensure_ascii=False)
            print("✅ Sucesso absoluto! Arquivo 'dados_produtos_desco.json' gerado.")
        else:
            print("❌ O site carregou, mas a requisição da API do Desco não foi interceptada.")

        browser.close()
        print("🔒 Navegador fechado com segurança.")

if __name__ == "__main__":
    mapear_desco()