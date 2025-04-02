import segno
from PIL import Image, ImageDraw, ImageFont
import os
import math
import colorsys

def generate_qr_codes(data, output_dir, qr_size, error_level='l'):
    """Generate QR codes for each data item"""
    qr_files = []
    
    for i, code in enumerate(data):
        clean_code = str(code).strip()
        
        # Try to create a Micro QR code first if possible
        try:
            qr = segno.make_micro(clean_code, error=None)
        except ValueError:
            # Fall back to standard QR with specified error correction
            qr = segno.make(clean_code, error=error_level)
        
        # Save the QR code image
        qr_file = os.path.join(output_dir, f"qr_{i}.png")
        
        # Calculate scale to achieve the desired size
        scale = max(1, int(qr_size / 25))
        
        # Save with specified border
        qr.save(qr_file, scale=scale, border=1)
        
        qr_files.append((qr_file, clean_code))
    
    return qr_files

def create_qr_pdf(qr_files, output_pdf, qr_size, page_margin, qr_margin, 
                  include_text=False, include_page_numbers=False):
    """Create PDF with QR codes based on user preferences"""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    
    # PDF page setup with A4 size
    c = canvas.Canvas(output_pdf, pagesize=A4)
    width, height = A4  # A4 is 595.2 x 841.8 points
    
    # Calculate effective area for QR codes
    effective_width = width - 2 * page_margin
    effective_height = height - 2 * page_margin
    
    # Calculate QR code size with spacing
    qr_with_spacing = qr_size + 2 * qr_margin
    
    # Calculate how many QR codes can fit per row and column
    cols = math.floor(effective_width / qr_with_spacing)
    rows = math.floor(effective_height / qr_with_spacing)
    
    # Calculate spacing to distribute QR codes evenly
    h_spacing = (effective_width - (cols * qr_size)) / (cols + 1)
    v_spacing = (effective_height - (rows * qr_size)) / (rows + 1)
    
    # Calculate total pages needed
    total_pages = math.ceil(len(qr_files) / (cols * rows))
    
    # Add QR codes to PDF
    for page in range(total_pages):
        if page > 0:
            c.showPage()  # Start a new page
        
        # Add page number if requested
        if include_page_numbers:
            c.setFont("Helvetica", 8)
            c.drawString(width - 50, 20, f"Page {page + 1}/{total_pages}")
        
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
            
            # Draw border rectangle if margin > 0
            if qr_margin > 0:
                c.rect(x - qr_margin, y - qr_margin, 
                       qr_size + 2 * qr_margin, qr_size + 2 * qr_margin)
            
            # Add QR code image
            c.drawImage(qr_file, x, y, width=qr_size, height=qr_size)
            
            # Add text label if requested
            if include_text:
                c.setFont("Helvetica", 6)
                # Truncate long codes for display
                display_text = code_text[:15] + "..." if len(code_text) > 15 else code_text
                text_width = c.stringWidth(display_text, "Helvetica", 6)
                c.drawString(x + (qr_size - text_width)/2, y - 10, display_text)
    
    # Save the PDF
    c.save()
    
    return {
        'qr_per_page': cols * rows,
        'total_pages': total_pages,
        'total_qr_codes': len(qr_files)
    }

def create_styled_qr(data, output_file, size, error_level='m', style='standard'):
    """Create a styled QR code with various visual options"""
    # Generate the QR code
    qr = segno.make(data, error=error_level)
    
    if style == 'standard':
        # Standard QR code
        scale = max(1, int(size / 25))
        qr.save(output_file, scale=scale, border=4)
    
    elif style == 'rounded':
        # Rounded QR code
        scale = max(1, int(size / 25))
        qr.save(output_file, scale=scale, border=4, 
                dark='black', light='white', 
                finder_dark='black', finder_light='white',
                data_dark='black', data_light='white',
                quiet_zone='white')
        
        # Open the image and apply rounded corners
        img = Image.open(output_file)
        
        # Create a new image with rounded corners
        rounded_img = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(rounded_img)
        
        # Get module size
        module_size = scale
        
        # Draw rounded rectangles for each black module
        for y in range(qr.symbol_size()[0]):
            for x in range(qr.symbol_size()[1]):
                if qr.get_module(x, y):
                    # Calculate position with border
                    pos_x = (x + 4) * module_size
                    pos_y = (y + 4) * module_size
                    
                    # Draw rounded rectangle
                    draw.rounded_rectangle(
                        [pos_x, pos_y, pos_x + module_size, pos_y + module_size],
                        radius=module_size/3,
                        fill="black"
                    )
        
        # Save the rounded QR code
        rounded_img.save(output_file)
    
    elif style == 'gradient':
        # Gradient QR code
        scale = max(1, int(size / 25))
        
        # Generate a temporary standard QR
        temp_file = output_file + ".temp.png"
        qr.save(temp_file, scale=scale, border=4)
        
        # Open the image
        img = Image.open(temp_file).convert("RGBA")
        width, height = img.size
        
        # Create gradient image
        gradient = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(gradient)
        
        # Create a gradient from blue to purple
        for y in range(height):
            # Calculate color based on position
            r = int(50 + (150 * y / height))
            g = 0
            b = int(200 - (50 * y / height))
            
            # Draw horizontal line with this color
            draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
        
        # Composite the QR code with the gradient
        result = Image.new("RGBA", img.size, (255, 255, 255, 255))
        
        # For each pixel, if the QR code is black, use the gradient color
        for x in range(width):
            for y in range(height):
                pixel = img.getpixel((x, y))
                if pixel[0] < 128:  # If it's a dark pixel in the QR code
                    result.putpixel((x, y), gradient.getpixel((x, y)))
        
        # Save the result
        result.save(output_file)
        
        # Clean up temporary file
        os.remove(temp_file)
    
    elif style == 'custom':
        # Custom colored QR code with logo placeholder
        scale = max(1, int(size / 25))
        qr.save(output_file, scale=scale, border=4, 
                dark='#1a73e8', light='#f8f9fa')
    
    return output_file
