import streamlit as st
import pandas as pd
import base64
from pathlib import Path
from html import escape
from datetime import date

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

st.markdown("""
<style>
.stApp {
    background: #F4F7FB;
}

.block-container {
    padding-top: 1.5rem;
}

.header {
    background: linear-gradient(90deg, #001B5E, #004AAD);
    padding: 34px 42px;
    border-radius: 22px;
    color: white;
    margin-bottom: 26px;
    box-shadow: 0 10px 28px rgba(0, 27, 94, 0.22);
}

.header * {
    color: white !important;
}

.kpi-card {
    background: white;
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.08);
    border: 1px solid #D9E2F1;
}

.kpi-label {
    color: #001B5E;
    font-size: 14px;
    font-weight: 900;
    text-transform: uppercase;
}

.kpi-number {
    color: #0077FF;
    font-size: 40px;
    font-weight: 950;
}

.filter-box {
    background: white;
    border: 1px solid #D9E2F1;
    border-radius: 20px;
    padding: 18px 20px;
    margin-bottom: 18px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.06);
}

.area-card {
    background: white;
    border-radius: 22px;
    padding: 20px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.08);
    border: 1px solid #D9E2F1;
    min-height: 520px;
    margin-bottom: 22px;
}

.area-title {
    font-size: 24px;
    font-weight: 950;
    color: #001B5E;
    margin-bottom: 4px;
}

.area-subtitle {
    font-size: 14px;
    color: #516077;
    font-weight: 700;
    margin-bottom: 18px;
}

.action-box {
    border-top: 1px solid #E8EEF7;
    padding: 16px 0 14px 0;
}

.action-title {
    font-size: 15px;
    font-weight: 950;
    color: #00133F;
    margin-top: 4px;
}

.obs-original {
    margin-top: 7px;
    color: #3B465A;
    font-size: 13px;
    line-height: 1.35;
}

.pill {
    display: inline-block;
    color: white !important;
    padding: 5px 11px;
    border-radius: 999px;
    font-weight: 900;
    font-size: 12px;
    margin-right: 6px;
    margin-bottom: 7px;
}

.stTextArea textarea {
    background-color: #F1F5FA !important;
    border-radius: 12px !important;
    color: #00133F !important;
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
    logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:76px;">'
else:
    logo_html = '<div style="font-size:32px;font-weight:900;">PUCRS</div>'

st.markdown(f"""
<div class="header">
    <div style="display:flex;align-items:center;gap:30px;">
        {logo_html}
        <div style="height:72px;width:2px;background:rgba(255,255,255,.45);"></div>
        <div>
            <div style="font-size:23px;font-weight:800;">ESTRUTURA DO SETOR FINANCEIRO</div>
            <div style="font-size:52px;font-weight:950;line-height:1;margin-top:8px;">CALENDÁRIO DE AÇÕES</div>
            <div style="font-size:20px;color:#8FDBFF!important;margin-top:14px;">Acompanhamento das ações por área</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Filtros por botão
areas_disponiveis = sorted(df["Área"].dropna().unique())

if "areas_selecionadas" not in st.session_state:
    st.session_state.areas_selecionadas = areas_disponiveis.copy()

st.markdown('<div class="filter-box">', unsafe_allow_html=True)
st.markdown("### Filtros")

botoes = st.columns(len(areas_disponiveis) + 1)

if botoes[0].button("Todas as áreas"):
    st.session_state.areas_selecionadas = areas_disponiveis.copy()
    st.rerun()

for i, area in enumerate(areas_disponiveis, start=1):
    ativo = area in st.session_state.areas_selecionadas
    label = f"✅ {area}" if ativo else area

    if botoes[i].button(label):
        if ativo:
            st.session_state.areas_selecionadas.remove(area)
        else:
            st.session_state.areas_selecionadas.append(area)
        st.rerun()

p1, p2, p3 = st.columns(3)

if p1.button("Todos os períodos"):
    st.session_state.periodo = "todos"
    st.rerun()

if p2.button("Próximos 7 dias"):
    st.session_state.periodo = "semana"
    st.rerun()

if p3.button("Próximos 30 dias"):
    st.session_state.periodo = "mes"
    st.rerun()

if "periodo" not in st.session_state:
    st.session_state.periodo = "todos"

st.markdown('</div>', unsafe_allow_html=True)

base_filtrada = df[df["Área"].isin(st.session_state.areas_selecionadas)].copy()

if st.session_state.periodo == "semana":
    base_filtrada = base_filtrada[
        (base_filtrada["Data"] >= hoje) &
        (base_filtrada["Data"] <= hoje + pd.Timedelta(days=7))
    ]

elif st.session_state.periodo == "mes":
    base_filtrada = base_filtrada[
        (base_filtrada["Data"] >= hoje) &
        (base_filtrada["Data"] <= hoje + pd.Timedelta(days=30))
    ]

base_filtrada = base_filtrada.sort_values(
    by=["Atrasada", "Hoje", "Data"],
    ascending=[False, False, True]
)

# KPIs
total = len(base_filtrada)
concluidas = int(base_filtrada["Concluída"].sum())
pendentes = total - concluidas
atrasadas = int(base_filtrada["Atrasada"].sum())

c1, c2, c3, c4 = st.columns(4)

c1.markdown(f'<div class="kpi-card"><div class="kpi-label">TOTAL FILTRADO</div><div class="kpi-number">{total}</div></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="kpi-card"><div class="kpi-label">CONCLUÍDAS</div><div class="kpi-number">{concluidas}</div></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="kpi-card"><div class="kpi-label">PENDENTES</div><div class="kpi-number">{pendentes}</div></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="kpi-card"><div class="kpi-label">ATRASADAS</div><div class="kpi-number">{atrasadas}</div></div>', unsafe_allow_html=True)

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

    cols = st.columns(3, gap="large")

    for i, area in enumerate(areas):
        dados_area = base[base["Área"] == area].sort_values(
            by=["Atrasada", "Hoje", "Data"],
            ascending=[False, False, True]
        )

        cor = cores.get(str(area).upper().strip(), "#001B5E")

        with cols[i % 3]:
            st.markdown(
                f"""
                <div class="area-card" style="border-top:8px solid {cor};">
                    <div class="area-title">{escape(str(area))}</div>
                    <div class="area-subtitle">{len(dados_area)} ações neste filtro</div>
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
                    <div class="action-box">
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
                    height=68
                )

                b1, b2 = st.columns([1.2, 1])

                if b1.button("Salvar observação", key=f"salvar_{key_base}"):
                    salvar_observacao(id_acao, nova_obs)

                if row["Concluída"]:
                    if b2.button("Desfazer", key=f"desfazer_{key_base}"):
                        mudar_status(id_acao, False)
                else:
                    if b2.button("Concluir", key=f"concluir_{key_base}", type="primary"):
                        mudar_status(id_acao, True)

            st.markdown("</div>", unsafe_allow_html=True)

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
    Calendário visual de ações do Setor Financeiro | Acompanhamento por cards
</div>
""", unsafe_allow_html=True)
