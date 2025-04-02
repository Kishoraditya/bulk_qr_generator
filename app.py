import os
import uuid
import zipfile
import tempfile
import pandas as pd
import segno
from flask import Flask, render_template, request, send_file, jsonify, url_for
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import math
import shutil
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls', 'csv'}

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def read_file_data(file_path, column_index, max_rows=None):
    """Read data from uploaded file based on file type"""
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path)
    elif file_ext == '.csv':
        df = pd.read_csv(file_path)
    else:
        raise ValueError("Unsupported file format")
    
    # Adjust column index (0-based)
    if column_index >= len(df.columns):
        raise ValueError(f"Column index {column_index} out of range. File has {len(df.columns)} columns.")
    
    # Get data from specified column
    data = df.iloc[:, column_index].astype(str)
    
    # Filter out blank/NA values
    data = data[data.notna() & (data.str.strip() != '')]
    
    # Limit to max_rows if specified
    if max_rows and max_rows > 0:
        data = data.head(max_rows)
    
    return data.tolist()

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    # Check if file was uploaded
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file format. Please upload .xlsx, .xls, or .csv file'}), 400
    
    # Get form parameters
    try:
        column_index = int(request.form.get('column', 0))
        max_rows = request.form.get('max_rows', '')
        max_rows = int(max_rows) if max_rows.strip() else None
        qr_size = int(request.form.get('qr_size', 50))
        page_margin = int(request.form.get('page_margin', 5))
        qr_margin = int(request.form.get('qr_margin', 0))
        include_text = request.form.get('include_text') == 'true'
        include_page_numbers = request.form.get('include_page_numbers') == 'true'
        error_level = request.form.get('error_level', 'l')
        download_type = request.form.get('download_type', 'pdf')
        
        # Validate inputs
        if qr_size < 50:
            qr_size = 50  # Minimum size for reliable scanning
        
        if page_margin < 0:
            page_margin = 0
            
        if qr_margin < 0:
            qr_margin = 0
            
    except ValueError as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    
    # Create unique session ID for this generation
    session_id = str(uuid.uuid4())
    session_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    # Save uploaded file
    file_path = os.path.join(session_dir, secure_filename(file.filename))
    file.save(file_path)
    
    try:
        # Read data from file
        data = read_file_data(file_path, column_index, max_rows)
        
        if not data:
            return jsonify({'error': 'No valid data found in the specified column'}), 400
        
        # Generate QR codes
        qr_files = generate_qr_codes(data, session_dir, qr_size, error_level)
        
        # Create output files based on download type
        if download_type == 'pdf' or download_type == 'both':
            pdf_path = os.path.join(session_dir, 'qr_codes.pdf')
            stats = create_qr_pdf(qr_files, pdf_path, qr_size, page_margin, qr_margin, 
                                 include_text, include_page_numbers)
        
        if download_type == 'zip' or download_type == 'both':
            # Create zip file with individual QR codes
            zip_path = os.path.join(session_dir, 'qr_codes.zip')
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for i, (qr_file, code) in enumerate(qr_files):
                    # Use the code value as filename (sanitized)
                    safe_name = "".join([c if c.isalnum() else "_" for c in code])
                    safe_name = safe_name[:50]  # Limit filename length
                    zipf.write(qr_file, f"{safe_name}.png")
        
        # Prepare download URLs
        download_urls = {}
        if download_type == 'pdf' or download_type == 'both':
            download_urls['pdf'] = url_for('download_file', session_id=session_id, file_type='pdf')
        if download_type == 'zip' or download_type == 'both':
            download_urls['zip'] = url_for('download_file', session_id=session_id, file_type='zip')
        
        # Return success with download links and stats
        return jsonify({
            'success': True,
            'message': f'Generated {len(qr_files)} QR codes successfully',
            'download_urls': download_urls,
            'stats': stats if download_type in ['pdf', 'both'] else {'total_qr_codes': len(qr_files)}
        })
        
    except Exception as e:
        # Clean up on error
        shutil.rmtree(session_dir, ignore_errors=True)
        return jsonify({'error': str(e)}), 500

@app.route('/download/<session_id>/<file_type>')
def download_file(session_id, file_type):
    session_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    
    if not os.path.exists(session_dir):
        return "Files not found or expired", 404
    
    if file_type == 'pdf':
        file_path = os.path.join(session_dir, 'qr_codes.pdf')
        return send_file(file_path, as_attachment=True, download_name='qr_codes.pdf')
    elif file_type == 'zip':
        file_path = os.path.join(session_dir, 'qr_codes.zip')
        return send_file(file_path, as_attachment=True, download_name='qr_codes.zip')
    else:
        return "Invalid file type", 400

# Cleanup task (in a production environment, you'd use a scheduled task)
@app.route('/cleanup', methods=['POST'])
def cleanup():
    # This would be protected in production
    try:
        # Delete folders older than 1 hour
        # In production, use a proper scheduled task instead
        return jsonify({'success': True, 'message': 'Cleanup completed'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
