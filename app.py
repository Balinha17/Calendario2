import streamlit as st
import pandas as pd
import base64
from pathlib import Path
from html import escape
from datetime import date
import unicodedata

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    gspread = None
    Credentials = None

st.set_page_config(page_title="Calendário de Ações", layout="wide")

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTCNXpx2t_KjaiKIeS3KCJa_vVd3eBaxf6uCfL5IXKT5Uz2Bml1gge5Yfq0OB5dMdnQYj2o3rJ3qEpz/pub?gid=0&single=true&output=csv"

ARQUIVO_STATUS = "status_acoes.csv"
LOGO_PATH = "logo_pucrs.png"

STATUS_WORKSHEET_NAME = "Status_Acoes"

# =========================
# FUNÇÕES AUXILIARES
# =========================

def normalizar_texto(txt):
    txt = str(txt).strip().upper()
    txt = unicodedata.normalize("NFKD", txt).encode("ASCII", "ignore").decode("utf-8")
    return txt

def img_to_base64(path):
    if Path(path).exists():
        with open(path, "rb") as img:
            return base64.b64encode(img.read()).decode()
    return None

def google_status_habilitado():
    return (
        gspread is not None
        and "gcp_service_account" in st.secrets
        and "STATUS_SPREADSHEET_ID" in st.secrets
    )

def abrir_status_sheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]),
        scopes=scopes
    )

    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(st.secrets["STATUS_SPREADSHEET_ID"])

    try:
        worksheet = spreadsheet.worksheet(STATUS_WORKSHEET_NAME)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=STATUS_WORKSHEET_NAME,
            rows=1000,
            cols=3
        )
        worksheet.update([["ID", "Concluída", "Observação acompanhamento"]])

    return worksheet

def carregar_status():
    if google_status_habilitado():
        worksheet = abrir_status_sheet()
        registros = worksheet.get_all_records()

        if registros:
            return pd.DataFrame(registros)

        return pd.DataFrame(columns=["ID", "Concluída", "Observação acompanhamento"])

    if Path(ARQUIVO_STATUS).exists():
        return pd.read_csv(ARQUIVO_STATUS)

    return pd.DataFrame(columns=["ID", "Concluída", "Observação acompanhamento"])

def salvar_status(df_status):
    df_status = df_status[["ID", "Concluída", "Observação acompanhamento"]].copy()
    df_status["Concluída"] = df_status["Concluída"].astype(bool)

    if google_status_habilitado():
        worksheet = abrir_status_sheet()

        dados = [["ID", "Concluída", "Observação acompanhamento"]]

        for _, row in df_status.iterrows():
            dados.append([
                str(row["ID"]),
                "TRUE" if bool(row["Concluída"]) else "FALSE",
                str(row["Observação acompanhamento"]) if pd.notna(row["Observação acompanhamento"]) else ""
            ])

        worksheet.clear()
        worksheet.update(dados)
    else:
        df_status.to_csv(ARQUIVO_STATUS, index=False)

def gerar_id(row):
    return (
        row["Data"].strftime("%Y%m%d")
        + "_"
        + normalizar_texto(row["Área"])
        + "_"
        + normalizar_texto(row["Ação sobre"])
    )

# =========================
# DADOS
# =========================

df = pd.read_csv(CSV_URL)
df.columns = df.columns.str.strip()

df = df[["Data", "Área", "Ação sobre", "Observação"]].copy()
df = df.dropna(subset=["Data", "Área", "Ação sobre"])

df["Data"] = pd.to_datetime(df["Data"], errors="coerce", dayfirst=True)
df = df.dropna(subset=["Data"])
df = df.sort_values("Data").reset_index(drop=True)

df["ID"] = df.apply(gerar_id, axis=1)

status = carregar_status()

if not status.empty:
    status.columns = status.columns.str.strip()

if "ID" not in status.columns:
    status["ID"] = ""

if "Concluída" not in status.columns:
    status["Concluída"] = False

if "Observação acompanhamento" not in status.columns:
    status["Observação acompanhamento"] = ""

status["ID"] = status["ID"].astype(str)
status["Concluída"] = status["Concluída"].astype(str).str.upper().isin(["TRUE", "1", "SIM", "YES"])
status["Observação acompanhamento"] = status["Observação acompanhamento"].fillna("")

df = df.merge(status, on="ID", how="left")

df["Concluída"] = df["Concluída"].fillna(False).astype(bool)
df["Observação acompanhamento"] = df["Observação acompanhamento"].fillna("")

hoje = pd.Timestamp(date.today())
df["Atrasada"] = (df["Data"] < hoje) & (~df["Concluída"])
df["Hoje"] = df["Data"] == hoje

cores = {
    "CRÉDITOS": "#16A65B",
    "ANÁLISE": "#0877F2",
    "FATURAMENTO": "#6F2DBD",
    "COBRANÇA": "#FF8C00",
}

def estado_atualizado():
    return df[["ID", "Concluída", "Observação acompanhamento"]].copy()

def mudar_status(id_acao, concluida):
    df.loc[df["ID"] == id_acao, "Concluída"] = concluida
    salvar_status(estado_atualizado())
    st.rerun()

def salvar_observacao(id_acao, obs):
    df.loc[df["ID"] == id_acao, "Observação acompanhamento"] = obs
    salvar_status(estado_atualizado())
    st.rerun()

total = len(df)
concluidas = int(df["Concluída"].sum())
pendentes = total - concluidas
atrasadas = int(df["Atrasada"].sum())

# =========================
# CSS
# =========================

