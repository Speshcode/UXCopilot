import random
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from typing import List, Dict

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
        stages = ['Awareness', 'Consideration', 'Purchase', 'Retention', 'Advocacy']
        journey = {
            stage: {
                'goals': [f'Goal {i+1}' for i in range(2)],
                'touchpoints': [f'Touchpoint {i+1}' for i in range(2)],
                'pain_points': persona['pain_points']
            }
            for stage in stages
        }
        self.journey_maps[persona['name']] = journey
        return journey

    def simulate_research(self, method: str = 'qualitative', interview_limit=5) -> Dict:
        if method == 'qualitative':
            return {
                'interviews': random.choices(self.customer_data['pain_points'], k=interview_limit),
                'themes': ['Usability', 'Speed', 'Content']
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
                'impact': random.choice(['High', 'Medium', 'Low']),
                'recommendation': random.choice(['Implement', 'Refine', 'Discard'])
            }
            for hypo in hypotheses
        }
        return self.test_results

    def visualize_age_distribution(self):
        plt.figure()
        self.customer_data['age'].hist(bins=10)
        plt.title("Age Distribution")
        plt.xlabel("Age")
        plt.ylabel("Number of Customers")
        plt.savefig("output/age_distribution.png")
        plt.close()

    def generate_pdf_report(self, filename="output/ux_report.pdf", selected_personas=None, tested_hypotheses=None):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="UX Research Report", ln=True, align="C")
        pdf.ln(10)

        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(200, 10, txt="Personas:", ln=True)
        pdf.set_font("Arial", size=11)
        for p in (selected_personas or self.personas):
            pdf.cell(0, 10, f"- {p['name']} (Segment: {p['segment']}, Age: {p['age_range'][0]}-{p['age_range'][1]})", ln=True)

        pdf.ln(5)
        self.visualize_age_distribution()
        pdf.image("output/age_distribution.png", w=180)
        pdf.ln(10)

        if tested_hypotheses and self.test_results:
            pdf.set_font("Arial", style='B', size=12)
            pdf.cell(200, 10, txt="Tested Hypotheses:", ln=True)
            pdf.set_font("Arial", size=11)
            for h in tested_hypotheses:
                result = self.test_results.get(h, {})
                pdf.multi_cell(0, 10, f"{h} — Confidence: {result.get('confidence', '-')}, Impact: {result.get('impact', '-')}, Recommendation: {result.get('recommendation', '-')}")
            pdf.ln(5)

        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(200, 10, txt="General Recommendations:", ln=True)
        pdf.set_font("Arial", size=11)
        for r in ["Улучшить удобство интерфейса", "Оптимизировать критические точки пути", "Сфокусироваться на гипотезах с высоким потенциалом"]:
            pdf.cell(0, 10, f"- {r}", ln=True)

        pdf.output(filename)
