import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import os
from fpdf import FPDF

# Configuração da página
st.set_page_config(
    page_title="📱 BR Veículos - Controle de Vendas", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS customizado para layout responsivo e moderno
st.markdown("""
<style>
    /* Reset e configurações gerais */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 500px;
    }
    
    /* Seção de filtros */
    .filters-section {
        background: #f8f9ff;
        padding: 15px;
        border-radius: 15px;
        border: 2px solid #e3e8ff;
        margin-bottom: 20px;
    }
    
    .filters-title {
        font-size: 14px;
        font-weight: 600;
        color: #2E73B5;
        margin-bottom: 10px;
    }
    
    /* Seção do formulário */
    .form-section {
        background: #f0f8ff;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #d4edda;
        margin-bottom: 20px;
    }
    
    .form-title {
        font-size: 16px;
        font-weight: 600;
        color: #2E73B5;
        margin-bottom: 15px;
    }
    
    /* Estatísticas */
    .stats-container {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.2);
    }
    
    .stat-item {
        background: rgba(255,255,255,0.2);
        padding: 15px;
        border-radius: 10px;
        margin: 5px;
    }
    
    .stat-value {
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 5px;
    }
    
    .stat-label {
        font-size: 12px;
        opacity: 0.9;
    }
    
    /* Cards de vendas */
    .sale-card {
        background: white;
        border: 2px solid #e3e8ff;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .sale-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
    }
    
    .sale-header {
        font-weight: 600;
        color: #2E73B5;
        margin-bottom: 5px;
    }
    
    .sale-date {
        font-size: 12px;
        color: #666;
    }
    
    /* Seção de exportação */
    .export-section {
        background: #fff3cd;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #ffeaa7;
    }
    
    .export-title {
        font-size: 16px;
        font-weight: 600;
        color: #856404;
        margin-bottom: 15px;
    }
    
    /* Botões customizados */
    .stButton > button {
        border-radius: 10px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    /* Botão de exclusão */
    .delete-btn {
        background: #ffebee !important;
        color: #f44336 !important;
        border: 2px solid #ffcdd2 !important;
        border-radius: 8px !important;
        padding: 8px !important;
        font-size: 16px !important;
    }
    
    .delete-btn:hover {
        background: #f44336 !important;
        color: white !important;
    }
    
    /* Responsividade */
    @media (max-width: 500px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
    
    /* Customização do file uploader */
    .stFileUploader > div > div > div > div {
        background: #f8f9ff;
        border: 2px dashed #2E73B5;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar estado de sessão
if "reset_form" not in st.session_state:
    st.session_state.reset_form = False

# Header com logomarca centralizada (sem faixa azul)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("br_veiculos.png", width=200)

st.markdown("""
<div style="text-align: center; margin-bottom: 30px;">
    <h1 style="color: #2E73B5; font-size: 24px; margin: 10px 0;">📊 Controle de Vendas de Veículos-João Felipe</h1>
</div>
""", unsafe_allow_html=True)

# Função para carregar e converter datas de forma segura
def carregar_dados_csv():
    try:
        df = pd.read_csv("vendas.csv")
        if not df.empty:
            df["data"] = pd.to_datetime(df["data"], format='mixed', dayfirst=True)
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["data", "modelo", "imagem"])
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame(columns=["data", "modelo", "imagem"])

# Função para excluir venda
def excluir_venda(index_para_excluir):
    try:
        df_atual = carregar_dados_csv()
        if not df_atual.empty and index_para_excluir < len(df_atual):
            imagem_path = df_atual.iloc[index_para_excluir]["imagem"]
            if os.path.exists(imagem_path):
                try:
                    os.remove(imagem_path)
                except:
                    pass
            
            df_atual = df_atual.drop(index_para_excluir).reset_index(drop=True)
            
            df_temp = df_atual.copy()
            if not df_temp.empty:
                df_temp["data"] = df_atual["data"].dt.strftime('%d/%m/%Y')
            df_temp.to_csv("vendas.csv", index=False)
            
            return True
    except Exception as e:
        st.error(f"Erro ao excluir venda: {e}")
    return False

# Carregar dados existentes
df = carregar_dados_csv()

# Configuração de datas
meses = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

mes_atual = datetime.today().month
ano_atual = datetime.today().year

if not df.empty:
    anos_disponiveis = sorted(df["data"].dt.year.unique(), reverse=True)
else:
    anos_disponiveis = [ano_atual]

# 📅 SEÇÃO DE FILTROS - Layout responsivo
st.markdown('<div class="filters-section">', unsafe_allow_html=True)
st.markdown('<div class="filters-title">📅 Filtros de Período</div>', unsafe_allow_html=True)

col_ano, col_mes = st.columns(2)
with col_ano:
    filtro_ano = st.selectbox("Ano", anos_disponiveis, index=0, key="filtro_ano")
with col_mes:
    nome_mes = st.selectbox("Mês", list(meses.values()), index=mes_atual - 1, key="filtro_mes")
    filtro_mes = [k for k, v in meses.items() if v == nome_mes][0]

st.markdown('</div>', unsafe_allow_html=True)

# ➕ SEÇÃO DO FORMULÁRIO
st.markdown('<div class="form-section">', unsafe_allow_html=True)
st.markdown('<div class="form-title">➕ Nova Venda</div>', unsafe_allow_html=True)

with st.form("form_venda", clear_on_submit=True):
    imagem = st.file_uploader("📷 Foto do veículo", type=["jpg", "jpeg", "png"])
    data_venda = st.date_input("📅 Data da venda", value=datetime.today())
    modelo = st.text_input("🚗 Modelo do veículo", placeholder="Ex: Honda Civic 2020")
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        enviar = st.form_submit_button("💾 Salvar Venda", use_container_width=True)

    if enviar and imagem and modelo:
        path = f"imagens/{imagem.name}"
        os.makedirs("imagens", exist_ok=True)
        with open(path, "wb") as f:
            f.write(imagem.getbuffer())
        nova_linha = pd.DataFrame([{
            "data": data_venda.strftime('%d/%m/%Y'),
            "modelo": modelo,
            "imagem": path
        }])

        df_existente = carregar_dados_csv()
        nova_linha["data"] = pd.to_datetime(nova_linha["data"], format='%d/%m/%Y')
        df_final = pd.concat([df_existente, nova_linha], ignore_index=True)
        
        df_temp = df_final.copy()
        df_temp["data"] = df_final["data"].dt.strftime('%d/%m/%Y')
        df_temp.to_csv("vendas.csv", index=False)
        
        st.success("✅ Venda salva com sucesso!")
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# 📊 SEÇÃO DE ESTATÍSTICAS
if not df.empty:
    df_filtrado = df[(df["data"].dt.month == filtro_mes) & (df["data"].dt.year == filtro_ano)]
    qtd = len(df_filtrado)
    
    if qtd <= 5:
        comissao = qtd * 250
    elif qtd <= 10:
        comissao = qtd * 300
    elif qtd <= 15:
        comissao = qtd * 350
    else:
        comissao = qtd * 400

    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
    
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.markdown(f'''
        <div class="stat-item">
            <div class="stat-value">{qtd}</div>
            <div class="stat-label">Vendas este mês</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col_stat2:
        st.markdown(f'''
        <div class="stat-item">
            <div class="stat-value">R$ {comissao:,.0f}</div>
            <div class="stat-label">Comissão total</div>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # 📋 SEÇÃO DE VENDAS
    st.markdown(f"### 📋 Vendas de {nome_mes}/{filtro_ano}")
    
    if not df_filtrado.empty:
        for index, (original_index, row) in enumerate(df_filtrado.iterrows()):
            data_formatada = row["data"].strftime("%d/%m/%Y")
            
            # Layout do card de venda
            col_card, col_delete = st.columns([5, 1])
            
            with col_card:
                with st.expander(f"📅 {data_formatada} - 🚗 {row['modelo']}", expanded=False):
                    if os.path.exists(row["imagem"]):
                        st.image(row["imagem"], width=300, caption=f"📷 {row['modelo']}")
                    else:
                        st.warning("⚠️ Imagem não encontrada")
            
            with col_delete:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"delete_{original_index}", help="Excluir esta venda"):
                    if excluir_venda(original_index):
                        st.success("✅ Venda excluída!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao excluir!")
    else:
        st.info("📭 Nenhuma venda encontrada para este período.")
else:
    st.info("📭 Nenhuma venda cadastrada ainda. Comece adicionando sua primeira venda!")

# Função para gerar PDF
def gerar_pdf_vendas(df_filtrado, filtro_mes, filtro_ano, caminho="relatorio_vendas.pdf"):
    meses = {
        1: "Janeiro", 2: "Fevereiro", 3: "Marco", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    if os.path.exists("br_veiculos.png"):
        try:
            logo_x = (210 - 40) / 2
            pdf.image("br_veiculos.png", x=logo_x, y=10, w=40)
            pdf.ln(30)
        except:
            pass
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Relatorio de Vendas João Felipe - {meses[filtro_mes]}/{filtro_ano}", ln=True, align="C")
    pdf.ln(10)

    qtd = len(df_filtrado)
    if qtd <= 5:
        comissao = qtd * 250
    elif qtd <= 10:
        comissao = qtd * 300
    elif qtd <= 15:
        comissao = qtd * 350
    else:
        comissao = qtd * 400

    for index, (_, row) in enumerate(df_filtrado.iterrows()):
        data = row["data"].strftime("%d/%m/%Y")
        modelo = row["modelo"]
        imagem = row["imagem"]
        
        if pdf.get_y() > 250:
            pdf.add_page()
        
        y_inicial = pdf.get_y()
        
        if os.path.exists(imagem):
            try:
                pdf.image(imagem, x=15, y=y_inicial, w=35, h=25)
            except:
                pdf.rect(15, y_inicial, 35, 25)
                pdf.set_xy(20, y_inicial + 10)
                pdf.set_font("Arial", "", 8)
                pdf.cell(25, 5, "Imagem", align="C")
        else:
            pdf.rect(15, y_inicial, 35, 25)
            pdf.set_xy(20, y_inicial + 10)
            pdf.set_font("Arial", "", 8)
            pdf.cell(25, 5, "Sem imagem", align="C")
        
        pdf.set_xy(55, y_inicial + 3)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, f"Data: {data}", ln=True)
        
        pdf.set_x(55)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 8, f"Modelo: {modelo}", ln=True)
        
        pdf.set_x(55)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 6, f"Venda #{index + 1}", ln=True)
        
        pdf.ln(8)
    
    pdf.ln(10)
    pdf.set_draw_color(46, 115, 181)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(46, 115, 181)
    pdf.cell(0, 10, f"Total de veiculos vendidos: {qtd}", ln=True, align="C")
    
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(0, 128, 0)
    pdf.cell(0, 10, f"Comissao total: R$ {comissao:,.2f}", ln=True, align="C")
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)
    pdf.set_font("Arial", "", 8)
    pdf.set_text_color(128, 128, 128)
    data_geracao = datetime.now().strftime("%d/%m/%Y as %H:%M")
    pdf.cell(0, 5, f"Relatorio gerado em {data_geracao}", ln=True, align="C")

    pdf.output(caminho)
    return caminho

# 📤 SEÇÃO DE EXPORTAÇÃO
st.markdown('<div class="export-section">', unsafe_allow_html=True)
st.markdown('<div class="export-title">📤 Exportar Relatório</div>', unsafe_allow_html=True)

if not df.empty:
    col_exp_ano, col_exp_mes = st.columns(2)
    with col_exp_ano:
        export_ano = st.selectbox("Ano", sorted(df["data"].dt.year.unique(), reverse=True), key="export_ano")
    with col_exp_mes:
        export_mes_nome = st.selectbox("Mês", list(meses.values()), index=mes_atual - 1, key="export_mes")
        export_mes = [k for k, v in meses.items() if v == export_mes_nome][0]

    df_export = df[(df["data"].dt.month == export_mes) & (df["data"].dt.year == export_ano)]

    col_pdf1, col_pdf2, col_pdf3 = st.columns([1, 2, 1])
    with col_pdf2:
        if st.button("📄 Gerar PDF", use_container_width=True):
            if not df_export.empty:
                caminho_pdf = f"relatorio_vendas_{export_mes:02d}_{export_ano}.pdf"
                gerar_pdf_vendas(df_export, export_mes, export_ano, caminho=caminho_pdf)
                with open(caminho_pdf, "rb") as f:
                    st.download_button("📥 Baixar PDF", f, file_name=caminho_pdf, use_container_width=True)
            else:
                st.warning("❌ Nenhuma venda encontrada para o período selecionado.")
else:
    st.info("📭 Nenhum dado disponível para exportar.")

st.markdown('</div>', unsafe_allow_html=True)