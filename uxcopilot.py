import random
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from typing import List, Dict
import os

class UXCopilot:
    def __init__(self, customer_data: pd.DataFrame):
        self.customer_data = customer_data
        self.personas = []
        self.journey_maps = {}
        self.test_results = {}

    def build_personas(self) -> List[Dict]:
        segments = self.customer_data.groupby('segment')
        self.personas.clear()
        for i, (name, group) in enumerate(segments):
            persona = {
                'name': f'Persona {i + 1}',
                'segment': name,
                'age_range': (group['age'].min(), group['age'].max()),
                'common_needs': group['needs'].mode().tolist(),
                'pain_points': group['pain_points'].mode().tolist()
            }
            self.personas.append(persona)
        return self.personas

    def build_customer_journey_map(self, persona_index: int) -> Dict:
        persona = self.personas[persona_index]
        stage_names = {
            'Awareness': 'Осведомлённость',
            'Consideration': 'Рассмотрение',
            'Purchase': 'Покупка',
            'Retention': 'Удержание',
            'Advocacy': 'Адвокация'
        }
        stages = stage_names.keys()
        journey = {
            stage_names[stage]: {
                'goals': [f'Цель {i+1}' for i in range(2)],
                'touchpoints': [f'Точка контакта {i+1}' for i in range(2)],
                'pain_points': persona['pain_points']
            }
            for stage in stages
        }
        self.journey_maps[persona['name']] = journey
        return journey

    def draw_cjm_timeline(self, persona_name: str, cjm: Dict) -> str:
        stages = list(cjm.keys())
        fig, ax = plt.subplots(figsize=(12, 2))
        ax.set_xlim(0, len(stages))
        ax.set_ylim(0, 1)
        ax.axis('off')

        for i, stage in enumerate(stages):
            ax.add_patch(plt.Rectangle((i, 0), 1, 1, edgecolor='black', facecolor='#DCEEFF'))
            ax.text(i + 0.5, 0.5, stage, va='center', ha='center', fontsize=9, fontweight='bold')

        plt.title(f"Карта пути клиента: {persona_name}", fontsize=12)
        os.makedirs("output", exist_ok=True)
        output_path = f"output/cjm_timeline_{persona_name.replace(' ', '_')}.png"
        plt.savefig(output_path, bbox_inches='tight')
        plt.close()
        return output_path

    def simulate_research(self, method: str = 'qualitative', interview_limit=5) -> Dict:
        if method == 'qualitative':
            return {
                'interviews': random.choices(self.customer_data['pain_points'], k=interview_limit),
                'themes': ['Удобство', 'Скорость', 'Контент']
            }
        else:
            return {
                'survey_results': {
                    'satisfaction': round(random.uniform(3, 5), 2),
                    'nps': random.randint(-100, 100)
                },
                'sample_size': len(self.customer_data)
            }

    def test_interface_hypotheses(self, hypotheses: List[str]) -> Dict:
        self.test_results = {
            hypo: {
                'confidence': round(random.uniform(0.7, 0.99), 2),
                'impact': random.choice(['Высокий', 'Средний', 'Низкий']),
                'recommendation': random.choice(['Реализовать', 'Уточнить', 'Отклонить'])
            }
            for hypo in hypotheses
        }
        return self.test_results

    def visualize_age_distribution(self):
        plt.figure()
        self.customer_data['age'].hist(bins=10)
        plt.title("Распределение по возрасту")
        plt.xlabel("Возраст")
        plt.ylabel("Количество клиентов")
        os.makedirs("output", exist_ok=True)
        plt.savefig("output/age_distribution.png")
        plt.close()

    def generate_pdf_report(self, filename="output/ux_report.pdf", selected_personas=None, tested_hypotheses=None):
        pdf = FPDF()
        pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("DejaVu", size=12)

        pdf.cell(200, 10, txt="UX Отчёт по исследованию", ln=True, align="C")
        pdf.ln(10)

        pdf.set_font("DejaVu", size=12)
        pdf.cell(200, 10, txt="Персоны:", ln=True)
        pdf.set_font("DejaVu", size=11)
        for p in (selected_personas or self.personas):
            pdf.cell(0, 10, f"- {p['name']} (Сегмент: {p['segment']}, Возраст: {p['age_range'][0]}–{p['age_range'][1]})", ln=True)

        pdf.ln(5)
        self.visualize_age_distribution()
        pdf.image("output/age_distribution.png", w=180)
        pdf.ln(10)

        # CJM timeline
        pdf.set_font("DejaVu", size=12)
        pdf.cell(200, 10, txt="Карта пути клиента (Customer Journey Map):", ln=True)
        for persona in (selected_personas or self.personas):
            name = persona["name"]
            cjm = self.journey_maps.get(name, {})
            img_path = self.draw_cjm_timeline(name, cjm)
            pdf.image(img_path, w=180)
            pdf.ln(5)

        if tested_hypotheses and self.test_results:
            pdf.set_font("DejaVu", size=12)
            pdf.cell(200, 10, txt="Протестированные гипотезы:", ln=True)
            pdf.set_font("DejaVu", size=11)
            for h in tested_hypotheses:
                result = self.test_results.get(h, {})
                pdf.multi_cell(0, 10, f"{h} — Уверенность: {result.get('confidence', '-')}, Влияние: {result.get('impact', '-')}, Рекомендация: {result.get('recommendation', '-')}")
            pdf.ln(5)

        pdf.set_font("DejaVu", size=12)
        pdf.cell(200, 10, txt="Общие рекомендации:", ln=True)
        pdf.set_font("DejaVu", size=11)
        for r in ["Упростить навигацию", "Оптимизировать ключевые экраны", "Сосредоточиться на приоритетных гипотезах"]:
            pdf.cell(0, 10, f"- {r}", ln=True)

        pdf.output(filename)
