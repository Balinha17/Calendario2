import streamlit as st
import pandas as pd
import base64
from pathlib import Path
from html import escape
from datetime import date
from io import BytesIO

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
df = df.sort_values("Data").reset_index(drop=True)

df["ID"] = (
    df.index.astype(str) + "_" +
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

def salvar_status():
    df[["ID", "Concluída", "Observação acompanhamento"]].to_csv(ARQUIVO_STATUS, index=False)

def mudar_status(id_acao, concluida):
    df.loc[df["ID"] == id_acao, "Concluída"] = concluida
    salvar_status()
    st.rerun()

def salvar_observacao(id_acao, obs):
    df.loc[df["ID"] == id_acao, "Observação acompanhamento"] = obs
    salvar_status()
    st.rerun()

def img_to_base64(path):
    if Path(path).exists():
        with open(path, "rb") as img:
            return base64.b64encode(img.read()).decode()
    return None

def preparar_exportacao(base):
    export = base[[
        "Data",
        "Área",
        "Ação sobre",
        "Observação",
        "Concluída",
        "Atrasada",
        "Observação acompanhamento"
    ]].copy()

    export["Data"] = pd.to_datetime(export["Data"], errors="coerce").dt.strftime("%d/%m/%Y")
    return export

def gerar_excel(base_exportada):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        base_exportada.to_excel(writer, index=False, sheet_name="Calendário")
    return buffer.getvalue()

st.markdown("""
<style>
:root {
    --card-bg: #FFFFFF;
    --text-main: #00133F;
    --text-soft: #3B465A;
    --border: #D9E2F1;
    --soft-bg: #F6F8FC;
}

@media (prefers-color-scheme: dark) {
    :root {
        --card-bg: #111827;
        --text-main: #F9FAFB;
        --text-soft: #D1D5DB;
        --border: #374151;
        --soft-bg: #1F2937;
    }
}

.block-container {
    padding-top: 1.5rem;
}

.header {
    background: linear-gradient(90deg,#00133F,#004AAD);
    border-radius: 24px;
    padding: 36px 42px;
    color: white;
    box-shadow: 0 8px 24px rgba(0,27,94,.25);
    margin-bottom: 28px;
}

.kpi-card, .area-summary, .area-group {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0 5px 18px rgba(0,0,0,.08);
}

.kpi-label {
    color: var(--text-main);
    font-size: 15px;
    font-weight: 900;
}

.kpi-number {
    color: #0077FF;
    font-size: 42px;
    font-weight: 950;
}

.area-summary-title, .area-title {
    color: var(--text-main);
    font-weight: 950;
}

.area-summary-title {
    font-size: 18px;
}

.area-title {
    font-size: 26px;
}

.area-summary-text, .area-subtitle, .obs-original {
    color: var(--text-soft);
}

.action-card {
    background: var(--soft-bg);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 16px;
    margin-bottom: 14px;
}

.action-title {
    font-size: 17px;
    font-weight: 950;
    color: var(--text-main);
    margin-top: 4px;
}

.obs-original {
    margin-top: 8px;
    font-size: 14px;
    line-height: 1.35;
}

.pill {
    display: inline-block;
    color: white;
    padding: 5px 11px;
    border-radius: 999px;
    font-weight: 900;
    font-size: 12px;
    margin-right: 6px;
    margin-bottom: 8px;
}

.footer {
    background: #001B5E;
    color: white;
    padding: 18px 24px;
    border-radius: 18px;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

logo_b64 = img_to_base64(LOGO_PATH)

if logo_b64:
    logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:80px;">'
else:
    logo_html = '<div style="font-size:32px;font-weight:900;">PUCRS</div>'

st.markdown(f"""
<div class="header">
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

st.subheader("Filtros")

col_f1, col_f2, col_f3, col_f4 = st.columns([2, 1, 1, 1])

areas_disponiveis = sorted(df["Área"].dropna().unique())

areas_selecionadas = col_f1.multiselect(
    "Área",
    options=areas_disponiveis,
    default=areas_disponiveis
)

periodo_rapido = col_f2.radio(
    "Período rápido",
    ["Todos", "Semana", "Mês"],
    horizontal=True
)

data_inicio = col_f3.date_input("Data inicial", value=df["Data"].min().date())
data_fim = col_f4.date_input("Data final", value=df["Data"].max().date())

base_filtrada = df.copy()

if periodo_rapido == "Semana":
    inicio = hoje.normalize()
    fim = inicio + pd.Timedelta(days=7)
    base_filtrada = base_filtrada[(base_filtrada["Data"] >= inicio) & (base_filtrada["Data"] <= fim)]

elif periodo_rapido == "Mês":
    inicio = hoje.normalize()
    fim = inicio + pd.Timedelta(days=30)
    base_filtrada = base_filtrada[(base_filtrada["Data"] >= inicio) & (base_filtrada["Data"] <= fim)]

else:
    base_filtrada = base_filtrada[
        (base_filtrada["Data"] >= pd.Timestamp(data_inicio)) &
        (base_filtrada["Data"] <= pd.Timestamp(data_fim))
    ]

base_filtrada = base_filtrada[base_filtrada["Área"].isin(areas_selecionadas)]

base_filtrada = base_filtrada.sort_values(
    by=["Atrasada", "Hoje", "Data"],
    ascending=[False, False, True]
)

st.divider()

total = len(base_filtrada)
concluidas = int(base_filtrada["Concluída"].sum())
pendentes = total - concluidas
atrasadas = int(base_filtrada["Atrasada"].sum())

c1, c2, c3, c4 = st.columns(4)

c1.markdown(f'<div class="kpi-card"><div class="kpi-label">TOTAL FILTRADO</div><div class="kpi-number">{total}</div></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="kpi-card"><div class="kpi-label">CONCLUÍDAS</div><div class="kpi-number">{concluidas}</div></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="kpi-card"><div class="kpi-label">PENDENTES</div><div class="kpi-number">{pendentes}</div></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="kpi-card"><div class="kpi-label">ATRASADAS</div><div class="kpi-number">{atrasadas}</div></div>', unsafe_allow_html=True)

st.write("")

st.subheader("Resumo por área")

resumo_cols = st.columns(4)

for i, area in enumerate(sorted(base_filtrada["Área"].dropna().unique())):
    dados_area = base_filtrada[base_filtrada["Área"] == area]
    total_area = len(dados_area)
    concluidas_area = int(dados_area["Concluída"].sum())
    pendentes_area = total_area - concluidas_area
    atrasadas_area = int(dados_area["Atrasada"].sum())
    cor = cores.get(str(area).upper().strip(), "#001B5E")

    with resumo_cols[i % 4]:
        st.markdown(f"""
        <div class="area-summary" style="border-top:6px solid {cor};">
            <div class="area-summary-title">{escape(str(area))}</div>
            <div class="area-summary-text">
                Total: <strong>{total_area}</strong><br>
                Pendentes: <strong>{pendentes_area}</strong><br>
                Concluídas: <strong>{concluidas_area}</strong><br>
                Atrasadas: <strong>{atrasadas_area}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

st.subheader("Exportação")

exportar = preparar_exportacao(base_filtrada)

e1, e2 = st.columns(2)

e1.download_button(
    "Baixar CSV filtrado",
    data=exportar.to_csv(index=False).encode("utf-8-sig"),
    file_name="calendario_acoes_filtrado.csv",
    mime="text/csv"
)

e2.download_button(
    "Baixar Excel filtrado",
    data=gerar_excel(exportar),
    file_name="calendario_acoes_filtrado.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.divider()

st.subheader("Ações")

aba_pendentes, aba_concluidas, aba_atrasadas, aba_todas = st.tabs(
    ["Pendentes", "Concluídas", "Atrasadas", "Todas"]
)

def renderizar_acoes(base, nome_aba):
    areas = list(base["Área"].dropna().unique())

    if not areas:
        st.info("Nenhuma ação nesta categoria.")
        return

    cols = st.columns(3)

    for i, area in enumerate(areas):
        dados_area = base[base["Área"] == area].sort_values(
            by=["Atrasada", "Hoje", "Data"],
            ascending=[False, False, True]
        )

        cor = cores.get(str(area).upper().strip(), "#001B5E")

        with cols[i % 3]:
            st.markdown(
                f"""
                <div class="area-group" style="border-top:8px solid {cor}; margin-bottom:16px;">
                    <div class="area-title">{escape(str(area))}</div>
                    <div class="area-subtitle">{len(dados_area)} ações neste filtro</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            for _, row in dados_area.iterrows():
                id_acao = row["ID"]
                data_txt = row["Data"].strftime("%d/%m")
                acao = row["Ação sobre"]
                obs = row["Observação"]
                obs_acomp = row["Observação acompanhamento"]

                if row["Concluída"]:
                    status_txt = "Concluída"
                    status_cor = "#17A65B"
                elif row["Atrasada"]:
                    status_txt = "Atrasada"
                    status_cor = "#D62828"
                elif row["Hoje"]:
                    status_txt = "Hoje"
                    status_cor = "#FFB000"
                else:
                    status_txt = "Pendente"
                    status_cor = "#6B7280"

                st.markdown(
                    f"""
                    <div class="action-card">
                        <span class="pill" style="background:{cor};">{data_txt}</span>
                        <span class="pill" style="background:{status_cor};">{status_txt}</span>
                        <div class="action-title">{escape(str(acao))}</div>
                        <div class="obs-original">{escape(str(obs))}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                key_base = f"{nome_aba}_{id_acao}"

                nova_obs = st.text_area(
                    "Observação de acompanhamento",
                    value=str(obs_acomp) if pd.notna(obs_acomp) else "",
                    key=f"obs_{key_base}",
                    height=75
                )

                b1, b2 = st.columns([1, 1])

                if b1.button("Salvar observação", key=f"salvar_{key_base}"):
                    salvar_observacao(id_acao, nova_obs)

                if row["Concluída"]:
                    if b2.button("Desfazer conclusão", key=f"desfazer_{key_base}"):
                        mudar_status(id_acao, False)
                else:
                    if b2.button("Concluir", key=f"concluir_{key_base}", type="primary"):
                        mudar_status(id_acao, True)

                st.write("")

with aba_pendentes:
    renderizar_acoes(base_filtrada[base_filtrada["Concluída"] == False], "pendentes")

with aba_concluidas:
    renderizar_acoes(base_filtrada[base_filtrada["Concluída"] == True], "concluidas")

with aba_atrasadas:
    renderizar_acoes(base_filtrada[base_filtrada["Atrasada"] == True], "atrasadas")

with aba_todas:
    renderizar_acoes(base_filtrada, "todas")

st.markdown("""
<div class="footer">
    Calendário visual de ações do Setor Financeiro | Filtros, resumo por área e exportação
</div>
""", unsafe_allow_html=True)
