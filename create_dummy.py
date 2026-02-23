from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

def create_dummy_pdf(filename="dummy_offer.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []

    data = [
        ['Name', 'Debayan Debnath'],
        ['Designation', 'Management Trainee'],
        ['Entity', 'GFPL'],
        ['Business Unit', 'Enabling Functions'],
        ['Department', 'Human Resources'],
        ['Sub-Department', 'Generalist'],
        ['Competency', 'Shared (HR - Generalist)'],
        ['Band', '2'],
        ['Grade', '2.2']
    ]

    # Create a table that matches the screenshot
    t = Table(data, colWidths=[200, 200])
    t.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))

    elements.append(t)
    doc.build(elements)
    print(f"Created {filename}")

if __name__ == "__main__":
    create_dummy_pdf()
