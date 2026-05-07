import streamlit as st
import pandas as pd
import base64
from pathlib import Path
from html import escape
from datetime import date
import streamlit.components.v1 as components

st.set_page_config(page_title="Calendário de Ações", layout="wide")

ARQUIVO_EXCEL = "Calendário2.xlsx"
ARQUIVO_STATUS = "status_acoes.csv"
LOGO_PATH = "logo_pucrs.png"

df = pd.read_excel(ARQUIVO_EXCEL)
df.columns = df.columns.str.strip()

df = df[["Data", "Área", "Ação sobre", "Observação"]].copy()
df = df.dropna(subset=["Data", "Área", "Ação sobre"])

df["Data"] = pd.to_datetime(df["Data"], errors="coerce", dayfirst=True)
df = df.dropna(subset=["Data"])
df = df.sort_values("Data")

df["ID"] = (
    df["Data"].dt.strftime("%Y%m%d") + "_" +
    df["Área"].astype(str) + "_" +
    df["Ação sobre"].astype(str)
)

if Path(ARQUIVO_STATUS).exists():
    status = pd.read_csv(ARQUIVO_STATUS)
else:
    status = pd.DataFrame(columns=["ID", "Concluída", "Observação acompanhamento"])

df = df.merge(status, on="ID", how="left")

df["Concluída"] = df["Concluída"].fillna(False).astype(bool)
df["Observação acompanhamento"] = df["Observação acompanhamento"].fillna("")

hoje = pd.Timestamp(date.today())

df["Atrasada"] = (df["Data"] < hoje) & (~df["Concluída"])
df["Hoje"] = df["Data"] == hoje

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
concluidas = int(df["Concluída"].sum())
pendentes = total_acoes - concluidas
atrasadas = int(df["Atrasada"].sum())
percentual = concluidas / total_acoes if total_acoes else 0

k1, k2, k3, k4 = st.columns(4)

k1.metric("Total de ações", total_acoes)
k2.metric("Concluídas", concluidas)
k3.metric("Pendentes", pendentes)
k4.metric("Atrasadas", atrasadas)

st.progress(percentual, text=f"{concluidas} de {total_acoes} ações concluídas")

st.divider()

st.subheader("Atualização das ações")

editor = df[[
    "Concluída",
    "Data",
    "Área",
    "Ação sobre",
    "Observação",
    "Observação acompanhamento",
    "Atrasada",
    "ID"
]].copy()

editor["Data"] = editor["Data"].dt.strftime("%d/%m/%Y")

editor_editado = st.data_editor(
    editor,
    hide_index=True,
    use_container_width=True,
    disabled=["Data", "Área", "Ação sobre", "Observação", "Atrasada", "ID"],
    column_config={
        "Concluída": st.column_config.CheckboxColumn("Concluída"),
        "Observação acompanhamento": st.column_config.TextColumn("Observação de acompanhamento"),
        "Atrasada": st.column_config.CheckboxColumn("Atrasada"),
        "ID": None,
    }
)

if st.button("Salvar alterações", type="primary"):
    salvar = editor_editado[["ID", "Concluída", "Observação acompanhamento"]].copy()
    salvar.to_csv(ARQUIVO_STATUS, index=False)
    st.success("Alterações salvas. Atualize a página se quiser conferir o painel atualizado.")

st.divider()

st.subheader("Resumo visual por área")

abas = st.tabs(["Pendentes", "Concluídas", "Atrasadas"])

def montar_card(dados, titulo_lista):
    areas = list(dados["Área"].dropna().unique())
    cols = st.columns(3)

    for i, area in enumerate(areas):
        dados_area = dados[dados["Área"] == area].sort_values("Data")
        area_upper = str(area).upper().strip()
        cor = cores.get(area_upper, "#001B5E")

        itens_html = ""

        for _, row in dados_area.iterrows():
            data_item = row["Data"].strftime("%d/%m")
            acao = escape(str(row["Ação sobre"]))
            obs = row["Observação"]
            obs_acomp = row["Observação acompanhamento"]

            if row["Concluída"]:
                status_label = "Concluída"
                status_cor = "#17A65B"
            elif row["Atrasada"]:
                status_label = "Atrasada"
                status_cor = "#D62828"
            elif row["Hoje"]:
                status_label = "Hoje"
                status_cor = "#FFB000"
            else:
                status_label = "Pendente"
                status_cor = "#6B7280"

            obs_html = ""
            if pd.notna(obs) and str(obs).strip():
                obs_html += f'<div class="obs"><strong>Obs. original:</strong> {escape(str(obs))}</div>'

            if pd.notna(obs_acomp) and str(obs_acomp).strip():
                obs_html += f'<div class="obs-acomp"><strong>Acompanhamento:</strong> {escape(str(obs_acomp))}</div>'

            itens_html += f"""
            <div class="action-item">
                <div>
                    <span class="date-pill" style="background:{cor};">{data_item}</span>
                    <span class="status-pill" style="background:{status_cor};">{status_label}</span>
                </div>
                <div class="action-title">{acao}</div>
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
                min-height: 580px;
            }}
            .area-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
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
            .date-pill, .status-pill {{
                display: inline-block;
                color: white;
                padding: 5px 11px;
                border-radius: 999px;
                font-weight: 900;
                font-size: 12px;
                margin-right: 6px;
                margin-bottom: 7px;
            }}
            .action-title {{
                font-size: 15px;
                font-weight: 850;
                color: #00133F;
                margin-top: 4px;
            }}
            .obs {{
                margin-top: 7px;
                font-size: 14px;
                color: #3B465A;
                line-height: 1.35;
            }}
            .obs-acomp {{
                margin-top: 7px;
                font-size: 14px;
                color: #001B5E;
                background: #EEF6FF;
                padding: 8px 10px;
                border-radius: 10px;
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
            components.html(card_html, height=720, scrolling=True)

with abas[0]:
    montar_card(df[df["Concluída"] == False], "Pendentes")

with abas[1]:
    montar_card(df[df["Concluída"] == True], "Concluídas")

with abas[2]:
    montar_card(df[df["Atrasada"] == True], "Atrasadas")