st.markdown("""
<style>
.stApp {
    background: #F4F7FB !important;
}

.block-container {
    padding-top: 1.4rem;
    max-width: 1760px;
}

.header {
    background: linear-gradient(90deg, #001B5E, #004AAD);
    padding: 34px 42px;
    border-radius: 22px;
    color: white;
    margin-bottom: 28px;
    box-shadow: 0 10px 28px rgba(0, 27, 94, 0.22);
}

.header * {
    color: white !important;
}

.header-grid {
    display: grid;
    grid-template-columns: 1.35fr 1fr;
    gap: 34px;
    align-items: center;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 30px;
}

.header-kpis {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
}

.header-kpi {
    background: rgba(255,255,255,0.14);
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 16px;
    padding: 15px 10px;
    text-align: center;
}

.header-kpi-label {
    font-size: 12px;
    font-weight: 900;
    opacity: .95;
    text-transform: uppercase;
}

.header-kpi-number {
    font-size: 34px;
    font-weight: 950;
    color: #8FDBFF !important;
    margin-top: 4px;
}

.area-title {
    font-size: 25px;
    font-weight: 950;
    color: #001B5E;
    margin-bottom: 2px;
}

.area-subtitle {
    font-size: 14px;
    color: #536175;
    font-weight: 700;
    margin-bottom: 8px;
}

.action-title {
    font-size: 16px;
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

.small-divider {
    border-top: 1px solid #E5ECF5;
    margin: 12px 0;
}

.stTextArea textarea {
    background-color: #F1F5FA !important;
    border: 1px solid #D9E2F1 !important;
    border-radius: 12px !important;
    color: #00133F !important;
}

.stButton > button {
    border-radius: 10px;
    font-weight: 800;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: white !important;
    border: 1px solid #D9E2F1 !important;
    border-radius: 22px !important;
    box-shadow: 0 5px 18px rgba(0,0,0,0.07) !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #F7FAFE !important;
    border: 1px solid #E3EAF5 !important;
    border-radius: 16px !important;
    box-shadow: none !important;
}

.footer {
    background: #001B5E;
    color: white;
    padding: 18px 24px;
    border-radius: 18px;
    margin-top: 20px;
    text-align: center;
    font-size: 15px;
    font-weight: 600;
}

@media (max-width: 1100px) {
    .header-grid {
        grid-template-columns: 1fr;
    }

    .header-kpis {
        grid-template-columns: repeat(2, 1fr);
    }
}
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================

logo_b64 = img_to_base64(LOGO_PATH)

if logo_b64:
    logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:76px;">'
else:
    logo_html = '<div style="font-size:32px;font-weight:900;">PUCRS</div>'

header_html = f"""
<div class="header">
<div class="header-grid">
<div class="header-left">
{logo_html}
<div style="height:72px;width:2px;background:rgba(255,255,255,.45);"></div>
<div>
<div style="font-size:23px;font-weight:800;">SETOR FINANCEIRO ACADÊMICO</div>
<div style="font-size:52px;font-weight:950;line-height:1;margin-top:8px;">CALENDÁRIO DE AÇÕES</div>
<div style="font-size:20px;color:#8FDBFF!important;margin-top:14px;">Gestão e acompanhamento das demandas operacionais</div>
</div>
</div>
<div class="header-kpis">
<div class="header-kpi"><div class="header-kpi-label">Total</div><div class="header-kpi-number">{total}</div></div>
<div class="header-kpi"><div class="header-kpi-label">Concluídas</div><div class="header-kpi-number">{concluidas}</div></div>
<div class="header-kpi"><div class="header-kpi-label">Pendentes</div><div class="header-kpi-number">{pendentes}</div></div>
<div class="header-kpi"><div class="header-kpi-label">Atrasadas</div><div class="header-kpi-number">{atrasadas}</div></div>
</div>
</div>
</div>
"""

st.markdown(header_html, unsafe_allow_html=True)

if not google_status_habilitado():
    st.warning(
        "O app está lendo o calendário do Google Sheets, mas as conclusões/anotações ainda estão sendo salvas localmente. "
        "Para persistência real, configure as credenciais do Google Sheets API no Streamlit Secrets."
    )

st.subheader("Ações por área")

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
            with st.container(border=True):
                st.markdown(
                    f"""
<div style="border-top:8px solid {cor}; border-radius:18px; padding-top:14px;">
<div class="area-title">{escape(str(area))}</div>
<div class="area-subtitle">{len(dados_area)} ações</div>
</div>
                    """,
                    unsafe_allow_html=True
                )

                for idx, (_, row) in enumerate(dados_area.iterrows()):
                    id_acao = row["ID"]
                    data_txt = row["Data"].strftime("%d/%m")
                    acao = row["Ação sobre"]
                    obs = row["Observação"]
                    obs_acomp = row["Observação acompanhamento"]

                    if row["Concluída"]:
                        status_txt = "Concluída"
                        status_cor = "#16A65B"
                    elif row["Atrasada"]:
                        status_txt = "Atrasada"
                        status_cor = "#D62828"
                    elif row["Hoje"]:
                        status_txt = "Hoje"
                        status_cor = "#FFB000"
                    else:
                        status_txt = "Pendente"
                        status_cor = "#6B7280"

                    if idx > 0:
                        st.markdown('<div class="small-divider"></div>', unsafe_allow_html=True)

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

with aba_pendentes:
    renderizar_acoes(df[df["Concluída"] == False], "pendentes")

with aba_concluidas:
    renderizar_acoes(df[df["Concluída"] == True], "concluidas")

with aba_atrasadas:
    renderizar_acoes(df[df["Atrasada"] == True], "atrasadas")

with aba_todas:
    renderizar_acoes(df, "todas")

st.markdown("""
<div class="footer">
Painel interno de acompanhamento • Setor Financeiro Acadêmico PUCRS
</div>
""", unsafe_allow_html=True)
