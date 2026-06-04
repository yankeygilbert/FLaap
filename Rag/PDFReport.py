from fpdf import FPDF
import io

def generate_pdf(text_content):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_margins(left=10, top=10, right=10)
    
    # Set font to standard Arial, bold for title if needed, size 12
    pdf.set_font("Arial", size=12)
    
    # Split text by newlines and write each line to the PDF
    for line in text_content.split('\n'):
        # Multi_cell handles text wrapping smoothly
        pdf.multi_cell(w=0, h=10, text=line)
    
    # Output the PDF as a byte string using 'O' format (dest='S' in older fpdf)
    pdf_bytes = pdf.output()
    return pdf_bytes