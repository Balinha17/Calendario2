import streamlit as st
import pandas as pd
import base64
from pathlib import Path
from html import escape

st.set_page_config(page_title="Calendário de Ações", layout="wide")

ARQUIVO_EXCEL = "Calendário2.xlsx"
LOGO_PATH = "logo_pucrs.png"

df = pd.read_excel(ARQUIVO_EXCEL)
df.columns = df.columns.str.strip()

df = df[["Data", "Área", "Ação sobre", "Observação"]].copy()
df = df.dropna(subset=["Data", "Área", "Ação sobre"])
df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
df = df.dropna(subset=["Data"])
df = df.sort_values("Data")

def img_to_base64(path):
    if Path(path).exists():
        with open(path, "rb") as img:
            return base64.b64encode(img.read()).decode()
    return None

logo_b64 = img_to_base64(LOGO_PATH)

cores = {
    "CRÉDITOS": "#17A65B",
    "FATURAMENTO": "#6F2DBD",
    "COBRANÇA": "#FF8C00",
    "RELACIONAMENTO": "#0077FF",
    "GRADUAÇÃO ONLINE": "#00A6D6",
    "PÓS ONLINE": "#001B5E",
    "ANÁLISE": "#0077FF",
}

st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.header {
    background: linear-gradient(90deg, #00133F, #004AAD);
    border-radius: 24px;
    padding: 34px 42px;
    color: white;
    margin-bottom: 28px;
    box-shadow: 0 8px 24px rgba(0, 27, 94, 0.25);
}

.header-top {
    display: flex;
    align-items: center;
    gap: 28px;
}

.logo-img {
    max-height: 76px;
    max-width: 190px;
}

.logo-text {
    font-size: 30px;
    font-weight: 900;
    letter-spacing: 1px;
}

.header-divider {
    height: 72px;
    width: 2px;
    background: rgba(255,255,255,0.45);
}

.header-label {
    font-size: 24px;
    font-weight: 700;
    opacity: 0.95;
}

.header-title {
    font-size: 54px;
    font-weight: 950;
    line-height: 1;
    margin-top: 6px;
}

.header-subtitle {
    font-size: 21px;
    color: #8FDBFF;
    margin-top: 12px;
}

.kpi-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 18px;
    margin-bottom: 28px;
}

.kpi-card {
    background: white;
    border: 1px solid #D9E2F1;
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0 5px 18px rgba(0,0,0,0.06);
}

.kpi-label {
    color: #001B5E;
    font-size: 15px;
    font-weight: 800;
    text-transform: uppercase;
}

.kpi-number {
    color: #0077FF;
    font-size: 42px;
    font-weight: 950;
    margin-top: 4px;
}

.area-card {
    background: white;
    border: 1px solid #D9E2F1;
    border-radius: 22px;
    padding: 22px;
    min-height: 500px;
    box-shadow: 0 5px 18px rgba(0,0,0,0.07);
    margin-bottom: 24px;
}

.area-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 18px;
}

.area-title {
    font-size: 24px;
    font-weight: 950;
    color: #001B5E;
}

.area-count {
    color: white;
    border-radius: 999px;
    padding: 6px 14px;
    font-size: 14px;
    font-weight: 800;
}

.action-item {
    border-top: 1px solid #EEF2F8;
    padding: 14px 0;
}

.date-pill {
    display: inline-block;
    color: white;
    padding: 5px 12px;
    border-radius: 999px;
    font-weight: 900;
    font-size: 13px;
    margin-right: 8px;
}

.action-title {
    font-size: 15px;
    font-weight: 850;
    color: #00133F;
}

.obs {
    margin-top: 7px;
    font-size: 14px;
    color: #3B465A;
    line-height: 1.35;
}

.footer {
    background: #001B5E;
    color: white;
    padding: 20px 26px;
    border-radius: 18px;
    margin-top: 14px;
    font-size: 15px;
}
</style>
""", unsafe_allow_html=True)

if logo_b64:
    logo_html = f'<img class="logo-img" src="data:image/png;base64,{logo_b64}">'
else:
    logo_html = '<div class="logo-text">PUCRS</div>'

st.markdown(f"""
<div class="header">
    <div class="header-top">
        {logo_html}
        <div class="header-divider"></div>
        <div>
            <div class="header-label">ESTRUTURA DO SETOR FINANCEIRO</div>
            <div class="header-title">CALENDÁRIO DE AÇÕES</div>
            <div class="header-subtitle">Acompanhamento das ações por área</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

total_acoes = len(df)
total_areas = df["Área"].nunique()
primeira_data = df["Data"].min().strftime("%d/%m/%Y")
ultima_data = df["Data"].max().strftime("%d/%m/%Y")

st.markdown(f"""
<div class="kpi-row">
    <div class="kpi-card">
        <div class="kpi-label">Total de ações</div>
        <div class="kpi-number">{total_acoes}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Áreas envolvidas</div>
        <div class="kpi-number">{total_areas}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Início</div>
        <div class="kpi-number" style="font-size:30px;">{primeira_data}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Fim</div>
        <div class="kpi-number" style="font-size:30px;">{ultima_data}</div>
    </div>
</div>
""", unsafe_allow_html=True)

areas = list(df["Área"].dropna().unique())

cols = st.columns(3)

for i, area in enumerate(areas):
    dados_area = df[df["Área"] == area].sort_values("Data")
    area_upper = str(area).upper().strip()
    cor = cores.get(area_upper, "#001B5E")

    html = f'''
<div class="area-card" style="border-top: 8px solid {cor};">
    <div class="area-header">
        <div class="area-title">{escape(str(area))}</div>
        <div class="area-count" style="background:{cor};">{len(dados_area)} ações</div>
    </div>
'''

    for _, row in dados_area.iterrows():
        data = row["Data"].strftime("%d/%m")
        acao = escape(str(row["Ação sobre"]))
        obs = row["Observação"]

        html += f'''
    <div class="action-item">
        <span class="date-pill" style="background:{cor};">{data}</span>
        <span class="action-title">{acao}</span>
'''

        if pd.notna(obs) and str(obs).strip():
            html += f'''
        <div class="obs">{escape(str(obs))}</div>
'''

        html += '''
    </div>
'''

    html += '''
</div>
'''

    cols[i % 3].markdown(html, unsafe_allow_html=True)

st.markdown("""
<div class="footer">
    Calendário visual de ações do Setor Financeiro | Modelo em Streamlit
</div>
""", unsafe_allow_html=True)
