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

# =========================
# DADOS
# =========================

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
    df["Ação sobre"].astype(str) + "_" +
    df["Observação"].astype(str)
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

# =========================
# FUNÇÕES
# =========================

def salvar_status():
    salvar = df[["ID", "Concluída", "Observação acompanhamento"]].copy()
    salvar.to_csv(ARQUIVO_STATUS, index=False)

def atualizar_status(id_acao, concluida):
    df.loc[df["ID"] == id_acao, "Concluída"] = concluida
    salvar_status()

def atualizar_obs(id_acao, obs):
    df.loc[df["ID"] == id_acao, "Observação acompanhamento"] = obs
    salvar_status()

def img_to_base64(path):
    if Path(path).exists():
        with open(path, "rb") as img:
            return base64.b64encode(img.read()).decode()
    return None

# =========================
# CSS
# =========================

st.markdown("""
<style>
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

.kpi-card {
    background: white;
    border: 1px solid #D9E2F1;
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0 5px 18px rgba(0,0,0,.06);
}

.kpi-label {
    color: #001B5E;
    font-size: 15px;
    font-weight: 900;
}

.kpi-number {
    color: #0077FF;
    font-size: 42px;
    font-weight: 950;
}

.area-box {
    background: white;
    border: 1px solid #D9E2F1;
    border-radius: 22px;
    padding: 18px;
    box-shadow: 0 5px 18px rgba(0,0,0,.06);
    margin-bottom: 22px;
}

.area-title {
    font-size: 25px;
    font-weight: 950;
    color: #001B5E;
    margin-bottom: 8px;
}

.action-card {
    background: #FFFFFF;
    border: 1px solid #E3EAF5;
    border-radius: 18px;
    padding: 16px;
    margin-bottom: 14px;
    box-shadow: 0 3px 10px rgba(0,0,0,.04);
}

.action-title {
    font-size: 16px;
    font-weight: 900;
    color: #00133F;
}

.obs-original {
    margin-top: 8px;
    color: #3B465A;
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

# =========================
# HEADER
# =========================

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

# =========================
# KPIs
# =========================

total = len(df)
concluidas = int(df["Concluída"].sum())
pendentes = total - concluidas
atrasadas = int(df["Atrasada"].sum())
progresso = concluidas / total if total else 0

c1, c2, c3, c4 = st.columns(4)

c1.markdown(f'<div class="kpi-card"><div class="kpi-label">TOTAL DE AÇÕES</div><div class="kpi-number">{total}</div></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="kpi-card"><div class="kpi-label">CONCLUÍDAS</div><div class="kpi-number">{concluidas}</div></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="kpi-card"><div class="kpi-label">PENDENTES</div><div class="kpi-number">{pendentes}</div></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="kpi-card"><div class="kpi-label">ATRASADAS</div><div class="kpi-number">{atrasadas}</div></div>', unsafe_allow_html=True)

st.write("")
st.progress(progresso, text=f"{concluidas} de {total} ações concluídas")

# =========================
# BARRAS POR ÁREA
# =========================

st.subheader("Progresso por área")

for area in df["Área"].dropna().unique():
    dados_area = df[df["Área"] == area]
    total_area = len(dados_area)
    concluidas_area = int(dados_area["Concluída"].sum())
    progresso_area = concluidas_area / total_area if total_area else 0

    st.markdown(f"**{area}** — {concluidas_area}/{total_area} concluídas")
    st.progress(progresso_area)

st.divider()

# =========================
# CONFIRMAÇÃO
# =========================

if "acao_confirmar" not in st.session_state:
    st.session_state.acao_confirmar = None

if "novo_status" not in st.session_state:
    st.session_state.novo_status = None

if st.session_state.acao_confirmar:
    acao_id = st.session_state.acao_confirmar
    linha = df[df["ID"] == acao_id].iloc[0]
    texto_acao = linha["Ação sobre"]

    with st.container(border=True):
        st.warning(f"Confirmar alteração da ação: **{texto_acao}**?")

        b1, b2 = st.columns(2)

        if b1.button("Confirmar", type="primary"):
            atualizar_status(acao_id, st.session_state.novo_status)
            st.session_state.acao_confirmar = None
            st.session_state.novo_status = None
            st.rerun()

        if b2.button("Cancelar"):
            st.session_state.acao_confirmar = None
            st.session_state.novo_status = None
            st.rerun()

# =========================
# CARDS
# =========================

st.subheader("Ações")

aba_pendentes, aba_concluidas, aba_atrasadas, aba_todas = st.tabs(
    ["Pendentes", "Concluídas", "Atrasadas", "Todas"]
)

def renderizar_acoes(base):
    areas = list(base["Área"].dropna().unique())

    if not areas:
        st.info("Nenhuma ação nesta categoria.")
        return

    cols = st.columns(3)

    for i, area in enumerate(areas):
        dados_area = base[base["Área"] == area].sort_values("Data")
        cor = cores.get(str(area).upper().strip(), "#001B5E")

        with cols[i % 3]:
            st.markdown(
                f"""
                <div class="area-box" style="border-top:8px solid {cor};">
                    <div class="area-title">{escape(str(area))}</div>
                    <div style="color:#5B6475;font-weight:700;margin-bottom:14px;">
                        {len(dados_area)} ações
                    </div>
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

                with st.container(border=True):
                    st.markdown(
                        f"""
                        <span class="pill" style="background:{cor};">{data_txt}</span>
                        <span class="pill" style="background:{status_cor};">{status_txt}</span>
                        <div class="action-title">{escape(str(acao))}</div>
                        <div class="obs-original">{escape(str(obs))}</div>
                        """,
                        unsafe_allow_html=True
                    )

                    nova_obs = st.text_area(
                        "Observação de acompanhamento",
                        value=str(obs_acomp) if pd.notna(obs_acomp) else "",
                        key=f"obs_{id_acao}",
                        height=80
                    )

                    b1, b2 = st.columns(2)

                    if b1.button("Salvar observação", key=f"salvar_obs_{id_acao}"):
                        atualizar_obs(id_acao, nova_obs)
                        st.success("Observação salva.")
                        st.rerun()

                    if not row["Concluída"]:
                        if b2.button("Concluir", key=f"concluir_{id_acao}", type="primary"):
                            st.session_state.acao_confirmar = id_acao
                            st.session_state.novo_status = True
                            st.rerun()
                    else:
                        if b2.button("Desfazer", key=f"desfazer_{id_acao}"):
                            st.session_state.acao_confirmar = id_acao
                            st.session_state.novo_status = False
                            st.rerun()

with aba_pendentes:
    renderizar_acoes(df[df["Concluída"] == False])

with aba_concluidas:
    renderizar_acoes(df[df["Concluída"] == True])

with aba_atrasadas:
    renderizar_acoes(df[df["Atrasada"] == True])

with aba_todas:
    renderizar_acoes(df)

st.markdown("""
<div class="footer">
    Calendário visual de ações do Setor Financeiro | Atualização por cards
</div>
""", unsafe_allow_html=True)
