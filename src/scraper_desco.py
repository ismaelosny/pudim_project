from playwright.sync_api import sync_playwright
import json
import time

def mapear_desco():
    print("🚀 Iniciando navegador automatizado com Playwright para o Desco...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        controle = {"dados": {}, "capturado": False}

        def interceptar_resposta(response):
            try:
                if "services.vipcommerce.com.br" in response.url and response.status == 200:
                    dados_json = response.json()
                    conteudo_texto = json.dumps(dados_json).lower()
                    
                    # 📑 TRAVA DE SEGURANÇA: Só aceita se tiver termos de produto E for o arquivo grande (> 15kb)
                    if len(conteudo_texto) > 15000 and ("preco" in conteudo_texto or "produto" in conteudo_texto):
                        print(f"🎯 API Alvo Detetada! Tamanho ideal encontrado: {len(conteudo_texto)} caracteres.")
                        controle["dados"] = dados_json
                        controle["capturado"] = True
            except Exception:
                pass

        page.on("response", interceptar_resposta)

        # PASSO 1: Forjar Sessão na Home
        print("🏠 Acessando a Home Page do Desco...")
        page.goto("https://www.loja.desco.com.br", wait_until="domcontentloaded", timeout=45000)
        time.sleep(4)

        # PASSO 2: Ir para a categoria
        url_categoria = "https://www.loja.desco.com.br/departamentos/matinais-e-sobremesas/leite-cond-e-creme-leite"
        print("⏳ Navegando para a categoria de Leite Condensado...")
        page.goto(url_categoria, wait_until="domcontentloaded", timeout=45000)
        
        # PASSO 3: Scroll humano para forçar a API de paginação
        print("🖱️ Simulando rolagens de página para carregar os produtos na tela...")
        for i in range(3):
            page.evaluate(f"window.scrollTo(0, {500 * (i + 1)});")
            time.sleep(2)
        
        # Espera final estendida para garantir o download do pacote grande
        for _ in range(8):
            if controle["capturado"]:
                break
            time.sleep(1)

        # PASSO 4: Salvamento definitivo
        if controle["capturado"] and controle["dados"]:
            with open("dados_produtos_desco.json", "w", encoding="utf-8") as f:
                json.dump(controle["dados"], f, indent=4, ensure_ascii=False)
            print("✅ VITÓRIA! O arquivo correto 'dados_produtos_desco.json' foi gerado.")
        else:
            print("❌ Erro: O arquivo grande de produtos não foi interceptado.")

        context.close()
        browser.close()
        print("🔒 Navegador fechado de forma segura.")

if __name__ == "__main__":
    mapear_desco()