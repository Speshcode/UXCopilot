import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os

def run_first_click_test():
    st.header("🖱️ First Click Attention Insight")

    uploaded_image = st.file_uploader("📷 Загрузите макет интерфейса (JPG или PNG)", type=["png", "jpg", "jpeg"])

    if uploaded_image:
        image = Image.open(uploaded_image)
        st.image(image, caption="Макет для анализа", use_container_width=True)

        width, height = image.size
        num_clicks = st.slider("🔢 Кол-во симулируемых пользователей", 10, 100, 40)

        # Генерация случайных координат
        x = np.random.randint(0, width, num_clicks)
        y = np.random.randint(0, height, num_clicks)

        # Визуализация тепловой карты
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.imshow(image)
        heatmap_data, _, _ = np.histogram2d(x, y, bins=[width // 10, height // 10])
        ax.imshow(heatmap_data.T, cmap="hot", alpha=0.5, extent=(0, width, height, 0))
        ax.set_title("🔥 Тепловая карта кликов")
        ax.set_xticks([])
        ax.set_yticks([])

        heatmap_path = "output/first_click_heatmap.png"
        os.makedirs("output", exist_ok=True)
        plt.savefig(heatmap_path, bbox_inches='tight')
        plt.close()

        st.image(heatmap_path, caption="Тепловая карта", use_container_width=True)

        # AOI — верх, середина, низ
        top = y < height / 3
        middle = (y >= height / 3) & (y < 2 * height / 3)
        bottom = y >= 2 * height / 3

        top_pct = round(np.sum(top) / num_clicks * 100, 1)
        middle_pct = round(np.sum(middle) / num_clicks * 100, 1)
        bottom_pct = round(np.sum(bottom) / num_clicks * 100, 1)

        # Clarity Score: чем меньше стандартное отклонение распределения — тем выше концентрация
        clarity = round(100 - np.std(heatmap_data) * 2, 1)
        if clarity < 0:
            clarity = 0.0

        st.markdown(f"### 🧠 Clarity Score: `{clarity} / 100`")
        st.markdown("### 📊 Внимание по зонам:")
        st.markdown(f"- 🔼 Верх: **{top_pct}%**")
        st.markdown(f"- 🔽 Центр: **{middle_pct}%**")
        st.markdown(f"- ⬇️ Низ: **{bottom_pct}%**")

        # Метрики CSI и NPS
        col1, col2 = st.columns(2)
        col1.metric("🟢 Удовлетворённость (CSI)", round(np.random.uniform(3.5, 5), 2))
        col2.metric("🧪 Лояльность (NPS)", round(np.random.uniform(40, 80), 1))

        with open(heatmap_path, "rb") as img_file:
            st.download_button("📥 Скачать тепловую карту", img_file, file_name="first_click_heatmap.png", mime="image/png")
    else:
        st.info("Пожалуйста, загрузите изображение для анализа.")
