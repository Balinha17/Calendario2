import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calendário de Ações", layout="wide")

df = pd.read_excel("Calendário2.xlsx")

st.markdown("""
<style>
.header {
    background: linear-gradient(90deg, #001B5E, #003B95);
    padding: 28px;
    border-radius: 18px;
    color: white;
    margin-bottom: 25px;
}
.card {
    background: white;
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.08);
    border: 1px solid #dbe4f0;
    min-height: 320px;
}
.area-title {
    font-size: 22px;
    font-weight: 800;
    color: #001B5E;
}
.date-pill {
    display: inline-block;
    background: #0077FF;
    color: white;
    padding: 5px 12px;
    border-radius: 12px;
    font-weight: 700;
    margin-right: 8px;
}
.action {
    margin-top: 14px;
    font-size: 15px;
    color: #111;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header">
    <div style="font-size:22px;font-weight:700;">PUCRS</div>
    <div style="font-size:44px;font-weight:900;">CALENDÁRIO DE AÇÕES</div>
    <div style="font-size:20px;color:#8FC7FF;">Setor Financeiro</div>
</div>
""", unsafe_allow_html=True)

st.metric("Total de ações", len(df))

areas = df["Área"].dropna().unique()

cols = st.columns(len(areas))

for col, area in zip(cols, areas):
    dados_area = df[df["Área"] == area]

    html = f"""
    <div class="card">
        <div class="area-title">{area}</div>
        <hr>
    """

    for _, row in dados_area.iterrows():
        data = pd.to_datetime(row["Data"]).strftime("%d/%m")
        acao = row["Ação"]

        html += f"""
        <div class="action">
            <span class="date-pill">{data}</span>
            {acao}
        </div>
        """

    html += "</div>"

    col.markdown(html, unsafe_allow_html=True)