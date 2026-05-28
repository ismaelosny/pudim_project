# --- VACINA ANTI-IPV6 ---
import socket
import requests.packages.urllib3.util.connection as urllib3_cn

def forcar_ipv4():
    return socket.AF_INET

urllib3_cn.allowed_gai_family = forcar_ipv4
# --------------------------------------------------

import time
import requests
import json
import os
import re
import pandas as pd

# 🛠️ Importação dos seus scrapers e pipeline de consolidação
from scraper_atacadao import mapear_atacadao
from scraper_stok import mapear_stok
from scraper_desco import mapear_desco
from consolidar_tudo import consolidar_pipeline

# 📍 Descobre automaticamente o caminho absoluto da pasta onde este script está (pasta 'src')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def carregar_config():
    caminho_config = os.path.join(BASE_DIR, "config_pudim.json")
    with open(caminho_config, "r", encoding="utf-8") as f:
        return json.load(f)

def ler_e_formatar_comparativo():
    """Lê o CSV, limpa os nomes dos produtos, filtra os 10 mais baratos e ordena crescente."""
    caminho_src = os.path.join(BASE_DIR, "precos_leite_condensado.csv")
    caminho_raiz = os.path.join(os.path.dirname(BASE_DIR), "precos_leite_condensado.csv")
    caminho_relativo = "precos_leite_condensado.csv"
    
    if os.path.exists(caminho_src):
        ficheiro_csv = caminho_src
    elif os.path.exists(caminho_raiz):
        ficheiro_csv = caminho_raiz
    elif os.path.exists(caminho_relativo):
        ficheiro_csv = caminho_relativo
    else:
        return "❌ Erro: O arquivo 'precos_leite_condensado.csv' não foi encontrado nem na pasta 'src' nem na raiz do projeto."
    
    try:
        df = pd.read_csv(ficheiro_csv)
        if df.empty:
            return "📭 O arquivo de preços está vazio."
            
        ofertas = []
        
        for _, row in df.iterrows():
            produto = row["Produto"]
            
            # ✂️ Limpeza do Texto: Remove a expressão "leite condensado" ignorando maiúsculas/minúsculas
            produto_limpo = re.sub(r'(?i)leite\s+condensado\s*', '', produto).strip()
            if produto_limpo:
                # Garante que a primeira letra do nome da marca/tipo continue maiúscula
                produto_limpo = produto_limpo[0].upper() + produto_limpo[1:]
            
            for loja in ["Atacadão", "Stok Center", "Desco"]:
                if loja in df.columns and pd.notna(row[loja]):
                    preco = float(row[loja])
                    if preco > 0:
                        ofertas.append({
                            "preco": preco,
                            "texto": f"R$ {preco:.2f} {produto_limpo}, no {loja}"
                        })
        
        if not ofertas:
            return "📭 Nenhuma oferta válida encontrada no arquivo."
            
        # 📈 ORDENAÇÃO CRESCENTE: Do menor preço para o maior preço
        ofertas_crescentes = sorted(ofertas, key=lambda x: x["preco"])
        
        # Separa as 10 melhores ofertas absolutas (já ordenadas do mais barato para o mais caro)
        top_10_crescente = ofertas_crescentes[:10]
        
        # Montagem da resposta limpa de texto
        texto = "📋 *TOP 10 MELHORES OFERTAS ENCONTRADAS* 📋\n"
        texto += f"📅 _Coleta: {df['Data da Recolha'].iloc[0]}_\n\n"
        
        for item in top_10_crescente:
            texto += f"{item['texto']}\n"
            
        return texto

    except Exception as e:
        return f"⚠️ Erro ao processar e formatar o Top 10: {e}"

def escutar_telegram():
    config = carregar_config()
    token = config["telegram_token"]
    master_id = str(config["master_id"])
    
    url_base = f"https://api.telegram.org/bot{token}/"
    offset = 0
    
    print("🤖 [INFO] Iniciando rotina do Pudim Project...")
    print("📡 [REDE] Testando conexão e Token com o servidor do Telegram...")
    
    try:
        teste_conexao = requests.get(f"{url_base}getMe", timeout=5).json()
        if teste_conexao.get("ok"):
            print(f"✅ [SUCESSO] Bot conectado e ativo: @{teste_conexao['result']['username']}")
        else:
            print(f"❌ [ERRO] Token rejeitado: {teste_conexao.get('description')}")
    except Exception as e:
        print(f"❌ [ERRO] Falha física de rede ao conectar com o Telegram: {e}")

    print("🎧 [ESCUTA] Loop de monitoramento iniciado. Aguardando mensagens no celular...")
    
    while True:
        try:
            url = f"{url_base}getUpdates?offset={offset}&timeout=5"
            resposta = requests.get(url, timeout=10).json()
            
            if "result" in resposta:
                for update in resposta["result"]:
                    offset = update["update_id"] + 1
                    
                    if "message" in update and "text" in update["message"]:
                        chat_id = str(update["message"]["chat"]["id"])
                        texto_recebido = update["message"]["text"].strip().lower()
                        user_nome = update["message"]["from"].get("first_name", "Usuário")
                        
                        print(f"📩 [MENSAGEM] Recebida de {user_nome} (ID: {chat_id}): '{texto_recebido}'")
                        
                        if chat_id != master_id:
                            print(f"⛔ [BLOQUEADO] ID {chat_id} não autorizado.")
                            continue
                            
                        if texto_recebido in ["/pudim", "pudim", "/comparar", "comparar"]:
                            print("\n⚡ [EXECUÇÃO] Comando válido recebido! Disparando pipeline...")
                            
                            requests.post(f"{url_base}sendMessage", json={
                                "chat_id": chat_id, 
                                "text": "🏭 *Iniciando Mapeamento dos Atacados...*\n\nAguarde um momento enquanto processo os dados locais.",
                                "parse_mode": "Markdown"
                            }, timeout=5)
                            
                            try:
                                print("   -> Processando Atacadão...")
                                mapear_atacadao()
                                print("   -> Processando Stok Center...")
                                mapear_stok()
                                print("   -> Processando Desco Atacado...")
                                mapear_desco()
                                print("   -> Executando consolidar_tudo.py...")
                                consolidar_pipeline()
                                
                                mensagem_comparativa = ler_e_formatar_comparativo()
                            except Exception as pipeline_error:
                                mensagem_comparativa = f"❌ Erro na execução dos scripts locais: {pipeline_error}"
                            
                            requests.post(f"{url_base}sendMessage", json={
                                "chat_id": chat_id, 
                                "text": mensagem_comparativa, 
                                "parse_mode": "Markdown"
                            }, timeout=5)
                            print("✅ [OK] Relatório entregue ao usuário.")
                            
        except Exception as e:
            print(f"⚠️ Alerta no loop de leitura: {e}")
            
        time.sleep(1)

if __name__ == "__main__":
    escutar_telegram()