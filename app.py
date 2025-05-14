
import streamlit as st
import pandas as pd
from uxcopilot import UXCopilot

st.set_page_config(page_title="UX Copilot", layout="wide")
st.title("🧠 UX Copilot")

st.sidebar.header("🔧 Выберите, что вы хотите сделать:")
task = st.sidebar.radio("", [
    "Построить CJM",
    "Проверить гипотезы",
    "Тест First Click (тепловая карта)",
    "Глубинное интервью",
    "Замер NPS и CSI"
])

uploaded_file = st.sidebar.file_uploader("📤 Загрузите CSV с клиентами", type=["csv"])
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

if task == "Построить CJM":
    st.header("🗺️ Customer Journey Map")
    personas = ux.build_personas()
    idx = st.selectbox("Выберите персону", list(range(len(personas))), format_func=lambda i: personas[i]['name'])
    cjm = ux.build_customer_journey_map(idx)
    img_path = ux.draw_cjm_timeline(personas[idx]["name"], cjm)
    st.image(img_path, caption=f"CJM: {personas[idx]['name']}", use_column_width=True)

    if st.button("📄 Сформировать PDF"):
        ux.generate_pdf_report("output/ux_report.pdf", selected_personas=[personas[idx]])
        with open("output/ux_report.pdf", "rb") as f:
            st.download_button("📥 Скачать PDF", f, file_name="UX_Report.pdf", mime="application/pdf")

elif task == "Проверить гипотезы":
    st.header("💡 Проверка гипотез")
    hypotheses = st.text_area("Введите гипотезы (по одной на строку):", "Изменить CTA\nСократить шаги\nДобавить обучение").splitlines()
    if st.button("Проверить гипотезы"):
        results = ux.test_interface_hypotheses(hypotheses)
        for h, res in results.items():
            st.markdown(f"**{h}** — Confidence: `{res['confidence']}`, Impact: `{res['impact']}`, Рекомендация: `{res['recommendation']}`")

elif task == "Тест First Click (тепловая карта)":
    import numpy as np
    import matplotlib.pyplot as plt
    from PIL import Image
    import os

    st.header("🖱️ First Click Test")
    image_file = st.file_uploader("Загрузите макет (PNG/JPG)", type=["png", "jpg", "jpeg"])
    if image_file:
        img = Image.open(image_file)
        st.image(img, use_column_width=True)
        st.info("Симуляция кликов (в будущем — реальные клики)")
        w, h = img.size
        n = st.slider("Сколько кликов сгенерировать", 10, 100, 40)
        x, y = np.random.randint(0, w, n), np.random.randint(0, h, n)
        fig, ax = plt.subplots()
        ax.imshow(img)
        ax.imshow(np.histogram2d(x, y, bins=[w//10, h//10])[0].T, cmap="hot", alpha=0.5, extent=(0, w, h, 0))
        ax.set_title("🔥 Тепловая карта")
        ax.axis('off')
        path = "output/first_click_heatmap.png"
        os.makedirs("output", exist_ok=True)
        plt.savefig(path)
        st.image(path)
        col1, col2 = st.columns(2)
        col1.metric("🟢 CSI", round(np.random.uniform(3.5, 5), 2))
        col2.metric("🧪 UMUX", round(np.random.uniform(65, 95), 1))
        with open(path, "rb") as f:
            st.download_button("📥 Скачать карту", f, file_name="heatmap.png", mime="image/png")
    else:
        st.info("Загрузите изображение для теста.")

elif task == "Глубинное интервью":
    st.header("🎙️ Глубинное интервью")
    qualitative = ux.simulate_research("qualitative", interview_limit=5)
    st.subheader("🧩 Основные темы:")
    st.write(", ".join(qualitative["themes"]))
    st.subheader("📋 Ответы пользователей:")
    for i, pain in enumerate(qualitative["interviews"], 1):
        st.markdown(f"{i}. {pain}")

elif task == "Замер NPS и CSI":
    st.header("📊 Замеры")
    quantitative = ux.simulate_research("quantitative")
    st.metric("🟢 CSI", quantitative["survey_results"]["satisfaction"])
    st.metric("📈 NPS", quantitative["survey_results"]["nps"])
    st.metric("👥 Кол-во респондентов", quantitative["sample_size"])
