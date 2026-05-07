import streamlit as st
import pandas as pd
import base64
from pathlib import Path
from html import escape
import streamlit.components.v1 as components

st.set_page_config(page_title="Calendário de Ações", layout="wide")

ARQUIVO_EXCEL = "Calendário2.xlsx"
LOGO_PATH = "logo_pucrs.png"

df = pd.read_excel(ARQUIVO_EXCEL)
df.columns = df.columns.str.strip()

df = df[["Data", "Área", "Ação sobre", "Observação"]].copy()
df = df.dropna(subset=["Data", "Área", "Ação sobre"])

df["Data"] = pd.to_datetime(df["Data"], errors="coerce", dayfirst=True)
df = df.dropna(subset=["Data"])
df = df.sort_values("Data")

cores = {
    "CRÉDITOS": "#17A65B",
    "ANÁLISE": "#0077FF",
    "FATURAMENTO": "#6F2DBD",
    "COBRANÇA": "#FF8C00",
}

def img_to_base64(path):
    if Path(path).exists():
        with open(path, "rb") as img:
            return base64.b64encode(img.read()).decode()
    return None

logo_b64 = img_to_base64(LOGO_PATH)

st.markdown("""
<style>
.block-container {
    padding-top: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

if logo_b64:
    logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:80px;">'
else:
    logo_html = '<div style="font-size:32px;font-weight:900;">PUCRS</div>'

st.markdown(f"""
<div style="
    background:linear-gradient(90deg,#00133F,#004AAD);
    border-radius:24px;
    padding:36px 42px;
    color:white;
    box-shadow:0 8px 24px rgba(0,27,94,.25);
    margin-bottom:28px;
">
    <div style="display:flex;align-items:center;gap:30px;">
        {logo_html}
        <div style="height:78px;width:2px;background:rgba(255,255,255,.45);"></div>
        <div>
            <div style="font-size:24px;font-weight:800;">ESTRUTURA DO SETOR FINANCEIRO</div>
            <div style="font-size:54px;font-weight:950;line-height:1;margin-top:8px;">CALENDÁRIO DE AÇÕES</div>
            <div style="font-size:21px;color:#8FDBFF;margin-top:14px;">Acompanhamento das ações por área</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

total_acoes = len(df)
total_areas = df["Área"].nunique()
primeira_data = df["Data"].min().strftime("%d/%m/%Y")
ultima_data = df["Data"].max().strftime("%d/%m/%Y")

k1, k2, k3, k4 = st.columns(4)

k1.markdown(f"""
<div style="background:white;border:1px solid #D9E2F1;border-radius:20px;padding:22px;box-shadow:0 5px 18px rgba(0,0,0,.06);">
<div style="color:#001B5E;font-size:15px;font-weight:900;">TOTAL DE AÇÕES</div>
<div style="color:#0077FF;font-size:42px;font-weight:950;">{total_acoes}</div>
</div>
""", unsafe_allow_html=True)

k2.markdown(f"""
<div style="background:white;border:1px solid #D9E2F1;border-radius:20px;padding:22px;box-shadow:0 5px 18px rgba(0,0,0,.06);">
<div style="color:#001B5E;font-size:15px;font-weight:900;">ÁREAS ENVOLVIDAS</div>
<div style="color:#0077FF;font-size:42px;font-weight:950;">{total_areas}</div>
</div>
""", unsafe_allow_html=True)

k3.markdown(f"""
<div style="background:white;border:1px solid #D9E2F1;border-radius:20px;padding:22px;box-shadow:0 5px 18px rgba(0,0,0,.06);">
<div style="color:#001B5E;font-size:15px;font-weight:900;">INÍCIO</div>
<div style="color:#0077FF;font-size:30px;font-weight:950;">{primeira_data}</div>
</div>
""", unsafe_allow_html=True)

k4.markdown(f"""
<div style="background:white;border:1px solid #D9E2F1;border-radius:20px;padding:22px;box-shadow:0 5px 18px rgba(0,0,0,.06);">
<div style="color:#001B5E;font-size:15px;font-weight:900;">FIM</div>
<div style="color:#0077FF;font-size:30px;font-weight:950;">{ultima_data}</div>
</div>
""", unsafe_allow_html=True)

st.write("")

areas = list(df["Área"].dropna().unique())
cols = st.columns(3)

for i, area in enumerate(areas):
    dados_area = df[df["Área"] == area].sort_values("Data")
    area_upper = str(area).upper().strip()
    cor = cores.get(area_upper, "#001B5E")

    itens_html = ""

    for _, row in dados_area.iterrows():
        data = row["Data"].strftime("%d/%m")
        acao = escape(str(row["Ação sobre"]))
        obs = row["Observação"]

        obs_html = ""
        if pd.notna(obs) and str(obs).strip():
            obs_html = f"""
            <div class="obs">{escape(str(obs))}</div>
            """

        itens_html += f"""
        <div class="action-item">
            <div>
                <span class="date-pill" style="background:{cor};">{data}</span>
                <span class="action-title">{acao}</span>
            </div>
            {obs_html}
        </div>
        """

    card_html = f"""
    <html>
    <head>
    <style>
        body {{
            margin: 0;
            font-family: Arial, sans-serif;
            background: transparent;
        }}
        .card {{
            background: white;
            border: 1px solid #D9E2F1;
            border-top: 8px solid {cor};
            border-radius: 22px;
            padding: 22px;
            box-shadow: 0 5px 18px rgba(0,0,0,.07);
            min-height: 620px;
        }}
        .area-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 18px;
        }}
        .area-title {{
            font-size: 24px;
            font-weight: 950;
            color: #001B5E;
        }}
        .area-count {{
            color: white;
            background: {cor};
            border-radius: 999px;
            padding: 7px 14px;
            font-size: 14px;
            font-weight: 800;
        }}
        .action-item {{
            border-top: 1px solid #EEF2F8;
            padding: 14px 0;
        }}
        .date-pill {{
            display: inline-block;
            color: white;
            padding: 5px 12px;
            border-radius: 999px;
            font-weight: 900;
            font-size: 13px;
            margin-right: 8px;
            margin-bottom: 6px;
        }}
        .action-title {{
            font-size: 15px;
            font-weight: 850;
            color: #00133F;
        }}
        .obs {{
            margin-top: 7px;
            font-size: 14px;
            color: #3B465A;
            line-height: 1.35;
        }}
    </style>
    </head>
    <body>
        <div class="card">
            <div class="area-header">
                <div class="area-title">{escape(str(area))}</div>
                <div class="area-count">{len(dados_area)} ações</div>
            </div>
            {itens_html}
        </div>
    </body>
    </html>
    """

    with cols[i % 3]:
        components.html(card_html, height=760, scrolling=True)
