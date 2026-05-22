from fpdf import FPDF
import tempfile
import os

class PDFGenerator:
    @staticmethod
    def create_report_pdf(title: str, user_note: str, author_note: str) -> str:
        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.add_page()
        
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align="C")
        
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 10, "Patient Notes:", new_x="LMARGIN", new_y="NEXT")       
        pdf.set_font("helvetica", "", 10)
        pdf.multi_cell(0, 8, user_note)
        
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 10, "Caregiver Notes:", new_x="LMARGIN", new_y="NEXT") 
        pdf.set_font("helvetica", "", 10)
        pdf.multi_cell(0, 8, author_note)
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(temp_file.name)
        
        return temp_file.name