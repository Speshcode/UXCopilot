
import pandas as pd
from fpdf import FPDF
import matplotlib.pyplot as plt
import os

class UXCopilot:
    def __init__(self, df):
        self.df = df

    def build_personas(self):
        personas = []
        for seg in self.df["segment"].unique():
            subset = self.df[self.df["segment"] == seg]
            persona = {
                "name": f"Persona {seg}",
                "segment": seg,
                "avg_age": round(subset["age"].mean()),
                "top_needs": subset["needs"].value_counts().head(2).index.tolist(),
                "top_pains": subset["pain_points"].value_counts().head(2).index.tolist()
            }
            personas.append(persona)
        return personas

    def build_customer_journey_map(self, persona_index):
        stages = ["Осведомлённость", "Рассмотрение", "Покупка", "Удержание", "Адвокация"]
        actions = ["Ищет решение", "Сравнивает", "Пробует", "Возвращается", "Рекомендует"]
        thoughts = ["Хочу понять", "Какой вариант лучше", "Подходит ли мне", "Стоит ли остаться", "Можно ли поделиться"]
        feelings = ["😐", "🤔", "🙂", "😌", "😍"]
        return {
            "stages": stages,
            "actions": actions,
            "thoughts": thoughts,
            "feelings": feelings
        }

    def draw_cjm_timeline(self, persona_name, cjm):
        fig, ax = plt.subplots(figsize=(12, 2))
        ax.set_axis_off()
        ax.set_title(f"CJM: {persona_name}", fontsize=14)
        for i, stage in enumerate(cjm["stages"]):
            ax.text(i, 1.0, stage, ha='center', va='center', bbox=dict(boxstyle="round", fc="lightblue"))
            ax.text(i, 0.6, cjm["actions"][i], ha='center', fontsize=8)
            ax.text(i, 0.3, cjm["thoughts"][i], ha='center', fontsize=8)
            ax.text(i, 0.0, cjm["feelings"][i], ha='center', fontsize=14)
        ax.set_xlim(-1, len(cjm["stages"]))
        img_path = "output/cjm_timeline.png"
        os.makedirs("output", exist_ok=True)
        fig.savefig(img_path, bbox_inches='tight')
        plt.close(fig)
        return img_path

    def simulate_research(self, mode="qualitative", interview_limit=5):
        if mode == "qualitative":
            interviews = self.df["pain_points"].sample(min(interview_limit, len(self.df))).tolist()
            themes = pd.Series(interviews).value_counts().head(3).index.tolist()
            return {
                "interviews": interviews,
                "themes": themes
            }
        elif mode == "quantitative":
            satisfaction = round(self.df["age"].mean() % 5, 2) + 1
            nps = int((satisfaction - 3) * 30)
            return {
                "survey_results": {
                    "satisfaction": round(satisfaction, 2),
                    "nps": nps
                },
                "sample_size": len(self.df)
            }

    def test_interface_hypotheses(self, hypotheses):
        results = {}
        for h in hypotheses:
            results[h] = {
                "confidence": f"{round(70 + len(h)%20, 1)}%",
                "impact": f"{round(1 + len(h)%3, 1)}",
                "recommendation": "Тестировать" if len(h) % 2 == 0 else "Отложить"
            }
        return results

    def generate_pdf_report(self, filename, selected_personas=None, date=None):
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
        pdf.set_font("DejaVu", size=14)
        pdf.cell(200, 10, txt="UX Copilot Report", ln=True, align="C")
        if date:
            pdf.set_font("DejaVu", size=10)
            pdf.cell(200, 10, txt=f"Отчёт сформирован: {date}", ln=True, align="C")
        pdf.set_font("DejaVu", size=12)
        pdf.ln(10)
        for persona in selected_personas or []:
            pdf.cell(200, 10, txt=f"{persona['name']} (сегмент {persona['segment']})", ln=True)
            pdf.cell(200, 10, txt=f"Средний возраст: {persona['avg_age']}", ln=True)
            pdf.multi_cell(0, 10, txt=f"Потребности: {', '.join(persona['top_needs'])}")
            pdf.multi_cell(0, 10, txt=f"Боли: {', '.join(persona['top_pains'])}")
            pdf.ln(5)
        img_path = "output/cjm_timeline.png"
        if os.path.exists(img_path):
            pdf.image(img_path, w=180)
        pdf.output(filename)
