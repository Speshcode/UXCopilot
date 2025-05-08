import streamlit as st
import pandas as pd
from uxcopilot import UXCopilot

st.set_page_config(page_title="UX Copilot Dashboard", layout="wide")
st.title("🧠 UX Copilot")
st.markdown("Интерактивный UX-агент для анализа пользовательского опыта.")

uploaded_file = st.file_uploader("📤 Загрузите данные пользователей (CSV)", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    ux = UXCopilot(df)

    num_personas = st.slider("🔢 Количество персон", 1, 10, 3)
    qualitative_count = st.slider("🎤 Кол-во интервью (качественное исследование)", 1, 10, 5)

    hypotheses = st.text_area(
        "💡 Введите гипотезы для тестирования (по одной на строку):",
        "Изменить интерфейс\nУпростить регистрацию\nДобавить обучение"
    ).splitlines()

    if st.button("🚀 Сгенерировать всё"):
        st.header("👤 Персоны")
        personas = ux.build_personas()[:num_personas]
        for i, persona in enumerate(personas):
            st.write(f"**{persona['name']}** — Сегмент: {persona['segment']}")
            st.write(f"Возраст: {persona['age_range']}")
            st.write(f"Потребности: {', '.join(persona['common_needs'])}")
            st.write(f"Боли: {', '.join(persona['pain_points'])}")
            st.markdown("---")

        st.header("🗺️ Customer Journey Map")
        for i in range(len(personas)):
            cjm = ux.build_customer_journey_map(i)
            st.subheader(f"{personas[i]['name']}")
            for stage, data in cjm.items():
                st.markdown(f"**{stage}**")
                st.write(f"🎯 Цели: {', '.join(data['goals'])}")
                st.write(f"📞 Точки контакта: {', '.join(data['touchpoints'])}")
                st.write(f"⚠️ Боли: {', '.join(data['pain_points'])}")

        st.header("🧪 Симуляция исследований")
        qualitative = ux.simulate_research("qualitative")
        qualitative['interviews'] = qualitative['interviews'][:qualitative_count]
        st.write("**Качественные:**", qualitative)
        st.write("**Количественные:**", ux.simulate_research("quantitative"))

        st.header("🧪 Тестирование гипотез")
        test_results = ux.test_interface_hypotheses(hypotheses)
        for h, res in test_results.items():
            st.markdown(f"**{h}** — 💡 Confidence: {res['confidence']}, 💥 Impact: {res['impact']}, 🧭 Рекомендация: {res['recommendation']}")

        st.header("📄 Отчёт в PDF")
        ux.generate_pdf_report("output/ux_report.pdf")
        with open("output/ux_report.pdf", "rb") as file:
            st.download_button("📥 Скачать PDF", file, file_name="UX_Report.pdf", mime="application/pdf")

else:
    st.info("Пожалуйста, загрузите CSV-файл с клиентскими данными.")
