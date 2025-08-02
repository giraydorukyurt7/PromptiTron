# modules/pdfgenerator.py

from fpdf import FPDF
from modules.utils import get_timestamp
from pathlib import Path

class PDFGenerator(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "📄 PromptiTron Raporu", ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f'Sayfa {self.page_no()}', 0, 0, 'C')

    def add_section(self, title, content):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, ln=True)
        self.set_font("Arial", "", 11)
        self.multi_cell(0, 8, content)
        self.ln(5)

def generate_pdf_report(sections: dict, filename=None):
    pdf = PDFGenerator()
    pdf.add_page()

    for section_title, section_content in sections.items():
        pdf.add_section(section_title, section_content)

    filename = filename or f"report_{get_timestamp()}.pdf"
    out_path = Path("Outputs/pdfs") / filename
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(out_path))

    return str(out_path)