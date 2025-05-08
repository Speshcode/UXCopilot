
# app.py
import streamlit as st
import pandas as pd
from uxcopilot import UXCopilot

st.set_page_config(page_title="UX Copilot Dashboard", layout="wide")

st.title("🧠 UX Copilot")
st.markdown("Интерактивный UX-дизайн ассистент для исследований и анализа пользовательского опыта.")

uploaded_file = st.file_uploader("📤 Загрузите данные пользователей (CSV)", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    st.info("Используются примерные данные")
    df = pd.DataFrame({
        'id': range(1, 11),
        'age': [25, 32, 40, 29, 35, 45, 52, 23, 30, 38],
        'segment': ['A', 'A', 'B', 'B', 'A', 'C', 'C', 'A', 'B', 'C'],
        'needs': ['fast', 'easy', 'secure', 'fast', 'easy', 'cheap', 'fast', 'easy', 'secure', 'cheap'],
        'pain_points': ['confusing UI', 'slow speed', 'complex setup', 'confusing UI', 'slow speed',
                        'poor support', 'complex setup', 'confusing UI', 'slow speed', 'poor support']
    })
