import pandas as pd
import segno
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
import tempfile
import shutil
import math

def generate_qr_codes_from_excel(excel_file, output_pdf, qr_size=50):
    # Create a temporary directory to store QR code images
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Read the Excel file, focusing on column A
        df = pd.read_excel(excel_file)
        codes = df.iloc[:, 0].astype(str)  # Convert column A values to strings
        
        qr_files = []
        
        # Generate QR code for each entry
        for i, code in enumerate(codes):
            if pd.notna(code) and code.strip():  # Check if code is not empty
                # Clean the code value
                clean_code = str(code).strip()
                
                # Create QR code using segno with medium error correction
                qr = segno.make(clean_code, error='m')
                
                # Save the QR code image
                qr_file = os.path.join(temp_dir, f"qr_{i}.png")
                
                # Calculate scale to achieve the desired size
                # Segno uses a different scaling approach
                # We need to determine the scale factor based on the desired size
                scale = max(1, int(qr_size / 25))  # Approximate scale factor
                
                # Save with appropriate scale and minimal border
                qr.save(qr_file, scale=scale, border=1)
                
                qr_files.append((qr_file, clean_code))
        
        # Create PDF with QR codes
        create_pdf_with_qr_codes(qr_files, output_pdf, qr_size)
        
        print(f"Successfully created PDF with QR codes: {output_pdf}")
        print(f"Total QR codes generated: {len(qr_files)}")
        
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)

def create_pdf_with_qr_codes(qr_files, output_pdf, qr_size):
    # PDF page setup with A4 size
    c = canvas.Canvas(output_pdf, pagesize=A4)
    width, height = A4  # A4 is 595.2 x 841.8 points
    
    # Define margins and spacing
    page_margin = 5  # margin from edge of page
    qr_margin = 5     # margin between QR codes
    
    # Calculate effective area for QR codes
    effective_width = width - 2 * page_margin
    effective_height = height - 2 * page_margin
    
    # Calculate QR code size with border
    qr_with_border = qr_size + 2 * qr_margin
    
    # Calculate how many QR codes can fit per row and column
    cols = math.floor(effective_width / qr_with_border)
    rows = math.floor(effective_height / qr_with_border)
    
    # Recalculate margins to center the grid
    h_spacing = (effective_width - (cols * qr_size)) / (cols + 1)
    v_spacing = (effective_height - (rows * qr_size)) / (rows + 1)
    
    # Debug information
    print(f"A4 size: {width} x {height} points")
    print(f"QR size: {qr_size} points")
    print(f"Grid: {cols} columns x {rows} rows")
    print(f"QR codes per page: {cols * rows}")
    
    # Calculate total pages needed
    total_pages = math.ceil(len(qr_files) / (cols * rows))
    print(f"Total pages: {total_pages}")
    
    # Add QR codes to PDF
    for page in range(total_pages):
        if page > 0:
            c.showPage()  # Start a new page
            
        # Draw page number
        #c.setFont("Helvetica", 8)
        #c.drawString(width - 50, 20, f"Page {page + 1}/{total_pages}")
        
        # Calculate starting indices for this page
        start_idx = page * cols * rows
        end_idx = min(start_idx + cols * rows, len(qr_files))
        
        for i in range(start_idx, end_idx):
            # Calculate position in the grid
            idx_in_page = i - start_idx
            row = idx_in_page // cols
            col = idx_in_page % cols
            
            # Calculate x, y position
            x = page_margin + h_spacing + col * (qr_size + h_spacing)
            y = height - (page_margin + v_spacing + (row + 1) * qr_size + row * v_spacing)
            
            qr_file, code_text = qr_files[i]
            
            # Draw border rectangle
            c.rect(x - qr_margin, y - qr_margin, 
                   qr_size + 2 * qr_margin, qr_size + 2 * qr_margin)
            
            # Add QR code image
            c.drawImage(qr_file, x, y, width=qr_size, height=qr_size)
            
            # Add small text label below the QR code
            #c.setFont("Helvetica", 6)
            # Truncate long codes for display
            #display_text = code_text[:15] + "..." if len(code_text) > 15 else code_text
            #text_width = c.stringWidth(display_text, "Helvetica", 6)
            #c.drawString(x + (qr_size - text_width)/2, y - 10, display_text)
    
    # Save the PDF
    c.save()

if __name__ == "__main__":
    # Replace with your Excel file path and desired output PDF path
    excel_file = "Country delight QR.xlsx"
    output_pdf = "qr_codes50s.pdf"
    
    # You can adjust QR size as needed
    generate_qr_codes_from_excel(excel_file, output_pdf, qr_size=50)
