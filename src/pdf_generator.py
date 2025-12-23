from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from io import BytesIO


def pdf_receipt_generator(data_input_api):
    data = data_input_api[0].get("fields", {})
    # Create PDF
    # pdf_file = "trip_receipt.pdf"
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=LETTER)
    width, height = LETTER
    
    y_position = height - 50  # start from top


    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position, "TRIP RECEIPT")
    y_position -= 30

    c.setFont("Helvetica", 12)
    for key, value in data.items():
        text_line = f"{key}: {value}"
        c.drawString(50, y_position, text_line)
        y_position -= 20  # move down for next line
    c.save()
    pdf_buffer.seek(0)