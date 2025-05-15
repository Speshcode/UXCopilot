
import streamlit as st
import pandas as pd
from uxcopilot import UXCopilot
import numpy as np
import os

from first_click_attention import run_first_click_test

st.set_page_config(page_title="UX Copilot", layout="wide")
st.title("🧠 UX Copilot")

if "screen" not in st.session_state:
    st.session_state["screen"] = None

uploaded_file = st.file_uploader("📤 Загрузите CSV с клиентами", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    df = pd.DataFrame({
        'id': range(1, 11),
        'age': [25, 32, 40, 29, 35, 45, 52, 23, 30, 38],
        'segment': ['A', 'A', 'B', 'B', 'A', 'C', 'C', 'A', 'B', 'C'],
        'needs': ['быстро', 'удобно', 'надёжно', 'быстро', 'удобно', 'дёшево', 'быстро', 'удобно', 'надёжно', 'дёшево'],
        'pain_points': ['запутанный интерфейс', 'медленная загрузка', 'сложная регистрация', 'запутанный интерфейс', 'медленная загрузка',
                        'отсутствие поддержки', 'сложная регистрация', 'запутанный интерфейс', 'медленная загрузка', 'отсутствие поддержки']
    })

ux = UXCopilot(df)
quant = ux.simulate_research("quantitative")

col1, col2 = st.columns(2)
col1.metric("🟢 Удовлетворённость (CSI)", quant["survey_results"]["satisfaction"], f"на {pd.Timestamp.today().strftime('%d.%m.%Y')}")
col2.metric("📈 Лояльность (NPS)", quant["survey_results"]["nps"], f"на {pd.Timestamp.today().strftime('%d.%m.%Y')}")

st.markdown("## 🧩 Выберите действие")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📍 Построить CJM"):
        st.session_state["screen"] = "cjm"
    if st.button("🎤 Глубинное интервью"):
        st.session_state["screen"] = "interview"
with col2:
    if st.button("💡 Проверить гипотезы"):
        st.session_state["screen"] = "hypo"
    if st.button("📊 Только метрики"):
        st.session_state["screen"] = "metrics"
with col3:
    if st.button("🔥 First Click"):
        st.session_state["screen"] = "click"

if st.session_state["screen"] == "cjm":
    st.header("🗺️ Customer Journey Map")
    personas = ux.build_personas()
    idx = st.selectbox("Выберите персону", list(range(len(personas))), format_func=lambda i: personas[i]['name'])
    cjm = ux.build_customer_journey_map(idx)
    img_path = ux.draw_cjm_timeline(personas[idx]["name"], cjm)
    st.image(img_path, caption=f"CJM: {personas[idx]['name']}", use_container_width=True)
    if st.button("📄 Сформировать PDF"):
        ux.generate_pdf_report("output/ux_report.pdf", selected_personas=[personas[idx]], date=pd.Timestamp.today().strftime('%d.%m.%Y'))
        with open("output/ux_report.pdf", "rb") as f:
            st.download_button("📥 Скачать PDF", f, file_name="UX_Report.pdf", mime="application/pdf")

elif st.session_state["screen"] == "hypo":
    st.header("💡 Проверка гипотез")
    hypotheses = st.text_area("Введите гипотезы (по одной на строку):", "Изменить CTA\nСократить шаги\nДобавить обучение").splitlines()
    if st.button("Проверить гипотезы"):
        results = ux.test_interface_hypotheses(hypotheses)
        for h, res in results.items():
            st.markdown(f"**{h}** — Confidence: `{res['confidence']}`, Impact: `{res['impact']}`, Рекомендация: `{res['recommendation']}`")

elif st.session_state["screen"] == "click":
    run_first_click_test()

elif st.session_state["screen"] == "interview":
    st.header("🎙️ Глубинное интервью")
    qualitative = ux.simulate_research("qualitative", interview_limit=5)
    st.subheader("🧩 Основные темы:")
    st.write(", ".join(qualitative["themes"]))
    st.subheader("📋 Ответы пользователей:")
    for i, pain in enumerate(qualitative["interviews"], 1):
        st.markdown(f"{i}. {pain}")

elif st.session_state["screen"] == "metrics":
    st.header("📊 Замеры")
    st.metric("🟢 Удовлетворённость (CSI)", quant["survey_results"]["satisfaction"])
    st.metric("📈 Лояльность (NPS)", quant["survey_results"]["nps"])
    st.metric("👥 Кол-во респондентов", quant["sample_size"])
