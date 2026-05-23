import os
import subprocess
import streamlit as st
import pandas as pd
import sys


# 1. Configura uma variável de ambiente para forçar o Playwright a usar a pasta do projeto para o cache
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.abspath("./.playwright-cache")

# 2. Verifica se o navegador já está instalado nessa pasta fixa. Se não estiver, instala.
if not os.path.exists("./.playwright-cache"):
    with st.spinner("Instalando navegadores na nuvem... (Isso ocorre apenas uma vez)"):
        try:
            # Cria a pasta e roda a instalação apontando para ela
            os.makedirs("./.playwright-cache", exist_ok=True)
            subprocess.run(["playwright", "install", "chromium"], check=True)
            st.success("Navegador instalado com sucesso no servidor!")
        except Exception as e:
            st.error(f"Erro na instalação do navegador: {e}")

# Permite que o Python encontre os scripts dentro da pasta 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

# Importa as funções de automação dos seus scripts originais
try:
    from scraper_atacadao import mapear_atacadao  # Ajuste o nome da função se necessário
    from scraper_stok import mapear_stok          # Ajuste o nome da função se necessário
    from scraper_desco import mapear_desco
    from consolidar_tudo import consolidar_pipeline
except ImportError as e:
    st.error(f"Erro ao importar os scripts de automação: {e}")

def carregar_dados():
    try:
        # Força o Pandas a ler o arquivo mais recente do disco sem usar cache
        df = pd.read_csv("precos_leite_condensado.csv")
        return df
    except FileNotFoundError:
        return None

def extrair_marca(nome_produto):
    if not nome_produto:
        return "Outra"
    nome_min = str(nome_produto).lower()
    termo_ancora = "leite condensado "
    if termo_ancora in nome_min:
        posicao_inicial = nome_min.find(termo_ancora) + len(termo_ancora)
        trecho_restante = nome_produto[posicao_inicial:].strip()
        palavras = trecho_restante.split()
        if keywords := palavras:
            if len(keywords) > 1 and keywords[1].lower() in ["de", "da", "do"]:
                return f"{keywords[0]} {keywords[1]} {keywords[2]}".title()
            return keywords[0].title()
    return str(nome_produto).split()[0].title()

def calcular_top_3(df):
    df_tradicional = df[
        (~df["Produto"].str.lower().str.contains("integral", na=False)) & 
        (~df["Produto"].str.lower().str.contains("lactose", na=False)) &
        (~df["Produto"].str.lower().str.contains("diet", na=False))
    ].copy()
    
    if df_tradicional.empty:
        return []
        
    df_longo = df_tradicional.melt(
        id_vars=["Produto"],
        value_vars=["Atacadão", "Stok Center", "Desco"],
        var_name="Supermercado",
        value_name="Valor"
    ).dropna()
    
    df_top3 = df_longo.sort_values(by="Valor").head(3)
    
    resultados = []
    for _, linha in df_top3.iterrows():
        marca = extrair_marca(linha["Produto"])
        resultados.append({
            "marca": marca,
            "valor": linha["Valor"],
            "supermercado": linha["Supermercado"]
        })
    return resultados

def rodar_automacao_completa():
    """
    Executa sequencialmente a extração dos três mercados e consolida os dados.
    """
    print("🤖 Executando raspadores a partir da interface web...")
    
    # 1. Executa a extração em cada mercado
    mapear_atacadao()
    mapear_stok()
    mapear_desco()
    
    # 2. Executa a inteligência de tratamento e unificação
    consolidar_pipeline()

from datetime import datetime, timedelta

def construir_interface():
    st.set_page_config(page_title="Comparador de Preços", layout="wide")
    
    # Layout do cabeçalho
    col_titulo, col_botao = st.columns([4, 1])
    
    with col_titulo:
        st.title("📊 Comparador de Preços - Leite Condensado")
        st.markdown("Análise comparativa de valores praticados nos estabelecimentos Atacadão, Stok Center e Desco.")
    
    df = carregar_dados()
    
    # --- AUTOMATIZAÇÃO DE SEGUNDO PLANO ---
    # Verifica se o arquivo não existe OU se a última atualização foi há mais de 4 horas
    precisa_atualizar = False
    if df is None:
        precisa_atualizar = True
    else:
        try:
            horario_str = df["Data da Recolha"].iloc[0]
            horario_csv = datetime.strptime(horario_str, "%d/%m/%Y às %H:%M:%S")
            horario_atual = datetime.utcnow() - timedelta(hours=3) # Horário de Brasília
            
            # Se a diferença for maior que 4 horas, marca para atualizar sozinho
            if horario_atual - horario_csv > timedelta(hours=4):
                precisa_atualizar = True
        except Exception:
            precisa_atualizar = True

    # Se precisar atualizar (seja pela visita do robô ou falta de arquivo), roda o bloco
    if precisa_atualizar:
        with st.spinner("🤖 Atualização automática em segundo plano... Coletando dados novos dos mercados..."):
            try:
                rodar_automacao_completa()
                st.success("Dados atualizados automaticamente com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Falha na atualização automática: {e}")
    # --------------------------------------

    with col_botao:
        st.write("") 
        st.write("")
        # Mantemos o botão manual caso você queira forçar a barra a qualquer momento
        if st.button("🔄 Atualizar Preços", use_container_width=True):
            with st.spinner("Varrendo os mercados (isso pode levar de 1 a 2 minutos)..."):
                try:
                    rodar_automacao_completa()
                    st.success("Dados atualizados com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Falha durante a atualização: {e}")

    # Daqui para baixo o código do seu layout segue exatamente igual...
    if df is not None:
        st.markdown("---")
        st.subheader("🏆 Top 3 - Menores Preços (Leite Condensado Tradicional)")
        
        horario_coleta = df["Data da Recolha"].iloc[0] if "Data da Recolha" in df.columns else "Não identificada"
        st.caption(f"🕒 **Última verificação nos mercados:** {horario_coleta}")
        
        lista_top3 = calcular_top_3(df)
        
        if lista_top3:
            col1, col2, col3 = st.columns(3)
            colunas = [col1, col2, col3]
            for i, item in enumerate(lista_top3):
                with colunas[i]:
                    st.info(
                        f"**{i+1}º Menor Preço**\n\n"
                        f"Marca: {item['marca']}\n\n"
                        f"Valor: R$ {item['valor']:.2f}\n\n"
                        f"Estabelecimento: {item['supermercado']}"
                    )
        else:
            st.warning("Nenhum produto tradicional encontrado para calcular o Top 3.")
            
        st.markdown("---")
        
        total_itens = len(df)
        st.metric(label="Total de Itens Monitorizados", value=total_itens)
        
        termo_pesquisa = st.text_input("Filtrar tabela geral por marca ou descrição:", "")
        
        if termo_pesquisa:
            df = df[df["Produto"].str.contains(termo_pesquisa, case=False, na=False)]
        
        st.dataframe(
            df,
            column_config={
                "Código de Barras": st.column_config.TextColumn("Código de Barras"),
                "Produto": st.column_config.TextColumn("Descrição do Produto"),
                "Atacadão": st.column_config.NumberColumn("Preço Atacadão", format="R$ %.2f"),
                "Stok Center": st.column_config.NumberColumn("Preço Stok Center", format="R$ %.2f"),
                "Desco": st.column_config.NumberColumn("Preço Desco", format="R$ %.2f"),
                "Data da Recolha": st.column_config.TextColumn("Data da Recolha")
            },
            use_container_width=True,
            hide_index=True
        )
if __name__ == "__main__":
    construir_interface()