# USE REPORTLAB LIBRARY FOR PDF GENERATION
import io
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from datetime import datetime

def generate_quote_pdf(quote, current_user, trade_ins=None, finance=None, packages=None):
    """
    Given a Quote object (and optional TradeIns, Finance, packages list),
    returns a BytesIO containing the PDF laid out to mimic my HTML/Tailwind design.
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    def draw_header(canvas):
        # --- HEADER BACKGROUND ---
        header_height = 40 * mm
        canvas.setFillColor(colors.HexColor('#1F2937'))
        canvas.rect(0, height - header_height, width, header_height, fill=1, stroke=0)

        # --- LOGO & COMPANY INFO ---
        logo_path = os.path.join('static', 'images', 'bmw-logo.png')
        logo_width = 25 * mm
        logo_height = 25 * mm
        canvas.drawImage(logo_path,
                    x=15 * mm,
                    y=height - header_height + (header_height - logo_height) / 2,
                    width=logo_width,
                    height=logo_height,
                    mask='auto')

        text_x = 45 * mm
        canvas.setFont('Helvetica-Bold', 16)
        canvas.setFillColor(colors.white)
        canvas.drawString(text_x, height - 15 * mm, "Performance Motors Limited")

        canvas.setFont('Helvetica', 9)
        canvas.drawString(text_x, height - 20 * mm, "303 Alexandra Rd, Singapore 159941")
        
        # Add Date
        today = datetime.now().strftime("%d %B %Y")
        canvas.drawString(text_x, height - 25 * mm, today)

        # --- SALES CONSULTANT INFO (right) ---
        right_x = width - 15 * mm
        canvas.setFont('Helvetica', 8)
        canvas.drawRightString(right_x, height - 12 * mm, "Sales Consultant:")
        canvas.setFont('Helvetica-Bold', 10)
        canvas.drawRightString(right_x, height - 17 * mm, current_user.name)
        canvas.setFont('Helvetica', 8)
        canvas.drawRightString(right_x, height - 22 * mm, current_user.phone_number)

        return height - header_height - 20 * mm

    def draw_footer(canvas, y_position):
        footer_y = 15 * mm
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#6B7280'))
        canvas.drawCentredString(width / 2, footer_y, f"Thank you for choosing Performance Motors Limited. Please contact {current_user.name} for any questions.")
        return footer_y + 20 * mm  # Return the space taken by footer

    def check_page_break(y_pos, needed_space):
        """Helper function to check if we need a page break"""
        if y_pos - needed_space < 60 * mm:  # Increased minimum space needed
            footer_height = draw_footer(c, y_pos)
            c.showPage()
            return draw_header(c)
        return y_pos

    # Start first page
    y = draw_header(c)
    page_number = 1

    # Customer & Vehicle
    c.setFont('Helvetica-Bold', 12)
    c.setFillColor(colors.HexColor('#374151'))
    c.drawString(15 * mm, y, "Customer")
    c.drawString(100 * mm, y, "Vehicle Model")

    c.setFont('Helvetica', 10)
    c.setFillColor(colors.black)
    c.drawString(15 * mm, y - 6 * mm, quote.customer_name)
    c.drawString(15 * mm, y - 11 * mm, quote.customer_contact)
    c.drawString(100 * mm, y - 6 * mm, quote.model)

    y -= 25 * mm  # Increased spacing

    # --- Price Breakdown Table ---
    y = check_page_break(y, 50 * mm)  # Check if we need space for price breakdown
    table_y = y
    line_height = 6 * mm
    col1_x = 15 * mm
    col2_x = width - 50 * mm

    rows = [
        ("Retail Price:", f"${quote.retail_price:,.2f}"),
        ("Discount:", f"-${quote.discount:,.2f}", colors.HexColor('#10B981')),
        ("Add-Ons:", f"${quote.addons:,.2f}"),
        ("Net Price:", f"${quote.net_price:,.2f}", None, True),
    ]

    c.setFont('Helvetica', 10)
    for i, row in enumerate(rows):
        text_label, text_value = row[0], row[1]
        color = row[2] if len(row) > 2 and row[2] else colors.black
        bold = len(row) > 3 and row[3]
        y0 = table_y - i * line_height

        if bold:
            c.setFont('Helvetica-Bold', 11)
            c.setFillColor(colors.HexColor('#111827'))
        else:
            c.setFont('Helvetica', 10)
            c.setFillColor(color)

        c.drawString(col1_x, y0, text_label)
        c.drawRightString(col2_x + 35 * mm, y0, text_value)

        # draw separator line under every row
        c.setStrokeColor(colors.HexColor('#D1D5DB'))
        c.setLineWidth(0.5)
        c.line(col1_x, y0 - 2 * mm, width - 15 * mm, y0 - 2 * mm)

    y = table_y - len(rows) * line_height - 20 * mm

    # --- OPTIONAL Trade-In ---
    if trade_ins:
        y = check_page_break(y, 40 * mm)  # Check if we need space for trade-in section
        
        c.setFont('Helvetica-Bold', 12)
        c.setFillColor(colors.HexColor('#374151'))
        c.drawString(15 * mm, y, "Trade-In")
        c.setFont('Helvetica', 10)
        y -= 6 * mm

        ti_rows = [
            ("Car Plate:", trade_ins.plate),
            ("Trade-In Value:", f"${trade_ins.trade_in_value:,.2f}"),
            ("Outstanding Loan:", f"-${trade_ins.outstanding_loan:,.2f}"),
            ("Balance:", f"${trade_ins.balance:,.2f}", True),
        ]
        for i, row in enumerate(ti_rows):
            y0 = y - i * line_height
            
            bold = len(row) > 2 and row[2]
            c.setFont('Helvetica-Bold' if bold else 'Helvetica', 10)
            c.setFillColor(colors.black)
            c.drawString(col1_x, y0, row[0])
            c.drawRightString(col2_x + 35 * mm, y0, row[1])
            c.setStrokeColor(colors.HexColor('#D1D5DB'))
            c.line(col1_x, y0 - 2 * mm, width - 15 * mm, y0 - 2 * mm)
        y = y0 - 20 * mm  # consistent spacing before next section

    # --- OPTIONAL Finance ---
    if finance:
        y = check_page_break(y, 50 * mm)  # Check if we need space for finance section
        
        c.setFont('Helvetica-Bold', 12)
        c.setFillColor(colors.HexColor('#374151'))
        c.drawString(15 * mm, y, "Finance Details")
        c.setFont('Helvetica', 10)
        y -= 6 * mm

        fin_rows = [
            ("Bank:", finance.bank),
            ("Loan Amount:", f"${finance.loan_amount:,.2f}"),
            ("Tenure:", f"{finance.tenure_months} months"),
            ("Interest Rate:", f"{finance.interest_rate:.2f}%"),
            ("Monthly Installment:", f"${finance.monthly_installment:,.2f}", True),
        ]
        for i, row in enumerate(fin_rows):
            y0 = y - i * line_height

            bold = len(row) > 2 and row[2]
            c.setFont('Helvetica-Bold' if bold else 'Helvetica', 10)
            c.setFillColor(colors.black)
            c.drawString(col1_x, y0, row[0])
            c.drawRightString(col2_x + 35 * mm, y0, row[1])
            c.setStrokeColor(colors.HexColor('#D1D5DB'))
            c.line(col1_x, y0 - 2 * mm, width - 15 * mm, y0 - 2 * mm)
        y = y0 - 20 * mm  # Consistent spacing before next section

    # --- OPTIONAL Packages List ---
    if packages:
        # Calculate needed space for packages (15mm per package plus headers)
        needed_space = (len(packages) * 10 * mm) + 30 * mm
        y = check_page_break(y, needed_space)

        c.setFont('Helvetica-Bold', 12)
        c.setFillColor(colors.HexColor('#374151'))
        c.drawString(15 * mm, y, "Packages")
        y -= 10 * mm  # Increased spacing before packages
        c.setFont('Helvetica', 10)
        
        for pkg in packages:
            if pkg.strip():
                # Check if we need a page break for each package
                y = check_page_break(y, 15 * mm)
                c.drawString(20 * mm, y, f"• {pkg}")
                y -= 8 * mm  # Increased spacing between package items
        
        y -= 15 * mm  # Increased spacing after packages section

    # --- FOOTER TOTAL DUE AT SIGNING ---
    y = check_page_break(y, 30 * mm)  # Check if we need space for total section

    total_due = quote.net_price - (trade_ins.balance if trade_ins else 0) - (finance.loan_amount if finance else 0)
    c.setFont('Helvetica-Bold', 12)
    c.drawRightString(width - 15 * mm, y, f"Downpayment:")
    c.setFont('Helvetica-Bold', 14)
    c.drawRightString(width - 15 * mm, y - 6 * mm, f"${total_due:,.2f}")

    # Draw footer on the last page
    footer_height = draw_footer(c, y - 6 * mm)

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer
