from app.services.pdf_generator import PDFGenerator
from app.services.email_service import EmailService
from app.services.monthly_report import MonthlyReportService

async def generate_and_send_monthly_reports():
    print("[Scheduler] Waking up to send monthly reports...")
    
    dummy_email = "test@example.com"
    dummy_title = "May 2026 Report"
    
    pdf_path = PDFGenerator.create_report_pdf(
        title=dummy_title, 
        user_note="Patient slept well this month.", 
        author_note="No major issues observed."
    )
    
    email_svc = EmailService()
    await email_svc.send_monthly_report(dummy_email, dummy_title, pdf_path)
    
    print("[Scheduler] Finished sending reports!")