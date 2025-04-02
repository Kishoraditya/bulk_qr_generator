import pandas as pd
import segno
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
import tempfile
import shutil
import math

def generate_compact_qr_codes(excel_file, output_pdf, qr_size=50):
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
                clean_code = str(code).strip()
                
                # Try to create a Micro QR code first
                try:
                    # Attempt to create a Micro QR code with lowest error correction
                    qr = segno.make_micro(clean_code, error=None)
                except ValueError:
                    # If data is too large for Micro QR, use standard QR with low error correction
                    qr = segno.make(clean_code, error='l')
                
                # Save the QR code image
                qr_file = os.path.join(temp_dir, f"qr_{i}.png")
                
                # Calculate scale to achieve the desired size
                # For a 50px QR code with minimal border
                scale = max(1, int(qr_size / 25))
                
                # Save with minimal border (1 module)
                qr.save(qr_file, scale=scale, border=1)
                
                qr_files.append(qr_file)
        
        # Create PDF with QR codes
        create_compact_pdf(qr_files, output_pdf, qr_size)
        
        print(f"Successfully created PDF with {len(qr_files)} QR codes: {output_pdf}")
        
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)

def create_compact_pdf(qr_files, output_pdf, qr_size):
    # PDF page setup with A4 size
    c = canvas.Canvas(output_pdf, pagesize=A4)
    width, height = A4  # A4 is 595.2 x 841.8 points
    
    # Define minimal margins
    margin = 5  # 5pt margin from edge and between QR codes
    
    # Calculate effective area for QR codes
    effective_width = width - 2 * margin
    effective_height = height - 2 * margin
    
    # Calculate QR code size with minimal spacing
    qr_with_spacing = qr_size + margin
    
    # Calculate how many QR codes can fit per row and column
    cols = math.floor(effective_width / qr_with_spacing)
    rows = math.floor(effective_height / qr_with_spacing)
    
    # Calculate actual spacing to distribute QR codes evenly
    h_spacing = (effective_width - (cols * qr_size)) / (cols + 1)
    v_spacing = (effective_height - (rows * qr_size)) / (rows + 1)
    
    # Print layout information
    print(f"QR size: {qr_size}px")
    print(f"QR codes per page: {cols} columns × {rows} rows = {cols * rows} codes")
    print(f"Total pages needed: {math.ceil(len(qr_files) / (cols * rows))}")
    
    # Add QR codes to PDF
    page_num = 0
    for i in range(0, len(qr_files), cols * rows):
        if i > 0:
            c.showPage()  # Start a new page
            page_num += 1
        
        # Get QR codes for this page
        page_qr_files = qr_files[i:i + cols * rows]
        
        # Add QR codes to the page
        for j, qr_file in enumerate(page_qr_files):
            # Calculate position in the grid
            row = j // cols
            col = j % cols
            
            # Calculate x, y position with even spacing
            x = margin + h_spacing + col * (qr_size + h_spacing)
            y = height - (margin + v_spacing + (row + 1) * qr_size + row * v_spacing)
            
            # Add QR code image (no border, no text)
            c.drawImage(qr_file, x, y, width=qr_size, height=qr_size)
    
    # Save the PDF
    c.save()

if __name__ == "__main__":
    # Replace with your Excel file path and desired output PDF path
    excel_file = "Country delight QR.xlsx"
    output_pdf = "qr_codes50sm.pdf"
    
    # Generate compact QR codes (50px or smaller)
    generate_compact_qr_codes(excel_file, output_pdf, qr_size=50)
