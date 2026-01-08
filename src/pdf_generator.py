from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from io import BytesIO


def pdf_receipt_generator(data_input_api):
    # data = data_input_api[0].get("fields", {})
    data = data_input_api.get("fields", {})
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
    return pdf_buffer

# testing
# test_data = {
#         "trip_id": "12345",
#         "passenger_name": "John Doe",
#         "pickup": "123 Main St",
#         "dropoff": "456 Oak Ave",
#         "fare": "$25.00",
#         "date": "2025-01-01"
#     }

# pdf_buffer = pdf_receipt_generator(test_data)
# with open("test_receipt.pdf", "wb") as f:
#     f.write(pdf_buffer.read())