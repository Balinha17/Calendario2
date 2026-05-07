import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Calendário de Ações",
    layout="wide"
)

ARQUIVO_EXCEL = "Calendário2.xlsx"

df = pd.read_excel(ARQUIVO_EXCEL)

df.columns = df.columns.str.strip()

df = df.dropna(subset=["Data", "Área", "Ação sobre"])

df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
df = df.dropna(subset=["Data"])

st.markdown("""
<style>
.header {
    background: linear-gradient(90deg, #001B5E, #004AAD);
    padding: 32px;
    border-radius: 18px;
    color: white;
    margin-bottom: 28px;
}
.header-small {
    font-size: 22px;
    font-weight: 700;
}
.header-title {
    font-size: 46px;
    font-weight: 900;
    margin-top: 12px;
}
.header-subtitle {
    font-size: 20px;
    color: #8FC7FF;
    margin-top: 12px;
}
.metric-box {
    background: #001B5E;
    color: white;
    padding: 22px;
    border-radius: 18px;
    text-align: center;
    margin-bottom: 26px;
}
.metric-number {
    font-size: 48px;
    font-weight: 900;
    color: #7FDBFF;
}
.metric-label {
    font-size: 16px;
    font-weight: 700;
}
.card {
    background: white;
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.08);
    border: 1px solid #dbe4f0;
    min-height: 420px;
    margin-bottom: 22px;
}
.area-title {
    font-size: 22px;
    font-weight: 900;
    color: #001B5E;
    margin-bottom: 14px;
}
.action {
    margin-top: 16px;
    padding-bottom: 14px;
    border-bottom: 1px solid #edf1f7;
    font-size: 15px;
    color: #111;
}
.date-pill {
    display: inline-block;
    background: #0077FF;
    color: white;
    padding: 5px 12px;
    border-radius: 12px;
    font-weight: 800;
    margin-right: 8px;
    margin-bottom: 6px;
}
.obs {
    margin-top: 6px;
    font-size: 13px;
    color: #555;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header">
    <div class="header-small">PUCRS</div>
    <div class="header-title">CALENDÁRIO DE AÇÕES</div>
    <div class="header-subtitle">Setor Financeiro</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="metric-box">
    <div class="metric-label">TOTAL DE AÇÕES</div>
    <div class="metric-number">{len(df)}</div>
</div>
""", unsafe_allow_html=True)

areas = list(df["Área"].dropna().unique())

cores = {
    "CRÉDITOS": "#17A65B",
    "FATURAMENTO": "#6F2DBD",
    "COBRANÇA": "#FF8C00",
    "RELACIONAMENTO": "#0077FF",
    "GRADUAÇÃO ONLINE": "#00A6D6",
    "PÓS ONLINE": "#001B5E",
    "ANÁLISE": "#0077FF",
}

cols = st.columns(3)

for i, area in enumerate(areas):
    dados_area = df[df["Área"] == area].sort_values("Data")
    cor = cores.get(str(area).upper(), "#001B5E")

    html = f"""
    <div class="card" style="border-top: 8px solid {cor};">
        <div class="area-title">{area}</div>
    """

    for _, row in dados_area.iterrows():
        data = row["Data"].strftime("%d/%m")
        acao = row["Ação sobre"]
        observacao = row.get("Observação", "")

        html += f"""
        <div class="action">
            <span class="date-pill" style="background:{cor};">{data}</span>
            <strong>{acao}</strong>
        """

        if pd.notna(observacao) and str(observacao).strip():
            html += f"""
            <div class="obs">{observacao}</div>
            """

        html += "</div>"

    html += "</div>"

    cols[i % 3].markdown(html, unsafe_allow_html=True)
